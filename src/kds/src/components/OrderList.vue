<script setup lang="ts">
import { computed } from 'vue'
import type { KDSOrder } from '@/types/kds'
import OrderCard from './OrderCard.vue'
import { useOrderUtils } from '@/composables/useOrderUtils'

const props = defineProps<{
  orders: KDSOrder[]
  loading?: boolean
}>()

const emit = defineEmits<{
  (e: 'accept', orderId: string): void
  (e: 'start', orderId: string): void
  (e: 'complete', orderId: string): void
  (e: 'reject', orderId: string, reason: string): void
}>()

const { sortOrders } = useOrderUtils()

const sortedOrders = computed(() => sortOrders(props.orders))
</script>

<template>
  <div class="order-list">
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <span>加载中...</span>
    </div>

    <div v-else-if="orders.length === 0" class="empty">
      <div class="empty-icon">📋</div>
      <span>暂无订单</span>
    </div>

    <div v-else class="cards-grid">
      <OrderCard
        v-for="order in sortedOrders"
        :key="order.id"
        :order="order"
        @accept="emit('accept', $event)"
        @start="emit('start', $event)"
        @complete="emit('complete', $event)"
        @reject="(orderId, reason) => emit('reject', orderId, reason)"
      />
    </div>
  </div>
</template>

<style scoped>
.order-list {
  padding: 16px;
  min-height: 100%;
}

.loading,
.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  height: 60vh;
  color: #9ca3af;
  font-size: 18px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #374151;
  border-top-color: #60a5fa;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-icon {
  font-size: 64px;
  opacity: 0.5;
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
  align-items: start;
}

@media (min-width: 1024px) {
  .cards-grid {
    grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  }
}
</style>
