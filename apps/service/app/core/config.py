from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    asr_provider: str = Field(default="mock", alias="ASR_PROVIDER")
    asr_model_name: str = Field(
        default="Qwen/Qwen3-ASR-0.6B",
        alias="ASR_MODEL_NAME",
    )
    asr_sample_rate: int = Field(default=16000, alias="ASR_SAMPLE_RATE")
    max_session_seconds: int = Field(default=4 * 60 * 60, alias="MAX_SESSION_SECONDS")
    web_origin: str = Field(default="http://localhost:5173", alias="WEB_ORIGIN")

    @property
    def cors_origins(self) -> list[str]:
        if self.web_origin == "*":
            return ["*"]
        return [origin.strip() for origin in self.web_origin.split(",")]


@lru_cache
def get_settings() -> Settings:
    return Settings()
