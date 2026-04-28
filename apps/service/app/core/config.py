from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    asr_provider: str = Field(default="mock", alias="ASR_PROVIDER")
    asr_model_name: str = Field(
        default="Qwen/Qwen3-ASR-0.6B",
        alias="ASR_MODEL_NAME",
    )
    asr_sample_rate: int = Field(default=16000, alias="ASR_SAMPLE_RATE", gt=0)
    max_session_seconds: int = Field(
        default=4 * 60 * 60,
        alias="MAX_SESSION_SECONDS",
        gt=0,
    )
    websocket_start_timeout_seconds: int = Field(
        default=15,
        alias="WEBSOCKET_START_TIMEOUT_SECONDS",
        gt=0,
    )
    max_audio_chunk_bytes: int = Field(
        default=1_048_576,
        alias="MAX_AUDIO_CHUNK_BYTES",
        gt=0,
    )
    web_origin: str = Field(default="http://localhost:5173", alias="WEB_ORIGIN")
    asr_auth_token: SecretStr | None = Field(default=None, alias="ASR_AUTH_TOKEN")
    preload_asr_provider: bool = Field(default=False, alias="PRELOAD_ASR_PROVIDER")
    qwen_gpu_memory_utilization: float = Field(
        default=0.8,
        alias="ASR_QWEN_GPU_MEMORY_UTILIZATION",
        gt=0,
        le=1,
    )
    qwen_max_new_tokens: int = Field(
        default=32,
        alias="ASR_QWEN_MAX_NEW_TOKENS",
        gt=0,
    )
    qwen_max_inference_batch_size: int = Field(
        default=1,
        alias="ASR_QWEN_MAX_INFERENCE_BATCH_SIZE",
        gt=0,
    )
    qwen_stream_chunk_seconds: float = Field(
        default=2.0,
        alias="ASR_QWEN_STREAM_CHUNK_SECONDS",
        gt=0,
    )
    qwen_unfixed_chunk_num: int = Field(
        default=2,
        alias="ASR_QWEN_UNFIXED_CHUNK_NUM",
        ge=0,
    )
    qwen_unfixed_token_num: int = Field(
        default=5,
        alias="ASR_QWEN_UNFIXED_TOKEN_NUM",
        ge=0,
    )
    qwen_context: str = Field(default="", alias="ASR_QWEN_CONTEXT")

    @property
    def cors_origins(self) -> list[str]:
        if self.web_origin == "*":
            return ["*"]
        return [origin.strip() for origin in self.web_origin.split(",")]

    @property
    def auth_token(self) -> str | None:
        if self.asr_auth_token is None:
            return None

        token = self.asr_auth_token.get_secret_value().strip()
        return token or None


@lru_cache
def get_settings() -> Settings:
    return Settings()
