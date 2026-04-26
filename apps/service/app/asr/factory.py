from app.asr.base import ASRProvider
from app.asr.mock_provider import MockASRProvider
from app.asr.qwen3_asr import Qwen3ASRProvider
from app.core.config import Settings


def create_asr_provider(settings: Settings) -> ASRProvider:
    provider = settings.asr_provider.lower()

    if provider == "mock":
        return MockASRProvider()

    if provider == "qwen3":
        return Qwen3ASRProvider(model_name=settings.asr_model_name)

    raise ValueError(f"Unsupported ASR_PROVIDER: {settings.asr_provider}")
