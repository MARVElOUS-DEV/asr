import type { ClientEvent, ServerEvent } from "./protocol";

type TranscriptionSocketOptions = {
  url: string;
  onEvent: (event: ServerEvent) => void;
  onOpen?: () => void;
  onClose?: () => void;
  onError?: (message: string) => void;
};

export class TranscriptionSocket {
  private socket: WebSocket | null = null;
  private readonly options: TranscriptionSocketOptions;

  constructor(options: TranscriptionSocketOptions) {
    this.options = options;
  }

  connect() {
    this.socket = new WebSocket(this.options.url);
    this.socket.binaryType = "arraybuffer";

    this.socket.onopen = () => {
      this.options.onOpen?.();
    };

    this.socket.onclose = () => {
      this.options.onClose?.();
    };

    this.socket.onerror = () => {
      this.options.onError?.("WebSocket connection failed");
    };

    this.socket.onmessage = (message) => {
      if (typeof message.data !== "string") {
        return;
      }

      try {
        this.options.onEvent(JSON.parse(message.data) as ServerEvent);
      } catch {
        this.options.onError?.("Received invalid server event");
      }
    };
  }

  sendEvent(event: ClientEvent) {
    this.send(JSON.stringify(event));
  }

  sendAudio(chunk: ArrayBuffer) {
    this.send(chunk);
  }

  close() {
    this.socket?.close();
    this.socket = null;
  }

  private send(payload: string | ArrayBuffer) {
    if (this.socket?.readyState !== WebSocket.OPEN) {
      return;
    }

    this.socket.send(payload);
  }
}
