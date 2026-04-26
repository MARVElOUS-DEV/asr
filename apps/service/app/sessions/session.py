import asyncio
from collections.abc import AsyncIterator

from app.asr.base import ASRProvider, ASRSessionContext, TranscriptEvent
from app.audio.chunks import AudioChunk, AudioFormat


class TranscriptionSession:
    def __init__(
        self,
        context: ASRSessionContext,
        provider: ASRProvider,
    ) -> None:
        self.context = context
        self.provider = provider
        self._queue: asyncio.Queue[AudioChunk | None] = asyncio.Queue(maxsize=256)
        self._closed = False

    async def push_audio(self, data: bytes) -> None:
        if self._closed:
            return

        chunk = AudioChunk(data=data, format=self.context.audio_format)
        await self._queue.put(chunk)

    async def close(self) -> None:
        if self._closed:
            return

        self._closed = True
        await self._queue.put(None)

    async def events(self) -> AsyncIterator[TranscriptEvent]:
        async for event in self.provider.stream(self.context, self._audio()):
            yield event

    async def _audio(self) -> AsyncIterator[AudioChunk]:
        while True:
            chunk = await self._queue.get()
            if chunk is None:
                return
            yield chunk


def create_session(
    session_id: str,
    language: str,
    sample_rate: int,
    provider: ASRProvider,
) -> TranscriptionSession:
    context = ASRSessionContext(
        session_id=session_id,
        language=language,
        audio_format=AudioFormat(sample_rate=sample_rate),
    )
    return TranscriptionSession(context=context, provider=provider)
