from typing import Literal

from pydantic import BaseModel, Field


class StartTranscriptionEvent(BaseModel):
    type: Literal["start"]
    session_id: str | None = None
    sample_rate: int = Field(default=16000)
    language: str = Field(default="auto")


class StopTranscriptionEvent(BaseModel):
    type: Literal["stop"]


class ReadyEvent(BaseModel):
    type: Literal["ready"] = "ready"
    session_id: str


class PartialTranscriptEvent(BaseModel):
    type: Literal["partial"] = "partial"
    session_id: str
    text: str


class FinalTranscriptEvent(BaseModel):
    type: Literal["final"] = "final"
    session_id: str
    text: str


class ErrorEvent(BaseModel):
    type: Literal["error"] = "error"
    message: str


ServerEvent = ReadyEvent | PartialTranscriptEvent | FinalTranscriptEvent | ErrorEvent
