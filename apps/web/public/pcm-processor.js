class PcmProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this.targetSampleRate = 16000;
    this.pending = [];
    this.pendingLength = 0;
    this.frameSize = 1600;
  }

  process(inputs) {
    const input = inputs[0]?.[0];

    if (!input || input.length === 0) {
      return true;
    }

    const resampled = this.resample(input, sampleRate, this.targetSampleRate);
    this.pending.push(resampled);
    this.pendingLength += resampled.length;

    while (this.pendingLength >= this.frameSize) {
      const frame = this.takeFrame();
      const pcm = this.floatToPcm16(frame);
      this.port.postMessage(pcm.buffer, [pcm.buffer]);
    }

    return true;
  }

  resample(input, sourceRate, targetRate) {
    if (sourceRate === targetRate) {
      return new Float32Array(input);
    }

    const ratio = sourceRate / targetRate;
    const outputLength = Math.floor(input.length / ratio);
    const output = new Float32Array(outputLength);

    for (let i = 0; i < outputLength; i += 1) {
      const sourceIndex = i * ratio;
      const left = Math.floor(sourceIndex);
      const right = Math.min(left + 1, input.length - 1);
      const fraction = sourceIndex - left;
      output[i] = input[left] + (input[right] - input[left]) * fraction;
    }

    return output;
  }

  takeFrame() {
    const frame = new Float32Array(this.frameSize);
    let offset = 0;

    while (offset < this.frameSize && this.pending.length > 0) {
      const head = this.pending[0];
      const available = Math.min(head.length, this.frameSize - offset);
      frame.set(head.subarray(0, available), offset);
      offset += available;

      if (available === head.length) {
        this.pending.shift();
      } else {
        this.pending[0] = head.subarray(available);
      }
    }

    this.pendingLength -= this.frameSize;
    return frame;
  }

  floatToPcm16(input) {
    const output = new Int16Array(input.length);

    for (let i = 0; i < input.length; i += 1) {
      const sample = Math.max(-1, Math.min(1, input[i]));
      output[i] = sample < 0 ? sample * 0x8000 : sample * 0x7fff;
    }

    return output;
  }
}

registerProcessor("pcm-processor", PcmProcessor);
