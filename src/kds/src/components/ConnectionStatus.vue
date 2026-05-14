<script setup lang="ts">
import { computed } from 'vue'
import type { SSEStatus } from '@/types/kds'

const props = defineProps<{
  status: SSEStatus
}>()

const statusConfig = computed(() => {
  const configs: Record<SSEStatus, { color: string; label: string }> = {
    connected: { color: '#10b981', label: '已连接' },
    reconnecting: { color: '#f59e0b', label: '重新连接中...' },
    error: { color: '#ef4444', label: '连接失败' },
    closed: { color: '#6b7280', label: '已断开' }
  }
  return configs[props.status]
})
</script>

<template>
  <div class="connection-status">
    <span class="dot" :style="{ background: statusConfig.color }"></span>
    <span class="label">{{ statusConfig.label }}</span>
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
