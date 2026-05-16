<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import type { KDSOrder } from '@/types/kds'
import { useOrderUtils } from '@/composables/useOrderUtils'

const props = defineProps<{
  order: KDSOrder
}>()

const emit = defineEmits<{
  accept: [orderId: string]
  start: [orderId: string]
  complete: [orderId: string]
  reject: [orderId: string, reason: string]
}>()

const { t } = useI18n()
const { formatTime, formatOptions } = useOrderUtils()

const WARNING_MINUTES = 5
const URGENT_MINUTES = 10

const waitMinutes = ref(0)
let waitTimer: ReturnType<typeof setInterval> | null = null

function updateWaitTime() {
  const now = Date.now()
  const orderTime = new Date(props.order.created_at).getTime()
  waitMinutes.value = Math.floor((now - orderTime) / 60000)
}

onMounted(() => {
  updateWaitTime()
  waitTimer = setInterval(updateWaitTime, 30000)
})

onUnmounted(() => {
  if (waitTimer) clearInterval(waitTimer)
})

const waitLevel = computed((): 'normal' | 'warning' | 'urgent' => {
  if (waitMinutes.value >= URGENT_MINUTES) return 'urgent'
  if (waitMinutes.value >= WARNING_MINUTES) return 'warning'
  return 'normal'
})

const statusClass = computed(() => props.order.status)

const seatDisplay = computed(() => {
  const id = props.order.seat_id
  return id.replace(/^[A-Z]+/, '')
})

const seatPrefix = computed(() => {
  const id = props.order.seat_id
  const prefix = id.match(/^[A-Z]+/)
  return prefix ? prefix[0] : ''
})
</script>

<template>
  <div :class="['order-card', statusClass, `wait-${waitLevel}`]">
    <div class="card-header">
      <div class="seat-info">
        <span class="seat-prefix">{{ seatPrefix }}</span>
        <span class="seat-number">{{ seatDisplay }}</span>
      </div>
      <div class="order-meta">
        <span class="order-id">#{{ order.id.split('-').pop() }}</span>
        <span class="wait-time">
          {{ formatTime(order.created_at) }}
          <span v-if="waitLevel === 'warning'" class="wait-badge warn">{{ waitMinutes }}m</span>
          <span v-if="waitLevel === 'urgent'" class="wait-badge urgent">{{ waitMinutes }}m</span>
        </span>
      </div>
    </div>

    <div class="items-list">
      <div
        v-for="item in order.items"
        :key="item.id"
        class="item"
      >
        <span class="item-qty">{{ item.quantity }}x</span>
        <span class="item-name">{{ item.item_name_zh }}</span>
        <span class="item-options">{{ formatOptions(item.options) }}</span>
        <span v-if="item.notes" class="item-notes">📝 {{ item.notes }}</span>
      </div>
    </div>

    <div v-if="order.customer_notes" class="customer-notes">
      ⚠️ {{ order.customer_notes }}
    </div>

    <div class="actions">
      <button
        v-if="order.status === 'submitted'"
        class="btn btn-accept"
        @click="emit('accept', order.id)"
      >
        {{ t('kds.action.accept') }}
      </button>

      <button
        v-if="order.status === 'confirmed'"
        class="btn btn-start"
        @click="emit('start', order.id)"
      >
        {{ t('kds.action.start') }}
      </button>

      <button
        v-if="order.status === 'preparing'"
        class="btn btn-complete"
        @click="emit('complete', order.id)"
      >
        {{ t('kds.action.complete') }}
      </button>

      <button
        class="btn btn-reject"
        @click="emit('reject', order.id, 'customer_request')"
      >
        {{ t('kds.action.reject') }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.order-card {
  background: #1e1e2e;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  border: 2px solid transparent;
  transition: border-color 0.2s, transform 0.2s, box-shadow 0.2s;
}

.order-card.submitted {
  border-color: #f59e0b;
}

.order-card.confirmed {
  border-color: #3b82f6;
}

.order-card.preparing {
  border-color: #8b5cf6;
}

.order-card.ready {
  border-color: #10b981;
}

.order-card.wait-warning {
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.4);
}

.order-card.wait-urgent {
  animation: pulse-urgent 1s ease-in-out infinite;
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.4);
}

@keyframes pulse-urgent {
  0%, 100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
  50% { box-shadow: 0 0 0 8px rgba(239, 68, 68, 0); }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.seat-info {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.seat-prefix {
  font-size: 24px;
  font-weight: 700;
  color: #fbbf24;
}

.seat-number {
  font-size: 48px;
  font-weight: 800;
  color: #fbbf24;
  line-height: 1;
}

.order-meta {
  text-align: right;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.order-id {
  font-size: 14px;
  color: #9ca3af;
  font-family: monospace;
}

.wait-time {
  font-size: 16px;
  color: #9ca3af;
  display: flex;
  align-items: center;
  gap: 4px;
}

.wait-badge {
  font-size: 11px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 4px;
}

.wait-badge.warn {
  background: #f59e0b;
  color: white;
}

.wait-badge.urgent {
  background: #ef4444;
  color: white;
}

.items-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px 0;
  border-top: 1px solid #374151;
  border-bottom: 1px solid #374151;
}

.item {
  display: grid;
  grid-template-columns: auto 1fr;
  grid-template-rows: auto auto;
  gap: 2px 8px;
  font-size: 18px;
}

.item-qty {
  font-weight: 700;
  color: #60a5fa;
  grid-row: span 2;
  display: flex;
  align-items: center;
}

.item-name {
  color: #f3f4f6;
  font-weight: 500;
}

.item-options {
  color: #9ca3af;
  font-size: 14px;
}

.item-notes {
  grid-column: 2;
  color: #fbbf24;
  font-size: 14px;
}

.customer-notes {
  background: rgba(251, 191, 36, 0.1);
  border: 1px solid rgba(251, 191, 36, 0.3);
  border-radius: 8px;
  padding: 8px 12px;
  color: #fbbf24;
  font-size: 14px;
}

.actions {
  display: flex;
  gap: 8px;
  margin-top: 4px;
}

.btn {
  flex: 1;
  min-height: 56px;
  border: none;
  border-radius: 8px;
  font-size: 18px;
  font-weight: 700;
  cursor: pointer;
  transition: transform 0.1s, opacity 0.2s;
  touch-action: manipulation;
}

.btn:active {
  transform: scale(0.95);
}

.btn-accept {
  background: #f59e0b;
  color: white;
}

.btn-start {
  background: #8b5cf6;
  color: white;
}

.btn-complete {
  background: #10b981;
  color: white;
}

.btn-reject {
  background: #374151;
  color: #9ca3af;
  flex: 0.5;
}
</style>
