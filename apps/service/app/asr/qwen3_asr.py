import asyncio
from collections.abc import AsyncIterator
from typing import Any

from app.asr.base import ASRProvider, ASRSessionContext, TranscriptEvent
from app.audio.chunks import AudioChunk
from app.schemas.events import FinalTranscriptEvent, PartialTranscriptEvent

LANGUAGE_ALIASES = {
    "auto": None,
    "": None,
    "en": "English",
    "zh": "Chinese",
    "yue": "Cantonese",
    "ar": "Arabic",
    "de": "German",
    "fr": "French",
    "es": "Spanish",
    "pt": "Portuguese",
    "id": "Indonesian",
    "it": "Italian",
    "ko": "Korean",
    "ru": "Russian",
    "th": "Thai",
    "vi": "Vietnamese",
    "ja": "Japanese",
    "tr": "Turkish",
    "hi": "Hindi",
    "ms": "Malay",
    "nl": "Dutch",
    "sv": "Swedish",
    "da": "Danish",
    "fi": "Finnish",
    "pl": "Polish",
    "cs": "Czech",
    "fil": "Filipino",
    "fa": "Persian",
    "el": "Greek",
    "hu": "Hungarian",
    "mk": "Macedonian",
    "ro": "Romanian",
}


class Qwen3ASRProvider(ASRProvider):
    def __init__(
        self,
        model_name: str,
        *,
        gpu_memory_utilization: float,
        max_new_tokens: int,
        max_inference_batch_size: int,
        stream_chunk_seconds: float,
        unfixed_chunk_num: int,
        unfixed_token_num: int,
        context: str,
    ) -> None:
        self.model_name = model_name
        self.gpu_memory_utilization = gpu_memory_utilization
        self.max_new_tokens = max_new_tokens
        self.max_inference_batch_size = max_inference_batch_size
        self.stream_chunk_seconds = stream_chunk_seconds
        self.unfixed_chunk_num = unfixed_chunk_num
        self.unfixed_token_num = unfixed_token_num
        self.context = context
        self._model: Any | None = None
        self._load_lock = asyncio.Lock()
        self._decode_lock = asyncio.Lock()

    async def warmup(self) -> None:
        await self._get_model()

    async def stream(
        self,
        context: ASRSessionContext,
        audio: AsyncIterator[AudioChunk],
    ) -> AsyncIterator[TranscriptEvent]:
        model = await self._get_model()
        state = await asyncio.to_thread(
            model.init_streaming_state,
            context=self.context,
            language=_normalize_language(context.language),
            unfixed_chunk_num=self.unfixed_chunk_num,
            unfixed_token_num=self.unfixed_token_num,
            chunk_size_sec=self.stream_chunk_seconds,
        )

        last_partial = ""
        async for chunk in audio:
            samples = _pcm_s16le_to_float32(chunk)

            async with self._decode_lock:
                await asyncio.to_thread(model.streaming_transcribe, samples, state)

            text = _state_text(state)
            if text and text != last_partial:
                last_partial = text
                yield PartialTranscriptEvent(
                    session_id=context.session_id,
                    text=text,
                )

        async with self._decode_lock:
            await asyncio.to_thread(model.finish_streaming_transcribe, state)

        final_text = _state_text(state)
        if final_text:
            yield FinalTranscriptEvent(session_id=context.session_id, text=final_text)

    async def _get_model(self) -> Any:
        if self._model is not None:
            return self._model

        async with self._load_lock:
            if self._model is None:
                self._model = await asyncio.to_thread(self._load_model)
            return self._model

    def _load_model(self) -> Any:
        try:
            from qwen_asr import Qwen3ASRModel
        except ImportError as exc:
            raise RuntimeError(
                "Qwen3-ASR runtime is not installed. "
                "Install it on the GPU server with `uv sync --extra qwen`."
            ) from exc

        return Qwen3ASRModel.LLM(
            model=self.model_name,
            gpu_memory_utilization=self.gpu_memory_utilization,
            max_inference_batch_size=self.max_inference_batch_size,
            max_new_tokens=self.max_new_tokens,
        )


def _normalize_language(language: str) -> str | None:
    normalized = language.strip()
    alias = LANGUAGE_ALIASES.get(normalized.lower())
    if alias is not None or normalized.lower() in LANGUAGE_ALIASES:
        return alias

    return normalized


def _pcm_s16le_to_float32(chunk: AudioChunk) -> Any:
    if chunk.format.encoding != "pcm_s16le":
        raise ValueError(f"Unsupported audio encoding: {chunk.format.encoding}")
    if chunk.format.channels != 1:
        raise ValueError(f"Unsupported channel count: {chunk.format.channels}")
    if chunk.format.sample_rate != 16000:
        raise ValueError(f"Unsupported sample rate: {chunk.format.sample_rate}")

    try:
        import numpy as np
    except ImportError as exc:
        raise RuntimeError(
            "Qwen3-ASR streaming requires numpy from the `qwen` extra. "
            "Install it on the GPU server with `uv sync --extra qwen`."
        ) from exc

    byte_length = len(chunk.data) - (len(chunk.data) % 2)
    if byte_length == 0:
        return np.zeros((0,), dtype=np.float32)

    pcm = np.frombuffer(chunk.data[:byte_length], dtype="<i2")
    return (pcm.astype(np.float32) / 32768.0).copy()


def _state_text(state: Any) -> str:
    return str(getattr(state, "text", "")).strip()
