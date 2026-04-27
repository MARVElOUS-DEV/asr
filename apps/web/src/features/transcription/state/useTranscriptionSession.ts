import { useCallback, useRef, useState } from "react";
import { MicrophoneStream } from "@/features/transcription/audio/microphone-stream";
import type { ServerEvent } from "@/features/transcription/realtime/protocol";
import { TranscriptionSocket } from "@/features/transcription/realtime/transcription-socket";

type SessionStatus = "idle" | "connecting" | "recording" | "stopped" | "error";

const DEFAULT_WS_URL = import.meta.env.VITE_ASR_WS_URL ?? "ws://localhost:8000/ws/transcribe";
const ASR_AUTH_TOKEN = import.meta.env.VITE_ASR_AUTH_TOKEN;

function getWebSocketUrl() {
  if (!ASR_AUTH_TOKEN) {
    return DEFAULT_WS_URL;
  }

  const url = new URL(DEFAULT_WS_URL, window.location.href);
  url.searchParams.set("access_token", ASR_AUTH_TOKEN);
  return url.toString();
}

export function useTranscriptionSession() {
  const [status, setStatus] = useState<SessionStatus>("idle");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [partialText, setPartialText] = useState("");
  const [finalText, setFinalText] = useState("");
  const [error, setError] = useState<string | null>(null);
  const socketRef = useRef<TranscriptionSocket | null>(null);
  const microphoneRef = useRef<MicrophoneStream | null>(null);

  const handleServerEvent = useCallback((event: ServerEvent) => {
    if (event.type === "ready") {
      setSessionId(event.session_id);
      setStatus("recording");
      return;
    }

    if (event.type === "partial") {
      setPartialText(event.text);
      return;
    }

    if (event.type === "final") {
      setFinalText((current) => (current.length > 0 ? `${current}\n${event.text}` : event.text));
      setPartialText("");
      return;
    }

    setError(event.message);
    setStatus("error");
  }, []);

  const stop = useCallback(async () => {
    socketRef.current?.sendEvent({ type: "stop" });
    socketRef.current?.close();
    socketRef.current = null;

    await microphoneRef.current?.stop();
    microphoneRef.current = null;

    setStatus("stopped");
  }, []);

  const start = useCallback(async () => {
    setError(null);
    setPartialText("");
    setStatus("connecting");

    const socket = new TranscriptionSocket({
      url: getWebSocketUrl(),
      onEvent: handleServerEvent,
      onOpen: () => {
        socket.sendEvent({
          type: "start",
          sample_rate: 16000,
          language: "auto",
        });
      },
      onClose: () => {
        setStatus((current) => (current === "recording" ? "stopped" : current));
      },
      onError: (message) => {
        setError(message);
        setStatus("error");
      },
    });

    const microphone = new MicrophoneStream({
      onChunk: (chunk) => socket.sendAudio(chunk),
      onError: (message) => {
        setError(message);
        setStatus("error");
      },
    });

    socketRef.current = socket;
    microphoneRef.current = microphone;
    socket.connect();
    await microphone.start();
  }, [handleServerEvent]);

  const clear = useCallback(() => {
    setFinalText("");
    setPartialText("");
    setError(null);
    setSessionId(null);
    setStatus("idle");
  }, []);

  return {
    status,
    sessionId,
    partialText,
    finalText,
    error,
    start,
    stop,
    clear,
  };
}
