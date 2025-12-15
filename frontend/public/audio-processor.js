/**
 * AudioWorklet Processor for real-time audio capture
 * STORY-3.1: WebSocket Real-Time Analysis
 *
 * This processor runs in the AudioWorklet thread (separate from main thread)
 * and captures audio at low latency for real-time analysis.
 *
 * Usage:
 * 1. Register: await audioContext.audioWorklet.addModule('/audio-processor.js')
 * 2. Create: const node = new AudioWorkletNode(audioContext, 'audio-processor')
 * 3. Connect: micStream → node → audioContext.destination
 * 4. Listen: node.port.onmessage = (e) => sendToWebSocket(e.data.audioData)
 */

class AudioProcessor extends AudioWorkletProcessor {
  constructor() {
    super();

    // Buffer configuration
    this.chunkSize = 512; // Samples to send per message (matches WebSocket protocol)
    this.buffer = [];
    this.sampleRate = sampleRate; // Global from AudioWorkletGlobalScope

    // Performance tracking
    this.chunksProcessed = 0;
    this.startTime = currentTime;

    // Listen for control messages from main thread
    this.port.onmessage = (event) => {
      if (event.data.command === 'getStats') {
        this.sendStats();
      } else if (event.data.command === 'reset') {
        this.reset();
      } else if (event.data.command === 'setChunkSize') {
        this.chunkSize = event.data.chunkSize;
      }
    };

    console.log(`AudioProcessor initialized: ${this.sampleRate}Hz, chunk size: ${this.chunkSize}`);
  }

  /**
   * Process audio (called every 128 samples)
   * @param {Float32Array[][]} inputs - Input audio data
   * @param {Float32Array[][]} outputs - Output audio data (for pass-through)
   * @param {Object} parameters - Audio parameters
   * @returns {boolean} - true to keep processor alive
   */
  process(inputs, outputs, parameters) {
    const input = inputs[0];
    const output = outputs[0];

    // Pass-through audio (so user can hear themselves)
    if (input.length > 0 && output.length > 0) {
      for (let channel = 0; channel < Math.min(input.length, output.length); channel++) {
        output[channel].set(input[channel]);
      }
    }

    // Capture audio from first channel (mono)
    if (input.length > 0 && input[0].length > 0) {
      const channelData = input[0];

      // Add samples to buffer
      for (let i = 0; i < channelData.length; i++) {
        this.buffer.push(channelData[i]);
      }

      // When buffer is full, send chunk to main thread
      while (this.buffer.length >= this.chunkSize) {
        const chunk = this.buffer.splice(0, this.chunkSize);
        const audioData = new Float32Array(chunk);

        // Send to main thread for WebSocket transmission
        this.port.postMessage({
          type: 'audio',
          audioData: audioData,
          timestamp: currentTime,
          chunkNumber: this.chunksProcessed,
        });

        this.chunksProcessed++;
      }
    }

    // Return true to keep processor alive
    return true;
  }

  /**
   * Send processor statistics to main thread
   */
  sendStats() {
    const uptime = currentTime - this.startTime;
    this.port.postMessage({
      type: 'stats',
      data: {
        sampleRate: this.sampleRate,
        chunkSize: this.chunkSize,
        chunksProcessed: this.chunksProcessed,
        bufferSize: this.buffer.length,
        uptime: uptime,
      },
    });
  }

  /**
   * Reset processor state
   */
  reset() {
    this.buffer = [];
    this.chunksProcessed = 0;
    this.startTime = currentTime;
    console.log('AudioProcessor reset');
  }
}

// Register the processor
registerProcessor('audio-processor', AudioProcessor);
