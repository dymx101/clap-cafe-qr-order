<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
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

const { formatTime, formatWaitTime, formatOptions } = useOrderUtils()

const waitInfo = ref({ minutes: 0, isWarning: false })
let waitTimer: ReturnType<typeof setInterval> | null = null

function updateWaitTime() {
  waitInfo.value = formatWaitTime(props.order.created_at)
}

onMounted(() => {
  updateWaitTime()
  waitTimer = setInterval(updateWaitTime, 30000) // Update every 30 seconds
})

onUnmounted(() => {
  if (waitTimer) clearInterval(waitTimer)
})

const statusClass = computed(() => props.order.status)

const seatDisplay = computed(() => {
  // Extract seat number from seat_id like "T01" -> "01"
  const id = props.order.seat_id
  return id.replace(/^[A-Z]+/, '')
})

const seatPrefix = computed(() => {
  const id = props.order.seat_id
  const prefix = id.match(/^[A-Z]+/)
  return prefix ? prefix[0] : ''
})

function handleAccept() {
  emit('accept', props.order.id)
}

function handleStart() {
  emit('start', props.order.id)
}

function handleComplete() {
  emit('complete', props.order.id)
}

function handleReject() {
  emit('reject', props.order.id, 'customer_request')
}
</script>

<template>
  <div :class="['order-card', statusClass, { warning: waitInfo.isWarning }]">
    <div class="card-header">
      <div class="seat-info">
        <span class="seat-prefix">{{ seatPrefix }}</span>
        <span class="seat-number">{{ seatDisplay }}</span>
      </div>
      <div class="order-meta">
        <span class="order-id">#{{ order.id.split('-').pop() }}</span>
        <span class="wait-time" :class="{ warning: waitInfo.isWarning }">
          {{ formatTime(order.created_at) }}
          <span v-if="waitInfo.isWarning" class="warning-badge">久</span>
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
        @click="handleAccept"
      >
        接单
      </button>

      <button
        v-if="order.status === 'confirmed'"
        class="btn btn-start"
        @click="handleStart"
      >
        开始制作
      </button>

      <button
        v-if="order.status === 'preparing'"
        class="btn btn-complete"
        @click="handleComplete"
      >
        完成
      </button>

      <button
        class="btn btn-reject"
        @click="handleReject"
      >
        拒单
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
  transition: border-color 0.2s, transform 0.2s;
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

.order-card.warning {
  animation: pulse-warning 1s ease-in-out infinite;
}

@keyframes pulse-warning {
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

.wait-time.warning {
  color: #ef4444;
}

.warning-badge {
  background: #ef4444;
  color: white;
  font-size: 10px;
  padding: 2px 4px;
  border-radius: 4px;
  font-weight: 700;
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
