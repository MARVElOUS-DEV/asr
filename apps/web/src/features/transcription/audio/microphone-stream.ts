export type MicrophoneStreamOptions = {
  onChunk: (chunk: ArrayBuffer) => void;
  onError: (message: string) => void;
};

export class MicrophoneStream {
  private audioContext: AudioContext | null = null;
  private mediaStream: MediaStream | null = null;
  private source: MediaStreamAudioSourceNode | null = null;
  private processor: AudioWorkletNode | null = null;
  private readonly options: MicrophoneStreamOptions;

  constructor(options: MicrophoneStreamOptions) {
    this.options = options;
  }

  async start() {
    try {
      this.mediaStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });

      this.audioContext = new AudioContext();
      await this.audioContext.audioWorklet.addModule("/pcm-processor.js");

      this.source = this.audioContext.createMediaStreamSource(this.mediaStream);
      this.processor = new AudioWorkletNode(this.audioContext, "pcm-processor");
      this.processor.port.onmessage = (event: MessageEvent<ArrayBuffer>) => {
        this.options.onChunk(event.data);
      };

      this.source.connect(this.processor);
      this.processor.connect(this.audioContext.destination);
    } catch (error) {
      this.options.onError(error instanceof Error ? error.message : "Microphone startup failed");
      await this.stop();
    }
  }

  async stop() {
    this.processor?.disconnect();
    this.source?.disconnect();
    this.mediaStream?.getTracks().forEach((track) => track.stop());

    if (this.audioContext?.state !== "closed") {
      await this.audioContext?.close();
    }

    this.processor = null;
    this.source = null;
    this.mediaStream = null;
    this.audioContext = null;
  }
}
