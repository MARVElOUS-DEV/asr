# API Contract

## Health

```http
GET /health
```

Response:

```json
{
  "status": "ok",
  "asr_provider": "mock"
}
```

## Streaming Transcription

```http
WS /ws/transcribe
```

When `ASR_AUTH_TOKEN` is set on the service, websocket clients must provide the
same token in one of these forms:

```http
Authorization: Bearer <token>
X-ASR-Auth-Token: <token>
```

Browser clients can authenticate with the websocket URL:

```http
WS /ws/transcribe?access_token=<token>
```

### Client Events

Start a session:

```json
{
  "type": "start",
  "session_id": "optional-client-session-id",
  "sample_rate": 16000,
  "language": "auto"
}
```

Send audio:

```text
binary PCM chunks
```

Stop a session:

```json
{
  "type": "stop"
}
```

### Server Events

Session accepted:

```json
{
  "type": "ready",
  "session_id": "server-session-id"
}
```

Partial transcript:

```json
{
  "type": "partial",
  "session_id": "server-session-id",
  "text": "today we are discussing"
}
```

Final transcript:

```json
{
  "type": "final",
  "session_id": "server-session-id",
  "text": "Today we are discussing the ASR project plan."
}
```

Error:

```json
{
  "type": "error",
  "message": "Unsupported sample rate"
}
```
