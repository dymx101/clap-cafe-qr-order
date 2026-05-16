<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { SSEStatus } from '@/types/kds'

const props = defineProps<{
  status: SSEStatus
}>()

const { t } = useI18n()

const statusConfig = computed(() => {
  const configs: Record<SSEStatus, { color: string; labelKey: string }> = {
    connected: { color: '#10b981', labelKey: 'kds.connection.connected' },
    reconnecting: { color: '#f59e0b', labelKey: 'kds.connection.reconnecting' },
    error: { color: '#ef4444', labelKey: 'kds.connection.error' },
    closed: { color: '#6b7280', labelKey: 'kds.connection.closed' }
  }
  return configs[props.status]
})
</script>

<template>
  <div class="connection-status">
    <span class="dot" :style="{ background: statusConfig.color }"></span>
    <span class="label">{{ t(statusConfig.labelKey) }}</span>
  </div>
</template>

<style scoped>
.connection-status {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #1e1e2e;
  border-radius: 8px;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.label {
  font-size: 14px;
  color: #9ca3af;
}
</style>
