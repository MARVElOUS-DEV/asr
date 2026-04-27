# Backend Deployment Runbook

This runbook deploys the ASR backend on a Lightning GPU machine with the
Qwen3-ASR provider.

## 1. Prepare Secrets and Cache

Use a persistent cache path on the Lightning machine. Do not put model cache
under `/tmp`.

```bash
export HF_HOME=/persistent/cache/huggingface
export HF_HUB_CACHE=$HF_HOME/hub
export HF_TOKEN=hf_optional_read_token
```

`HF_TOKEN` is optional for public models, but recommended for reliable
Hugging Face access and future gated/private models.

## 2. Configure the Service

```bash
export ASR_PROVIDER=qwen3
export ASR_MODEL_NAME=Qwen/Qwen3-ASR-0.6B
export PRELOAD_ASR_PROVIDER=true

export ASR_AUTH_TOKEN=replace-with-a-long-random-token
export WEB_ORIGIN=https://your-web-origin.example

export ASR_QWEN_GPU_MEMORY_UTILIZATION=0.8
export ASR_QWEN_MAX_NEW_TOKENS=32
export ASR_QWEN_STREAM_CHUNK_SECONDS=2.0
export ASR_QWEN_UNFIXED_CHUNK_NUM=2
export ASR_QWEN_UNFIXED_TOKEN_NUM=5

export WEBSOCKET_START_TIMEOUT_SECONDS=15
export MAX_SESSION_SECONDS=14400
export MAX_AUDIO_CHUNK_BYTES=1048576
```

Keep `WEB_ORIGIN` specific in production. Do not use `*` unless the service is
strictly private and temporary.

## 3. Install Dependencies

```bash
cd apps/service
uv sync --extra qwen
```

## 4. Preflight Checks

```bash
uv run python -c "import qwen_asr; print('qwen_asr ok')"
uv run python -c "import torch; print(torch.cuda.is_available())"
```

The second command should print `True`.

## 5. Pre-download Model Weights

This avoids the first WebSocket request paying the model download cost.

```bash
uv run huggingface-cli download Qwen/Qwen3-ASR-0.6B
```

Use the same model name as `ASR_MODEL_NAME`.

## 6. Start the API

Run one worker unless you intentionally want multiple model copies in GPU
memory.

```bash
uv run uvicorn app.main:create_app \
  --factory \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 1
```

With `PRELOAD_ASR_PROVIDER=true`, startup loads Qwen and fails fast if the GPU,
runtime, Hugging Face access, or model cache is not ready.

## 7. Verify Health

From the Lightning machine:

```bash
curl http://127.0.0.1:8000/health
```

Expected shape:

```json
{
  "status": "ok",
  "asr_provider": "qwen3"
}
```

## 8. Connect the Web Client

Set the web app environment to the backend WebSocket URL and matching auth
token:

```bash
export VITE_ASR_WS_URL=wss://your-backend-domain.example/ws/transcribe
export VITE_ASR_AUTH_TOKEN=$ASR_AUTH_TOKEN
```

Use `wss://` for browser microphone flows over HTTPS.

## 9. Debug with Port Forwarding

For private testing, forward the backend port to your laptop:

```bash
ssh -L 8000:127.0.0.1:8000 <lightning-host>
```

Then run the web client with:

```bash
export VITE_ASR_WS_URL=ws://localhost:8000/ws/transcribe
export VITE_ASR_AUTH_TOKEN=$ASR_AUTH_TOKEN
```

For breakpoint debugging:

```bash
uv run --with debugpy python -m debugpy \
  --listen 0.0.0.0:5678 \
  --wait-for-client \
  -m uvicorn app.main:create_app \
  --factory \
  --host 0.0.0.0 \
  --port 8000
```

Forward the debug port:

```bash
ssh -L 5678:127.0.0.1:5678 <lightning-host>
```

Attach VS Code to `localhost:5678`.

## 10. Production Checklist

- `ASR_AUTH_TOKEN` is set to a long random value.
- `WEB_ORIGIN` is the real web origin, not `*`.
- Backend is served behind HTTPS or a trusted reverse proxy.
- `HF_HOME` and `HF_HUB_CACHE` point to persistent storage.
- `PRELOAD_ASR_PROVIDER=true` is enabled for fail-fast startup.
- Uvicorn is running with `--workers 1`.
- `/health` returns `asr_provider: qwen3`.
- A real browser microphone WebSocket test succeeds against the Lightning GPU.
