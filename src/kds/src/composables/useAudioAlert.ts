import { ref, onUnmounted } from 'vue'

const audioContext = ref<AudioContext | null>(null)

export function useAudioAlert() {
  const isSupported = ref(true)
  let audioBuffer: AudioBuffer | null = null

  async function initAudio() {
    try {
      audioContext.value = new AudioContext()
      // Generate a simple beep sound
      audioBuffer = await generateBeepSound()
    } catch {
      console.warn('Web Audio API not supported')
      isSupported.value = false
    }
  }

  async function generateBeepSound(): Promise<AudioBuffer | null> {
    if (!audioContext.value) return null

    const ctx = audioContext.value
    const sampleRate = ctx.sampleRate
    const duration = 0.3
    const frequency = 880
    const numSamples = sampleRate * duration

    const buffer = ctx.createBuffer(1, numSamples, sampleRate)
    const data = buffer.getChannelData(0)

    for (let i = 0; i < numSamples; i++) {
      const t = i / sampleRate
      const envelope = Math.min(1, (numSamples - i) / (numSamples * 0.1))
      data[i] = Math.sin(2 * Math.PI * frequency * t) * envelope * 0.5
    }

    return buffer
  }

  async function playAlert() {
    if (!audioContext.value || !audioBuffer) {
      await initAudio()
    }

    if (audioContext.value && audioBuffer) {
      if (audioContext.value.state === 'suspended') {
        await audioContext.value.resume()
      }

      const source = audioContext.value.createBufferSource()
      source.buffer = audioBuffer
      source.connect(audioContext.value.destination)
      source.start()
    }
  }

  function cleanup() {
    if (audioContext.value) {
      audioContext.value.close()
      audioContext.value = null
    }
  }

  onUnmounted(cleanup)

  return {
    isSupported,
    initAudio,
    playAlert
  }
}
