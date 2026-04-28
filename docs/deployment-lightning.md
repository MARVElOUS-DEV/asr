# Lightning Deployment Notes

## Runtime Assumptions

- GPU-backed Lightning instance.
- Python 3.12 environment.
- Qwen3-ASR model accessible from Hugging Face or already cached on the server.
- HTTPS or a trusted reverse proxy for remote browser microphone permissions.

## Environment

```bash
ASR_PROVIDER=qwen3
ASR_MODEL_NAME=Qwen/Qwen3-ASR-0.6B
PRELOAD_ASR_PROVIDER=true
ASR_QWEN_GPU_MEMORY_UTILIZATION=0.8
ASR_QWEN_MAX_NEW_TOKENS=32
ASR_QWEN_MAX_INFERENCE_BATCH_SIZE=1
ASR_QWEN_STREAM_CHUNK_SECONDS=2.0
WEBSOCKET_START_TIMEOUT_SECONDS=15
MAX_AUDIO_CHUNK_BYTES=1048576
ASR_HOST=0.0.0.0
ASR_PORT=8000
WEB_ORIGIN=https://your-web-origin.example
ASR_AUTH_TOKEN=replace-with-a-long-random-token
HF_HOME=/path/to/persistent/cache/huggingface
HF_HUB_CACHE=/path/to/persistent/cache/huggingface/hub
HF_TOKEN=optional-huggingface-read-token
```

## Service Startup

```bash
cd apps/service
uv sync --extra qwen
uv run uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000 --workers 1
```

With `PRELOAD_ASR_PROVIDER=true`, startup initializes `Qwen3ASRModel.LLM(...)`
and fails fast if the Qwen runtime, GPU, Hugging Face access, or model cache is
not ready. Keep `--workers 1` unless you intentionally want multiple model
copies loaded into GPU memory.

## Preflight

Run these on the Lightning machine before exposing the service:

```bash
uv run python -c "import qwen_asr; print('qwen_asr ok')"
uv run python -c "import torch; print(torch.cuda.is_available())"
uv run huggingface-cli download Qwen/Qwen3-ASR-0.6B
```

Then start the service and check:

```bash
curl http://127.0.0.1:8000/health
```

## Remote Debugging

For fast iteration, keep the API private on the Lightning machine and forward
ports to your laptop:

```bash
ssh -L 8000:127.0.0.1:8000 <lightning-host>
```

Then point the web client at the local tunnel:

```bash
VITE_ASR_WS_URL=ws://localhost:8000/ws/transcribe
VITE_ASR_AUTH_TOKEN=$ASR_AUTH_TOKEN
```

For breakpoints, run Uvicorn under `debugpy` on the Lightning server and forward
the debug port:

```bash
uv run --with debugpy python -m debugpy --listen 0.0.0.0:5678 --wait-for-client \
  -m uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000
ssh -L 5678:127.0.0.1:5678 <lightning-host>
```

Attach VS Code to `localhost:5678`. If you use VS Code Remote SSH into the
Lightning host, you can forward ports from the Ports panel instead of writing
the SSH tunnel manually.

## Notes

- Remote microphone access usually requires HTTPS.
- Start with `Qwen/Qwen3-ASR-0.6B` to reduce GPU pressure.
- Move to `Qwen/Qwen3-ASR-1.7B` after the protocol and UX are stable.
