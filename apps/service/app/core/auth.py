import secrets

from fastapi import WebSocket, status

AUTH_QUERY_PARAMS = ("access_token", "token")
AUTH_TOKEN_HEADER = "x-asr-auth-token"


def verify_auth_token(provided_token: str | None, expected_token: str | None) -> bool:
    if expected_token is None:
        return True

    if provided_token is None:
        return False

    return secrets.compare_digest(provided_token, expected_token)


async def verify_websocket_auth(
    websocket: WebSocket,
    expected_token: str | None,
) -> bool:
    if verify_auth_token(_get_websocket_token(websocket), expected_token):
        return True

    await websocket.close(
        code=status.WS_1008_POLICY_VIOLATION,
        reason="Unauthorized",
    )
    return False


def _get_websocket_token(websocket: WebSocket) -> str | None:
    bearer_token = _get_bearer_token(websocket.headers.get("authorization"))
    if bearer_token is not None:
        return bearer_token

    header_token = websocket.headers.get(AUTH_TOKEN_HEADER)
    if header_token:
        return header_token.strip()

    for param_name in AUTH_QUERY_PARAMS:
        query_token = websocket.query_params.get(param_name)
        if query_token:
            return query_token.strip()

    return None


def _get_bearer_token(authorization: str | None) -> str | None:
    if authorization is None:
        return None

    scheme, separator, credentials = authorization.partition(" ")
    if separator == "" or scheme.lower() != "bearer":
        return None

    token = credentials.strip()
    return token or None
