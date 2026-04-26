from collections.abc import AsyncIterator

from app.asr.base import ASRProvider, ASRSessionContext, TranscriptEvent
from app.audio.chunks import AudioChunk
from app.schemas.events import FinalTranscriptEvent, PartialTranscriptEvent


class MockASRProvider(ASRProvider):
    async def stream(
        self,
        context: ASRSessionContext,
        audio: AsyncIterator[AudioChunk],
    ) -> AsyncIterator[TranscriptEvent]:
        received_bytes = 0
        emitted = 0
        phrases = [
            "Starting live transcription.",
            "Audio chunks are reaching the service.",
            "The Qwen3 ASR adapter can replace this mock provider.",
        ]

        async for chunk in audio:
            received_bytes += chunk.byte_length
            if received_bytes < (emitted + 1) * 32000:
                continue

            text = phrases[min(emitted, len(phrases) - 1)]
            emitted += 1
            yield PartialTranscriptEvent(session_id=context.session_id, text=text)

            if emitted % 3 == 0:
                yield FinalTranscriptEvent(session_id=context.session_id, text=text)

        if emitted > 0:
            yield FinalTranscriptEvent(
                session_id=context.session_id,
                text="Streaming session stopped.",
            )
