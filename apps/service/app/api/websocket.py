import asyncio
import contextlib
import logging
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.asr.factory import create_asr_provider
from app.core.auth import verify_websocket_auth
from app.core.config import get_settings
from app.realtime.protocol import parse_control_event, parse_start_event
from app.schemas.events import ErrorEvent, ReadyEvent
from app.sessions.session import TranscriptionSession, create_session

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/ws/transcribe")
async def transcribe(websocket: WebSocket) -> None:
    settings = get_settings()
    if not await verify_websocket_auth(websocket, settings.auth_token):
        return

    await websocket.accept()
    event_task: asyncio.Task[None] | None = None

    try:
        first_message = await asyncio.wait_for(
            websocket.receive_text(),
            timeout=settings.websocket_start_timeout_seconds,
        )
        start = parse_start_event(first_message)

        if start.sample_rate != settings.asr_sample_rate:
            await _send_error(websocket, "Unsupported sample rate")
            return

        provider = create_asr_provider(settings)
        await _warmup_provider(provider)

        session_id = start.session_id or str(uuid4())
        session = create_session(
            session_id=session_id,
            language=start.language,
            sample_rate=start.sample_rate,
            provider=provider,
        )

        await websocket.send_json(ReadyEvent(session_id=session_id).model_dump())
        event_task = asyncio.create_task(_send_session_events(websocket, session))
        deadline = asyncio.get_running_loop().time() + settings.max_session_seconds

        try:
            while True:
                remaining_seconds = deadline - asyncio.get_running_loop().time()
                if remaining_seconds <= 0:
                    await _send_error(websocket, "Session timed out")
                    break

                receive_task = asyncio.create_task(websocket.receive())
                done, _ = await asyncio.wait(
                    {receive_task, event_task},
                    timeout=remaining_seconds,
                    return_when=asyncio.FIRST_COMPLETED,
                )

                if not done:
                    receive_task.cancel()
                    with contextlib.suppress(asyncio.CancelledError):
                        await receive_task
                    await _send_error(websocket, "Session timed out")
                    break

                if event_task in done:
                    if not receive_task.done():
                        receive_task.cancel()
                        with contextlib.suppress(asyncio.CancelledError):
                            await receive_task
                    await _handle_event_task_result(websocket, event_task)
                    break

                message = receive_task.result()

                if message["type"] == "websocket.disconnect":
                    break

                if "bytes" in message and message["bytes"] is not None:
                    if len(message["bytes"]) > settings.max_audio_chunk_bytes:
                        await _send_error(websocket, "Audio chunk is too large")
                        break
                    await session.push_audio(message["bytes"])
                    continue

                if "text" in message and message["text"] is not None:
                    control = parse_control_event(message["text"])
                    if control is not None:
                        break
        finally:
            await session.close()
            if event_task is not None:
                try:
                    await asyncio.wait_for(asyncio.shield(event_task), timeout=5)
                except TimeoutError:
                    pass
                except WebSocketDisconnect:
                    pass
                except Exception as exc:
                    logger.error(
                        "Transcription event task failed during cleanup",
                        exc_info=(type(exc), exc, exc.__traceback__),
                    )
                if not event_task.done():
                    event_task.cancel()
                    with contextlib.suppress(asyncio.CancelledError):
                        await event_task

    except WebSocketDisconnect:
        return
    except TimeoutError:
        await _send_error(websocket, "Start event timed out")
    except ValueError as exc:
        await _send_error(websocket, str(exc))
    except Exception:
        logger.exception("Unhandled websocket transcription error")
        await _send_error(websocket, "Internal transcription error")
    finally:
        with contextlib.suppress(RuntimeError, WebSocketDisconnect):
            await websocket.close()


async def _send_session_events(
    websocket: WebSocket,
    session: TranscriptionSession,
) -> None:
    async for event in session.events():
        await websocket.send_json(event.model_dump())


async def _warmup_provider(provider: Any) -> None:
    warmup = getattr(provider, "warmup", None)
    if warmup is not None:
        await warmup()


async def _handle_event_task_result(
    websocket: WebSocket,
    event_task: asyncio.Task[None],
) -> None:
    try:
        event_task.result()
    except WebSocketDisconnect:
        return
    except Exception as exc:
        logger.error(
            "Transcription event task failed",
            exc_info=(type(exc), exc, exc.__traceback__),
        )
        await _send_error(websocket, "Transcription provider failed")


async def _send_error(websocket: WebSocket, message: str) -> None:
    with contextlib.suppress(RuntimeError, WebSocketDisconnect):
        await websocket.send_json(ErrorEvent(message=message).model_dump())
