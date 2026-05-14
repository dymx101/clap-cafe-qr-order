<template>
  <div class="order-confirm-view">
    <header class="header">
      <button class="back-btn" @click="router.push('/')">←</button>
      <h1>{{ t('order.your_order') }}</h1>
    </header>

    <div class="content">
      <div v-if="orderStore.loading" class="loading">{{ t('common.loading') }}</div>
      <div v-else-if="order" class="confirm-card">
        <div class="status-badge" :class="order.status">
          {{ t(`order.${order.status}`) }}
        </div>
        <div class="order-info">
          <div class="row"><span>{{ t('order.order_number') }}</span><span class="mono">{{ order.id }}</span></div>
          <div class="row"><span>{{ t('order.seat') }}</span><span>{{ lang === 'zh' ? seatLabel : seatLabelEn }}</span></div>
        </div>

        <div class="items">
          <div v-for="item in order.items" :key="item.id" class="item-row">
            <span class="qty">{{ item.quantity }}x</span>
            <span class="name">{{ lang === 'zh' ? item.item_name_zh : item.item_name_en }}</span>
            <span class="price">S$ {{ (item.unit_price * item.quantity).toFixed(2) }}</span>
          </div>
        </div>

        <div class="totals">
          <div class="row"><span>{{ t('cart.subtotal') }}</span><span>S$ {{ order.subtotal_sgd.toFixed(2) }}</span></div>
          <div class="row"><span>{{ t('cart.tax') }}</span><span>S$ {{ order.tax_sgd.toFixed(2) }}</span></div>
          <div class="row total"><span>{{ t('cart.total') }}</span><span>S$ {{ order.total_sgd.toFixed(2) }}</span></div>
        </div>

        <div class="actions">
          <button class="primary-btn" @click="goToStatus">{{ t('status.title') }} →</button>
          <button class="secondary-btn" @click="router.push('/')">{{ t('menu.title') }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useOrderStore } from '@/stores/order'
import { useSeatStore } from '@/stores/seat'

const { t, locale } = useI18n()
const route = useRoute()
const router = useRouter()
const orderStore = useOrderStore()
const seatStore = useSeatStore()

const lang = computed(() => (locale.value === 'zh' ? 'zh' : 'en')) as unknown as 'zh' | 'en'
const order = computed(() => orderStore.currentOrder)

const seatLabel = computed(() => {
  const seat = seatStore.seats.find(s => s.id === order.value?.seat_id)
  return seat?.label_zh || order.value?.seat_id || '-'
})
const seatLabelEn = computed(() => {
  const seat = seatStore.seats.find(s => s.id === order.value?.seat_id)
  return seat?.label_en || order.value?.seat_id || '-'
})

onMounted(async () => {
  await seatStore.fetchSeats()
  await orderStore.fetchOrder(route.params.orderId as string)
})

function goToStatus() {
  router.push({ name: 'order-status', params: { orderId: route.params.orderId } })
}
</script>

<style scoped>
.order-confirm-view { min-height: 100vh; background: #F5F0E8; }
.header { background: #fff; padding: 12px 16px; display: flex; align-items: center; gap: 12px; position: sticky; top: 0; z-index: 10; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.back-btn { background: none; border: none; font-size: 24px; color: #3D2B1F; cursor: pointer; }
h1 { flex: 1; font-size: 18px; color: #3D2B1F; margin: 0; }
.content { padding: 16px; max-width: 600px; margin: 0 auto; }
.confirm-card { background: #fff; border-radius: 12px; overflow: hidden; }
.status-badge { text-align: center; padding: 16px; font-size: 18px; font-weight: 600; color: #fff; }
.status-badge.submitted { background: #f39c12; }
.status-badge.confirmed { background: #3498db; }
.status-badge.preparing { background: #9b59b6; }
.status-badge.ready { background: #27ae60; }
.status-badge.completed { background: #95a5a6; }
.status-badge.cancelled { background: #e74c3c; }
.order-info { padding: 16px; border-bottom: 1px solid #f0ebe3; }
.row { display: flex; justify-content: space-between; padding: 4px 0; font-size: 14px; color: #666; }
.mono { font-family: monospace; color: #3D2B1F; font-weight: 600; }
.items { padding: 16px; border-bottom: 1px solid #f0ebe3; }
.item-row { display: flex; align-items: baseline; gap: 8px; padding: 4px 0; }
.qty { font-weight: 600; color: #D4A574; min-width: 30px; }
.name { flex: 1; font-size: 14px; color: #3D2B1F; }
.price { font-size: 14px; font-weight: 600; }
.totals { padding: 16px; border-bottom: 1px solid #f0ebe3; }
.totals .row { display: flex; justify-content: space-between; padding: 4px 0; font-size: 14px; color: #666; }
.totals .row.total { border-top: 1px solid #eee; margin-top: 8px; padding-top: 10px; font-size: 18px; font-weight: bold; color: #3D2B1F; }
.actions { padding: 16px; display: flex; flex-direction: column; gap: 10px; }
.primary-btn { padding: 14px; background: #D4A574; color: #fff; border: none; border-radius: 10px; font-size: 16px; font-weight: 600; cursor: pointer; }
.secondary-btn { padding: 12px; background: #fff; color: #D4A574; border: 1px solid #D4A574; border-radius: 10px; font-size: 14px; cursor: pointer; }
.loading { text-align: center; padding: 40px; color: #888; }
</style>
