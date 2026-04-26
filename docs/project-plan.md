# Project Plan

## Goal

Build a maintainable MVP for live ASR:

1. The user speaks into the browser microphone.
2. The web client streams audio chunks to the Python service.
3. The service forwards audio into a local Qwen3-ASR runtime.
4. Partial and final transcript updates are streamed back to the browser.

## Architecture

```text
Browser
  React UI
  Microphone capture
  PCM encoding / resampling
  WebSocket client
    |
    v
FastAPI Service
  WebSocket endpoint
  Session manager
  Audio stream normalization
  ASR provider interface
    |
    v
Qwen3-ASR Runtime
  Local model
  vLLM streaming backend on GPU
```

## Layering

### Web

- `app`: application shell and composition.
- `features/transcription/ui`: screen-level components and controls.
- `features/transcription/audio`: microphone capture, worklet integration, and audio format handling.
- `features/transcription/realtime`: WebSocket protocol client.
- `features/transcription/state`: React state and session orchestration.
- `components/ui`: shadcn-style reusable primitives.
- `lib`: shared utilities.

### Service

- `api`: HTTP and WebSocket routes.
- `realtime`: websocket protocol parsing and connection lifecycle.
- `sessions`: per-client transcription session state.
- `audio`: audio chunk validation and future normalization.
- `asr`: provider abstraction plus Qwen3-ASR implementation.
- `schemas`: API events and payload models.
- `core`: config, logging, and application wiring.

## MVP Milestones

### 1. Scaffold

- Monorepo layout.
- React/Vite web client with Tailwind CSS and shadcn-style primitives.
- FastAPI service with health check and WebSocket endpoint.
- Mock ASR provider for UI and protocol validation.

### 2. Browser Audio Stream

- Request microphone permission.
- Capture microphone audio.
- Encode and stream 16 kHz mono PCM chunks.
- Show connection, recording, and transcript states.

### 3. Qwen3-ASR Integration

- Add lazy Qwen provider loading.
- Run Qwen3-ASR locally on GPU.
- Prefer vLLM streaming backend.
- Return partial and final transcript events through the same WebSocket protocol.

### 4. Long Recording Support

- Session lifecycle tracking.
- Transcript accumulation.
- Reconnect-aware client behavior.
- Memory and max-duration limits.
- Optional transcript persistence.

### 5. Lightning Deployment

- GPU server startup docs.
- Environment-based model/runtime config.
- Warmup path.
- Reverse proxy and HTTPS notes for remote browser microphone access.

## Initial Defaults

- Transport: WebSocket.
- Browser audio target: PCM 16-bit, mono, 16 kHz.
- ASR model: `Qwen/Qwen3-ASR-0.6B` for MVP.
- ASR provider: mock locally, Qwen3 on GPU.
- Python: 3.12.

