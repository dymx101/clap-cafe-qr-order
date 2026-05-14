<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAudioAlert } from '@/composables/useAudioAlert'

const props = defineProps<{
  enabled: boolean
}>()

const emit = defineEmits<{
  'toggle': []
}>()

const { initAudio, playAlert } = useAudioAlert()

onMounted(async () => {
  await initAudio()
})

// Expose playAlert for parent to call when new order arrives
defineExpose({ playAlert })

async function handleToggle() {
  if (!props.enabled) {
    // Turning on - play a test sound
    await playAlert()
  }
  emit('toggle')
}
</script>

<template>
  <button
    class="audio-toggle"
    :class="{ enabled: enabled }"
    @click="handleToggle"
    :title="enabled ? '点击静音' : '点击开启声音'"
  >
    <span class="icon">{{ enabled ? '🔔' : '🔕' }}</span>
    <span class="label">{{ enabled ? '声音开' : '声音关' }}</span>
  </button>
</template>

<style scoped>
.audio-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: #374151;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.audio-toggle:hover {
  background: #4b5563;
}

.audio-toggle.enabled {
  background: #1e3a5f;
}

.icon {
  font-size: 20px;
}

.label {
  font-size: 14px;
  color: #f3f4f6;
  font-weight: 500;
}
</style>
