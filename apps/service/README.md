# ASR Service

FastAPI service for live browser microphone transcription.

## Run Locally

```bash
uv sync
uv run uvicorn app.main:create_app --factory --reload --host 0.0.0.0 --port 8000
```

The default provider is `mock`, which validates the websocket protocol without loading a GPU model.

## Auth

Set `ASR_AUTH_TOKEN` to require authentication for transcription websocket
connections:

```bash
ASR_AUTH_TOKEN=replace-with-a-long-random-token \
  uv run uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000
```

Clients can authenticate with an `Authorization: Bearer <token>` header, an
`X-ASR-Auth-Token` header, or an `access_token` websocket query parameter. The
browser client uses `VITE_ASR_AUTH_TOKEN` to add the query parameter.

## Qwen3-ASR Runtime

On a GPU server:

```bash
uv sync --extra qwen
ASR_PROVIDER=qwen3 ASR_MODEL_NAME=Qwen/Qwen3-ASR-0.6B PRELOAD_ASR_PROVIDER=true \
  uv run uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000 --workers 1
```

The Qwen adapter is intentionally isolated in `app/asr/qwen3_asr.py`. It uses
the vLLM streaming backend and initializes lazily on the first Qwen request.
Model weights are not downloaded by this repo; the Qwen runtime resolves
`ASR_MODEL_NAME` on the GPU server.

Useful Qwen streaming settings:

```bash
ASR_QWEN_GPU_MEMORY_UTILIZATION=0.8
ASR_QWEN_MAX_NEW_TOKENS=32
ASR_QWEN_STREAM_CHUNK_SECONDS=2.0
ASR_QWEN_UNFIXED_CHUNK_NUM=2
ASR_QWEN_UNFIXED_TOKEN_NUM=5
ASR_QWEN_CONTEXT="optional domain vocabulary or hints"
```
