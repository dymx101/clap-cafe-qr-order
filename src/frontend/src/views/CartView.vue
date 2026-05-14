<template>
  <div class="cart-view">
    <header class="header">
      <button class="back-btn" @click="router.back()">←</button>
      <h1>{{ t('cart.title') }}</h1>
      <button v-if="cartStore.itemCount > 0" class="clear-btn" @click="cartStore.clear()">{{ t('cart.clear') }}</button>
    </header>

    <div v-if="cartStore.itemCount === 0" class="empty">
      <p>{{ t('cart.empty') }}</p>
      <button class="shop-btn" @click="router.push('/')">{{ t('menu.title') }}</button>
    </div>

    <div v-else class="content">
      <div class="items">
        <div v-for="(item, idx) in cartStore.items" :key="idx" class="cart-item">
          <div class="item-info">
            <span class="item-name">{{ lang === 'zh' ? item.name_zh : item.name_en }}</span>
            <span class="item-options">{{ formatOptions(item.options) }}</span>
            <span class="item-price">S$ {{ (item.price_sgd * item.quantity).toFixed(2) }}</span>
          </div>
          <div class="qty-control">
            <button @click="cartStore.updateQuantity(idx, item.quantity - 1)">−</button>
            <span>{{ item.quantity }}</span>
            <button @click="cartStore.updateQuantity(idx, item.quantity + 1)">+</button>
          </div>
        </div>
      </div>

      <div class="totals">
        <div class="row">
          <span>{{ t('cart.subtotal') }}</span>
          <span>S$ {{ cartStore.subtotal.toFixed(2) }}</span>
        </div>
        <div class="row">
          <span>{{ t('cart.tax') }}</span>
          <span>S$ {{ cartStore.tax.toFixed(2) }}</span>
        </div>
        <div class="row total">
          <span>{{ t('cart.total') }}</span>
          <span>S$ {{ cartStore.total.toFixed(2) }}</span>
        </div>
      </div>

      <button class="checkout-btn" @click="router.push('/checkout')">
        {{ t('cart.checkout') }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useCartStore } from '@/stores/cart'

const { t, locale } = useI18n()
const router = useRouter()
const cartStore = useCartStore()
const lang = computed(() => (locale.value === 'zh' ? 'zh' : 'en')) as unknown as 'zh' | 'en'

function formatOptions(opts: { size?: string; sweetness?: string; temperature?: string; extras?: string[] }) {
  const parts: string[] = []
  if (opts.size) parts.push(opts.size)
  if (opts.sweetness) parts.push(opts.sweetness)
  if (opts.temperature) parts.push(opts.temperature)
  if (opts.extras?.length) parts.push(...opts.extras)
  return parts.join(' / ')
}
</script>

<style scoped>
.cart-view { min-height: 100vh; background: #F5F0E8; }
.header { background: #fff; padding: 12px 16px; display: flex; align-items: center; gap: 12px; position: sticky; top: 0; z-index: 10; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.back-btn { background: none; border: none; font-size: 24px; color: #3D2B1F; cursor: pointer; }
h1 { flex: 1; font-size: 18px; color: #3D2B1F; margin: 0; }
.clear-btn { background: none; border: none; color: #D4A574; font-size: 14px; cursor: pointer; }
.empty { padding: 60px 20px; text-align: center; color: #888; }
.shop-btn { margin-top: 16px; padding: 12px 24px; background: #D4A574; color: #fff; border: none; border-radius: 8px; cursor: pointer; }
.content { padding: 16px; max-width: 600px; margin: 0 auto; }
.items { background: #fff; border-radius: 12px; overflow: hidden; margin-bottom: 16px; }
.cart-item { padding: 14px 16px; border-bottom: 1px solid #f0ebe3; display: flex; justify-content: space-between; align-items: center; }
.cart-item:last-child { border-bottom: none; }
.item-info { display: flex; flex-direction: column; gap: 4px; }
.item-name { font-size: 15px; font-weight: 600; color: #3D2B1F; }
.item-options { font-size: 12px; color: #888; }
.item-price { font-size: 14px; color: #D4A574; font-weight: 600; }
.qty-control { display: flex; align-items: center; gap: 10px; }
.qty-control button { width: 28px; height: 28px; border-radius: 50%; border: 1px solid #D4A574; background: #fff; font-size: 16px; cursor: pointer; }
.qty-control span { font-size: 16px; font-weight: 600; min-width: 24px; text-align: center; }
.totals { background: #fff; border-radius: 12px; padding: 16px; margin-bottom: 16px; }
.row { display: flex; justify-content: space-between; padding: 6px 0; font-size: 14px; color: #666; }
.row.total { border-top: 1px solid #eee; margin-top: 8px; padding-top: 12px; font-size: 18px; font-weight: bold; color: #3D2B1F; }
.checkout-btn { width: 100%; padding: 16px; background: #D4A574; color: #fff; border: none; border-radius: 12px; font-size: 16px; font-weight: 600; cursor: pointer; }
</style>
