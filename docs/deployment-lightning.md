# Lightning Deployment Notes

## Runtime Assumptions

- GPU-backed Lightning instance.
- Python 3.12 environment.
- Qwen3-ASR model downloaded or accessible from Hugging Face.
- HTTPS or a trusted reverse proxy for remote browser microphone permissions.

## Environment

```bash
ASR_PROVIDER=qwen3
ASR_MODEL_NAME=Qwen/Qwen3-ASR-0.6B
ASR_HOST=0.0.0.0
ASR_PORT=8000
WEB_ORIGIN=https://your-web-origin.example
```

## Service Startup

```bash
cd apps/service
uv sync --extra qwen
uv run uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000
```

## Notes

- Remote microphone access usually requires HTTPS.
- Start with `Qwen/Qwen3-ASR-0.6B` to reduce GPU pressure.
- Move to `Qwen/Qwen3-ASR-1.7B` after the protocol and UX are stable.

