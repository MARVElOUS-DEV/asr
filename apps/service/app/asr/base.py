from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Protocol

from app.audio.chunks import AudioChunk, AudioFormat
from app.schemas.events import FinalTranscriptEvent, PartialTranscriptEvent


@dataclass(frozen=True)
class ASRSessionContext:
    session_id: str
    language: str
    audio_format: AudioFormat


TranscriptEvent = PartialTranscriptEvent | FinalTranscriptEvent


class ASRProvider(Protocol):
    async def stream(
        self,
        context: ASRSessionContext,
        audio: AsyncIterator[AudioChunk],
    ) -> AsyncIterator[TranscriptEvent]:
        """Consume audio chunks and yield transcript events."""
