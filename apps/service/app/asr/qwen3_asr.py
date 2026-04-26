from collections.abc import AsyncIterator

from app.asr.base import ASRProvider, ASRSessionContext, TranscriptEvent
from app.audio.chunks import AudioChunk


class Qwen3ASRProvider(ASRProvider):
    def __init__(self, model_name: str) -> None:
        self.model_name = model_name

    async def stream(
        self,
        context: ASRSessionContext,
        audio: AsyncIterator[AudioChunk],
    ) -> AsyncIterator[TranscriptEvent]:
        raise RuntimeError(
            "Qwen3-ASR provider is scaffolded but not wired yet. "
            "Install qwen-asr[vllm] on the GPU server and adapt this module "
            "to the current qwen-asr streaming API."
        )
