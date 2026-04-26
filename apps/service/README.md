# ASR Service

FastAPI service for live browser microphone transcription.

## Run Locally

```bash
uv sync
uv run uvicorn app.main:create_app --factory --reload --host 0.0.0.0 --port 8000
```

The default provider is `mock`, which validates the websocket protocol without loading a GPU model.

## Qwen3-ASR Runtime

On a GPU server:

```bash
uv sync --extra qwen
ASR_PROVIDER=qwen3 ASR_MODEL_NAME=Qwen/Qwen3-ASR-0.6B \
  uv run uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000
```

The Qwen adapter is intentionally isolated in `app/asr/qwen3_asr.py`.

