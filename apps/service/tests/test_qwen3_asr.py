from collections.abc import AsyncIterator

import pytest

from app.asr.base import ASRSessionContext
from app.asr.factory import create_asr_provider
from app.asr.mock_provider import MockASRProvider
from app.asr.qwen3_asr import Qwen3ASRProvider, _normalize_language
from app.audio.chunks import AudioChunk, AudioFormat
from app.core.config import Settings


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


class FakeStreamingState:
    def __init__(self) -> None:
        self.text = ""


class FakeQwenModel:
    def __init__(self) -> None:
        self.stream_calls = 0
        self.finished = False

    def init_streaming_state(
        self,
        *,
        context: str,
        language: str | None,
        unfixed_chunk_num: int,
        unfixed_token_num: int,
        chunk_size_sec: float,
    ) -> FakeStreamingState:
        assert context == "domain words"
        assert language == "English"
        assert unfixed_chunk_num == 2
        assert unfixed_token_num == 5
        assert chunk_size_sec == 2.0
        return FakeStreamingState()

    def streaming_transcribe(
        self,
        pcm16k: object,
        state: FakeStreamingState,
    ) -> FakeStreamingState:
        self.stream_calls += 1
        state.text = "hello" if self.stream_calls == 1 else "hello world"
        return state

    def finish_streaming_transcribe(
        self,
        state: FakeStreamingState,
    ) -> FakeStreamingState:
        self.finished = True
        state.text = "hello world"
        return state


def test_normalize_language_allows_auto_and_iso_aliases() -> None:
    assert _normalize_language("auto") is None
    assert _normalize_language("en") == "English"
    assert _normalize_language("Chinese") == "Chinese"


def test_factory_caches_provider_instances() -> None:
    settings = Settings(ASR_PROVIDER="mock")

    first = create_asr_provider(settings)
    second = create_asr_provider(settings)

    assert isinstance(first, MockASRProvider)
    assert first is second


@pytest.mark.anyio
async def test_qwen_provider_streams_partial_and_final_events(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    model = FakeQwenModel()
    provider = Qwen3ASRProvider(
        model_name="Qwen/Qwen3-ASR-0.6B",
        gpu_memory_utilization=0.8,
        max_new_tokens=32,
        stream_chunk_seconds=2.0,
        unfixed_chunk_num=2,
        unfixed_token_num=5,
        context="domain words",
    )
    provider._model = model
    monkeypatch.setattr(
        "app.asr.qwen3_asr._pcm_s16le_to_float32",
        lambda chunk: object(),
    )

    events = [
        event
        async for event in provider.stream(
            ASRSessionContext(
                session_id="session-1",
                language="en",
                audio_format=AudioFormat(sample_rate=16000),
            ),
            _audio_chunks(),
        )
    ]

    assert [event.type for event in events] == ["partial", "partial", "final"]
    assert [event.text for event in events] == ["hello", "hello world", "hello world"]
    assert model.finished


async def _audio_chunks() -> AsyncIterator[AudioChunk]:
    yield AudioChunk(data=b"\x00\x00", format=AudioFormat(sample_rate=16000))
    yield AudioChunk(data=b"\x00\x00", format=AudioFormat(sample_rate=16000))
