<template>
  <div class="order-history-view">
    <header class="header">
      <button class="back-btn" @click="router.back()">←</button>
      <h1>{{ t('status.title') }}</h1>
    </header>

    <div class="content">
      <div v-if="!localOrder" class="empty">{{ t('status.no_orders') }}</div>
      <div v-else class="order-card">
        <div class="order-header">
          <span class="mono">{{ localOrder.id }}</span>
          <OrderStatusBadge :status="localOrder.status" :lang="lang" />
        </div>
        <div class="items">
          <div v-for="item in localOrder.items" :key="item.id" class="item-row">
            <span class="qty">{{ item.quantity }}x</span>
            <span class="name">{{ lang === 'zh' ? item.item_name_zh : item.item_name_en }}</span>
            <span class="price">S$ {{ (item.unit_price * item.quantity).toFixed(2) }}</span>
          </div>
        </div>
        <div class="total-row">
          <span>{{ t('cart.total') }}</span>
          <span>S$ {{ localOrder.total_sgd.toFixed(2) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useOrderStore } from '@/stores/order'
import OrderStatusBadge from '@/components/OrderStatusBadge.vue'

const { t, locale } = useI18n()
const route = useRoute()
const router = useRouter()
const orderStore = useOrderStore()
const localOrder = ref(orderStore.currentOrder)
const lang = computed(() => (locale.value === 'zh' ? 'zh' : 'en')) as unknown as 'zh' | 'en'

onMounted(async () => {
  if (!localOrder.value) {
    await orderStore.fetchOrder(route.params.orderId as string)
    localOrder.value = orderStore.currentOrder
  }
})
</script>

<style scoped>
.order-history-view { min-height: 100vh; background: #F5F0E8; }
.header { background: #fff; padding: 12px 16px; display: flex; align-items: center; gap: 12px; position: sticky; top: 0; z-index: 10; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.back-btn { background: none; border: none; font-size: 24px; color: #3D2B1F; cursor: pointer; }
h1 { flex: 1; font-size: 18px; color: #3D2B1F; margin: 0; }
.content { padding: 16px; max-width: 600px; margin: 0 auto; }
.empty { text-align: center; padding: 60px 20px; color: #888; }
.order-card { background: #fff; border-radius: 12px; padding: 16px; }
.order-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.mono { font-family: monospace; font-size: 14px; font-weight: 600; color: #3D2B1F; }
.items { border-top: 1px solid #f0ebe3; padding-top: 12px; }
.item-row { display: flex; align-items: baseline; gap: 8px; padding: 3px 0; }
.qty { font-weight: 600; color: #D4A574; min-width: 30px; }
.name { flex: 1; font-size: 14px; color: #3D2B1F; }
.price { font-size: 14px; font-weight: 600; }
.total-row { display: flex; justify-content: space-between; padding-top: 12px; border-top: 1px solid #eee; margin-top: 12px; font-size: 16px; font-weight: bold; color: #3D2B1F; }
</style>
