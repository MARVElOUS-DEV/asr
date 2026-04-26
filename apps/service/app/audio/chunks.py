from dataclasses import dataclass


@dataclass(frozen=True)
class AudioFormat:
    sample_rate: int
    channels: int = 1
    encoding: str = "pcm_s16le"


@dataclass(frozen=True)
class AudioChunk:
    data: bytes
    format: AudioFormat

    @property
    def byte_length(self) -> int:
        return len(self.data)
