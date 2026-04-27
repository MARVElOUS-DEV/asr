# ASR Streaming MVP

Real-time browser microphone transcription using a React web client and a Python ASR service backed by a local Qwen3-ASR model.

## Project Shape

```text
apps/
  web/      React + Vite + Tailwind CSS + shadcn-style components
  service/  FastAPI realtime ASR service
docs/       Architecture, API, and deployment notes
```

## MVP Target

- Browser microphone recording only.
- Live streaming transcription over WebSocket.
- Local Qwen3-ASR model behind the Python service.
- GPU-backed deployment target on Lightning.
- Layered code so web, realtime transport, audio processing, sessions, and ASR providers can evolve independently.

## First Run

Web client:

```bash
cd apps/web
pnpm install
pnpm dev
```

Python service:

```bash
cd apps/service
uv sync
uv run uvicorn app.main:create_app --factory --reload --host 0.0.0.0 --port 8000
```

The initial service uses a mock streaming ASR provider by default. Set `ASR_PROVIDER=qwen3` on a GPU machine after installing the optional Qwen runtime.

Set `ASR_AUTH_TOKEN` on the service to require websocket authentication. Browser
clients should set the same value as `VITE_ASR_AUTH_TOKEN`.
