import json

from pydantic import ValidationError

from app.schemas.events import StartTranscriptionEvent, StopTranscriptionEvent


def parse_start_event(payload: str) -> StartTranscriptionEvent:
    try:
        return StartTranscriptionEvent.model_validate_json(payload)
    except ValidationError as exc:
        raise ValueError("Expected a valid start event") from exc


def parse_control_event(payload: str) -> StopTranscriptionEvent | None:
    try:
        raw = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise ValueError("Expected a JSON control event") from exc

    if raw.get("type") == "stop":
        return StopTranscriptionEvent.model_validate(raw)

    return None
