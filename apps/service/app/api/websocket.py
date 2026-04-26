import asyncio
import contextlib
from uuid import uuid4

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.asr.factory import create_asr_provider
from app.core.config import get_settings
from app.realtime.protocol import parse_control_event, parse_start_event
from app.schemas.events import ErrorEvent, ReadyEvent
from app.sessions.session import TranscriptionSession, create_session

router = APIRouter()


@router.websocket("/ws/transcribe")
async def transcribe(websocket: WebSocket) -> None:
    await websocket.accept()
    settings = get_settings()

    try:
        first_message = await websocket.receive_text()
        start = parse_start_event(first_message)

        if start.sample_rate != settings.asr_sample_rate:
            await websocket.send_json(
                ErrorEvent(message="Unsupported sample rate").model_dump()
            )
            return

        provider = create_asr_provider(settings)
        session_id = start.session_id or str(uuid4())
        session = create_session(
            session_id=session_id,
            language=start.language,
            sample_rate=start.sample_rate,
            provider=provider,
        )

        await websocket.send_json(ReadyEvent(session_id=session_id).model_dump())
        event_task = asyncio.create_task(_send_session_events(websocket, session))

        try:
            while True:
                message = await websocket.receive()

                if message["type"] == "websocket.disconnect":
                    break

                if "bytes" in message and message["bytes"] is not None:
                    await session.push_audio(message["bytes"])
                    continue

                if "text" in message and message["text"] is not None:
                    control = parse_control_event(message["text"])
                    if control is not None:
                        break
        finally:
            await session.close()
            with contextlib.suppress(asyncio.TimeoutError):
                await asyncio.wait_for(event_task, timeout=5)
            if not event_task.done():
                event_task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await event_task

    except WebSocketDisconnect:
        return
    except Exception as exc:
        await websocket.send_json(ErrorEvent(message=str(exc)).model_dump())


async def _send_session_events(
    websocket: WebSocket,
    session: TranscriptionSession,
) -> None:
    async for event in session.events():
        await websocket.send_json(event.model_dump())
