<template>
  <div class="checkout-view">
    <header class="header">
      <button class="back-btn" @click="router.back()">←</button>
      <h1>{{ t('order.your_order') }}</h1>
    </header>

    <div class="content">
      <!-- Seat info -->
      <div class="section seat-info">
        <span class="label">{{ t('order.seat') }}:</span>
        <span class="value">{{ seatLabel }}</span>
      </div>

      <!-- Order items -->
      <div class="section items-section">
        <div v-for="(item, idx) in cartStore.items" :key="idx" class="order-item">
          <span class="qty">{{ item.quantity }}x</span>
          <span class="name">{{ lang === 'zh' ? item.name_zh : item.name_en }}</span>
          <span class="opts">{{ formatOptions(item.options) }}</span>
          <span class="price">S$ {{ (item.price_sgd * item.quantity).toFixed(2) }}</span>
        </div>
      </div>

      <!-- Customer notes -->
      <div class="section">
        <label>{{ t('order.notes') }}</label>
        <textarea
          v-model="customerNotes"
          :placeholder="t('order.notes_placeholder')"
          class="notes-input"
        />
      </div>

      <!-- Totals -->
      <div class="section totals">
        <div class="row"><span>{{ t('cart.subtotal') }}</span><span>S$ {{ cartStore.subtotal.toFixed(2) }}</span></div>
        <div class="row"><span>{{ t('cart.tax') }}</span><span>S$ {{ cartStore.tax.toFixed(2) }}</span></div>
        <div class="row total"><span>{{ t('cart.total') }}</span><span>S$ {{ cartStore.total.toFixed(2) }}</span></div>
      </div>

      <div v-if="orderStore.error" class="error-msg">{{ orderStore.error }}</div>

      <button class="submit-btn" @click="submitOrder" :disabled="orderStore.loading">
        {{ orderStore.loading ? t('common.loading') : t('order.place_order') }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useCartStore } from '@/stores/cart'
import { useOrderStore } from '@/stores/order'
import { useSeatStore } from '@/stores/seat'

const { t, locale } = useI18n()
const router = useRouter()
const cartStore = useCartStore()
const orderStore = useOrderStore()
const seatStore = useSeatStore()
const lang = computed((): 'zh' | 'en' => locale.value as 'zh' | 'en')
const customerNotes = ref('')

const seatLabel = computed(() => {
  const seat = seatStore.currentSeat
  if (!seat) return cartStore.seatId || '-'
  return lang.value === 'zh' ? seat.label_zh : seat.label_en
})

function formatOptions(opts: { size?: string; sweetness?: string; temperature?: string; extras?: string[] }) {
  const parts: string[] = []
  if (opts.size) parts.push(opts.size)
  if (opts.sweetness) parts.push(opts.sweetness)
  if (opts.temperature) parts.push(opts.temperature)
  if (opts.extras?.length) parts.push(...opts.extras)
  return parts.join(' / ')
}

async function submitOrder() {
  if (cartStore.itemCount === 0) return
  try {
    const order = await orderStore.submitOrder(
      cartStore.seatId,
      cartStore.items.map(i => ({
        item_id: i.item_id,
        quantity: i.quantity,
        options: i.options,
        notes: i.notes
      })),
      customerNotes.value || undefined
    )
    cartStore.clear()
    router.push({ name: 'payment', params: { orderId: order.id } })
  } catch {
    // error shown via store
  }
}
</script>

<style scoped>
.checkout-view { min-height: 100vh; background: #F5F0E8; }
.header { background: #fff; padding: 12px 16px; display: flex; align-items: center; gap: 12px; position: sticky; top: 0; z-index: 10; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.back-btn { background: none; border: none; font-size: 24px; color: #3D2B1F; cursor: pointer; }
h1 { flex: 1; font-size: 18px; color: #3D2B1F; margin: 0; }
.content { padding: 16px; max-width: 600px; margin: 0 auto; }
.section { background: #fff; border-radius: 12px; padding: 16px; margin-bottom: 12px; }
.seat-info .label { color: #888; font-size: 14px; margin-right: 8px; }
.seat-info .value { font-weight: 600; color: #3D2B1F; }
.order-item { display: flex; align-items: baseline; gap: 8px; padding: 6px 0; border-bottom: 1px solid #f0ebe3; }
.order-item:last-child { border-bottom: none; }
.qty { font-weight: 600; color: #D4A574; min-width: 30px; }
.name { flex: 1; font-size: 14px; color: #3D2B1F; }
.opts { font-size: 12px; color: #888; }
.price { font-size: 14px; font-weight: 600; color: #3D2B1F; }
label { display: block; font-size: 14px; color: #3D2B1F; margin-bottom: 8px; font-weight: 600; }
.notes-input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; min-height: 60px; }
.totals .row { display: flex; justify-content: space-between; padding: 4px 0; font-size: 14px; color: #666; }
.totals .row.total { border-top: 1px solid #eee; margin-top: 8px; padding-top: 10px; font-size: 18px; font-weight: bold; color: #3D2B1F; }
.error-msg { color: #e74c3c; text-align: center; padding: 10px; font-size: 14px; }
.submit-btn { width: 100%; padding: 16px; background: #D4A574; color: #fff; border: none; border-radius: 12px; font-size: 16px; font-weight: 600; cursor: pointer; }
.submit-btn:disabled { background: #ccc; cursor: not-allowed; }
</style>
