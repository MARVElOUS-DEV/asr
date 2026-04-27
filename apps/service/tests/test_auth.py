import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.core.auth import verify_auth_token
from app.core.config import get_settings
from app.main import create_app


@pytest.fixture(autouse=True)
def clear_settings_cache():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_verify_auth_token_allows_when_auth_is_disabled() -> None:
    assert verify_auth_token(None, None)


def test_verify_auth_token_rejects_missing_or_wrong_token() -> None:
    assert not verify_auth_token(None, "expected-token")
    assert not verify_auth_token("wrong-token", "expected-token")


def test_verify_auth_token_accepts_matching_token() -> None:
    assert verify_auth_token("expected-token", "expected-token")


def test_websocket_rejects_missing_auth_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ASR_AUTH_TOKEN", "expected-token")

    client = TestClient(create_app())

    with pytest.raises(WebSocketDisconnect) as disconnect:
        with client.websocket_connect("/ws/transcribe"):
            pass

    assert disconnect.value.code == 1008


def test_websocket_accepts_query_auth_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ASR_AUTH_TOKEN", "expected-token")

    client = TestClient(create_app())

    with client.websocket_connect(
        "/ws/transcribe?access_token=expected-token",
    ) as websocket:
        websocket.send_json(
            {
                "type": "start",
                "sample_rate": 16000,
                "language": "auto",
            },
        )

        assert websocket.receive_json()["type"] == "ready"


def test_websocket_accepts_authorization_header(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ASR_AUTH_TOKEN", "expected-token")

    client = TestClient(create_app())

    with client.websocket_connect(
        "/ws/transcribe",
        headers={"Authorization": "Bearer expected-token"},
    ) as websocket:
        websocket.send_json(
            {
                "type": "start",
                "sample_rate": 16000,
                "language": "auto",
            },
        )

        assert websocket.receive_json()["type"] == "ready"
