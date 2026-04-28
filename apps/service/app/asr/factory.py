from functools import lru_cache

from app.asr.base import ASRProvider
from app.asr.mock_provider import MockASRProvider
from app.asr.qwen3_asr import Qwen3ASRProvider
from app.core.config import Settings


def create_asr_provider(settings: Settings) -> ASRProvider:
    return _create_asr_provider(
        provider=settings.asr_provider.lower(),
        model_name=settings.asr_model_name,
        qwen_gpu_memory_utilization=settings.qwen_gpu_memory_utilization,
        qwen_max_new_tokens=settings.qwen_max_new_tokens,
        qwen_max_inference_batch_size=settings.qwen_max_inference_batch_size,
        qwen_stream_chunk_seconds=settings.qwen_stream_chunk_seconds,
        qwen_unfixed_chunk_num=settings.qwen_unfixed_chunk_num,
        qwen_unfixed_token_num=settings.qwen_unfixed_token_num,
        qwen_context=settings.qwen_context,
    )


@lru_cache
def _create_asr_provider(
    *,
    provider: str,
    model_name: str,
    qwen_gpu_memory_utilization: float,
    qwen_max_new_tokens: int,
    qwen_max_inference_batch_size: int,
    qwen_stream_chunk_seconds: float,
    qwen_unfixed_chunk_num: int,
    qwen_unfixed_token_num: int,
    qwen_context: str,
) -> ASRProvider:
    if provider == "mock":
        return MockASRProvider()

    if provider == "qwen3":
        return Qwen3ASRProvider(
            model_name=model_name,
            gpu_memory_utilization=qwen_gpu_memory_utilization,
            max_new_tokens=qwen_max_new_tokens,
            max_inference_batch_size=qwen_max_inference_batch_size,
            stream_chunk_seconds=qwen_stream_chunk_seconds,
            unfixed_chunk_num=qwen_unfixed_chunk_num,
            unfixed_token_num=qwen_unfixed_token_num,
            context=qwen_context,
        )

    raise ValueError(f"Unsupported ASR_PROVIDER: {provider}")
