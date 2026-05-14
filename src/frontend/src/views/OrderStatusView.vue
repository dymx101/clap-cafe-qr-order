<template>
  <div class="order-status-view">
    <header class="header">
      <button class="back-btn" @click="router.back()">←</button>
      <h1>{{ t('status.title') }}</h1>
    </header>

    <div class="content">
      <div v-if="orderStore.loading" class="loading">{{ t('common.loading') }}</div>
      <div v-else-if="order" class="status-card">
        <div class="order-header">
          <span class="order-id mono">{{ order.id }}</span>
          <OrderStatusBadge :status="order.status" :lang="lang" />
        </div>

        <div class="progress-steps">
          <div v-for="step in steps" :key="step.key" :class="['step', { active: isStepActive(step.key), done: isStepDone(step.key) }]">
            <div class="step-dot"></div>
            <span class="step-label">{{ t(`order.${step.key}`) }}</span>
          </div>
        </div>

        <div class="items">
          <div v-for="item in order.items" :key="item.id" class="item-row">
            <span class="qty">{{ item.quantity }}x</span>
            <span class="name">{{ lang === 'zh' ? item.item_name_zh : item.item_name_en }}</span>
            <span class="status-tag" :class="item.print_group">{{ item.print_group }}</span>
          </div>
        </div>

        <div class="info-grid">
          <div class="info-item">
            <span class="label">{{ t('order.seat') }}</span>
            <span class="value">{{ lang === 'zh' ? seatLabel : seatLabelEn }}</span>
          </div>
          <div class="info-item">
            <span class="label">{{ t('cart.total') }}</span>
            <span class="value amount">S$ {{ order.total_sgd.toFixed(2) }}</span>
          </div>
        </div>

        <div v-if="order.customer_notes" class="notes">
          <strong>{{ t('order.notes') }}:</strong> {{ order.customer_notes }}
        </div>
      </div>

      <button v-if="order && order.status === 'submitted'" class="cancel-btn" @click="showCancelModal = true">
        {{ t('order.cancel_order') }}
      </button>
    </div>

    <!-- Cancel modal -->
    <div v-if="showCancelModal" class="modal-overlay" @click.self="showCancelModal = false">
      <div class="modal">
        <h3>{{ t('order.cancel_order') }}</h3>
        <textarea v-model="cancelReason" :placeholder="t('order.cancel_reason')" class="reason-input" />
        <div class="modal-actions">
          <button class="secondary-btn" @click="showCancelModal = false">{{ t('common.cancel') }}</button>
          <button class="danger-btn" @click="confirmCancel">{{ t('common.confirm') }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useOrderStore } from '@/stores/order'
import { useSeatStore } from '@/stores/seat'
import { usePolling } from '@/composables/usePolling'
import OrderStatusBadge from '@/components/OrderStatusBadge.vue'
import { getOrderStatus } from '@/api/order'

const { t, locale } = useI18n()
const route = useRoute()
const router = useRouter()
const orderStore = useOrderStore()
const seatStore = useSeatStore()

const lang = computed(() => (locale.value === 'zh' ? 'zh' : 'en')) as unknown as 'zh' | 'en'
const order = computed(() => orderStore.currentOrder)
const showCancelModal = ref(false)
const cancelReason = ref('')

const seatLabel = computed(() => {
  const seat = seatStore.seats.find(s => s.id === order.value?.seat_id)
  return seat?.label_zh || order.value?.seat_id || '-'
})
const seatLabelEn = computed(() => {
  const seat = seatStore.seats.find(s => s.id === order.value?.seat_id)
  return seat?.label_en || order.value?.seat_id || '-'
})

const steps = [
  { key: 'submitted' },
  { key: 'confirmed' },
  { key: 'preparing' },
  { key: 'ready' },
  { key: 'completed' }
]

function isStepDone(step: string) {
  const orderStatus = order.value?.status
  if (!orderStatus) return false
  const statusOrder = ['submitted', 'confirmed', 'preparing', 'ready', 'completed']
  const currentIdx = statusOrder.indexOf(orderStatus)
  const stepIdx = statusOrder.indexOf(step)
  return currentIdx > stepIdx
}

function isStepActive(step: string) {
  return order.value?.status === step
}

onMounted(async () => {
  await seatStore.fetchSeats()
  await orderStore.fetchOrder(route.params.orderId as string)

  const orderId = route.params.orderId as string
  const { start, stop } = usePolling(
    () => getOrderStatus(orderId),
    (data: { status: string }) => {
      if (orderStore.currentOrder) {
        orderStore.currentOrder.status = data.status as typeof orderStore.currentOrder.status
      }
    },
    3000
  )
  start()
  onUnmounted(stop)
})

async function confirmCancel() {
  try {
    await orderStore.cancelOrder(route.params.orderId as string, cancelReason.value)
    showCancelModal.value = false
    router.push('/')
  } catch {}
}
</script>

<style scoped>
.order-status-view { min-height: 100vh; background: #F5F0E8; }
.header { background: #fff; padding: 12px 16px; display: flex; align-items: center; gap: 12px; position: sticky; top: 0; z-index: 10; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.back-btn { background: none; border: none; font-size: 24px; color: #3D2B1F; cursor: pointer; }
h1 { flex: 1; font-size: 18px; color: #3D2B1F; margin: 0; }
.content { padding: 16px; max-width: 600px; margin: 0 auto; }
.status-card { background: #fff; border-radius: 12px; padding: 20px; margin-bottom: 16px; }
.order-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.order-id.mono { font-family: monospace; font-size: 14px; font-weight: 600; color: #3D2B1F; }
.progress-steps { display: flex; justify-content: space-between; margin-bottom: 24px; position: relative; }
.progress-steps::before { content: ''; position: absolute; top: 8px; left: 20px; right: 20px; height: 2px; background: #eee; z-index: 0; }
.step { display: flex; flex-direction: column; align-items: center; gap: 6px; z-index: 1; }
.step-dot { width: 16px; height: 16px; border-radius: 50%; background: #ddd; border: 2px solid #fff; }
.step.done .step-dot { background: #27ae60; }
.step.active .step-dot { background: #D4A574; box-shadow: 0 0 0 4px rgba(212,165,116,0.3); }
.step-label { font-size: 10px; color: #888; text-align: center; }
.step.done .step-label, .step.active .step-label { color: #3D2B1F; font-weight: 600; }
.items { border-top: 1px solid #f0ebe3; padding-top: 16px; margin-bottom: 16px; }
.item-row { display: flex; align-items: baseline; gap: 8px; padding: 4px 0; }
.qty { font-weight: 600; color: #D4A574; min-width: 30px; }
.name { flex: 1; font-size: 14px; color: #3D2B1F; }
.status-tag { font-size: 10px; padding: 2px 6px; border-radius: 4px; background: #f0ebe3; color: #888; }
.info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.info-item { background: #f9f7f4; padding: 10px 12px; border-radius: 8px; }
.label { font-size: 11px; color: #888; display: block; margin-bottom: 2px; }
.value { font-size: 14px; font-weight: 600; color: #3D2B1F; }
.amount { color: #D4A574; font-size: 16px; }
.notes { background: #fff9e6; padding: 10px 12px; border-radius: 8px; font-size: 13px; color: #856404; margin-top: 12px; }
.cancel-btn { width: 100%; padding: 14px; background: #fff; color: #e74c3c; border: 1px solid #e74c3c; border-radius: 10px; font-size: 14px; cursor: pointer; }
.loading { text-align: center; padding: 40px; color: #888; }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 100; }
.modal { background: #fff; border-radius: 12px; padding: 24px; width: 90%; max-width: 400px; }
.modal h3 { margin: 0 0 16px; font-size: 16px; color: #3D2B1F; }
.reason-input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 8px; min-height: 80px; font-size: 14px; }
.modal-actions { display: flex; gap: 10px; margin-top: 16px; }
.secondary-btn { flex: 1; padding: 10px; background: #fff; border: 1px solid #ddd; border-radius: 8px; cursor: pointer; }
.danger-btn { flex: 1; padding: 10px; background: #e74c3c; color: #fff; border: none; border-radius: 8px; cursor: pointer; }
</style>
