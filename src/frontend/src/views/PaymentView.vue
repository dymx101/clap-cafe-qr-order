<template>
  <div class="payment-view">
    <header class="header">
      <button class="back-btn" @click="router.back()">←</button>
      <h1>{{ t('payment.title') }}</h1>
    </header>

    <div class="content">
      <!-- Order summary -->
      <div v-if="order" class="order-summary">
        <div class="summary-row">
          <span>{{ t('order.order_number') }}</span>
          <span class="order-id">{{ order.id }}</span>
        </div>
        <div class="summary-row">
          <span>{{ t('cart.total') }}</span>
          <span class="amount">S$ {{ (order.total_sgd).toFixed(2) }}</span>
        </div>
      </div>

      <!-- Payment status -->
      <div v-if="paymentStatus === 'succeeded'" class="status-card success">
        <div class="status-icon">✓</div>
        <p>{{ t('payment.success') }}</p>
        <button class="action-btn" @click="goToStatus">{{ t('status.title') }} →</button>
      </div>

      <div v-else-if="paymentStatus === 'failed'" class="status-card error">
        <div class="status-icon">✗</div>
        <p>{{ t('payment.failed') }}</p>
        <button class="action-btn" @click="retry">{{ t('common.retry') }}</button>
      </div>

      <div v-else-if="paymentStatus === 'timeout'" class="status-card error">
        <div class="status-icon">⏰</div>
        <p>{{ t('payment.timeout') }}</p>
        <button class="action-btn" @click="router.push('/')">{{ t('menu.title') }}</button>
      </div>

      <!-- Stripe PaymentElement -->
      <div v-if="showStripeElement" class="stripe-element-wrapper">
        <div ref="paymentElementRef" class="stripe-element"></div>
      </div>

      <div v-if="loading" class="loading">{{ t('payment.waiting') }}</div>

      <!-- PayNow fallback -->
      <div v-if="showPaynow && paymentStatus === 'pending'" class="paynow-section">
        <p class="paynow-title">{{ t('payment.scan_qr') }}</p>
        <img v-if="paynowQrUrl" :src="paynowQrUrl" alt="PayNow QR" class="paynow-qr" />
        <p v-if="expiresAt" class="expires">{{ t('payment.expires_in') }}: {{ formatExpiry(expiresAt) }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useOrderStore } from '@/stores/order'
import { createPaymentIntent, getPaymentStatus, confirmPaynow } from '@/api/payment'
import { loadStripe, type Stripe, type StripeElements } from '@stripe/stripe-js'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const orderStore = useOrderStore()

const order = computed(() => orderStore.currentOrder)

const paymentStatus = ref<'pending' | 'succeeded' | 'failed' | 'timeout'>('pending')
const loading = ref(false)
const showStripeElement = ref(false)
const showPaynow = ref(false)
const paynowQrUrl = ref('')
const expiresAt = ref('')
const paymentElementRef = ref<HTMLElement | null>(null)

let stripe: Stripe | null = null
let elements: StripeElements | null = null
let pollTimer: ReturnType<typeof setInterval> | null = null

const orderId = computed(() => route.params.orderId as string)

onMounted(async () => {
  await orderStore.fetchOrder(orderId.value)
  if (!order.value) return
  await initPayment()
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
})

async function initPayment() {
  loading.value = true
  try {
    const res = await createPaymentIntent(orderId.value)
    // Check if Stripe.js is available
    const publishableKey = import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY
    if (publishableKey && publishableKey !== 'pk_test_placeholder') {
      stripe = await loadStripe(publishableKey)
      if (stripe && paymentElementRef.value) {
        elements = stripe.elements({
          clientSecret: res.client_secret,
          appearance: {
            theme: 'stripe',
            variables: {
              colorPrimary: '#D4A574',
              colorBackground: '#ffffff',
              fontFamily: 'system-ui, sans-serif',
              borderRadius: '8px'
            }
          }
        })
        const paymentEl = elements.create('payment')
        paymentEl.mount(paymentElementRef.value)
        showStripeElement.value = true

        // Wait for payment result
        const result = await stripe.confirmPayment({
          elements,
          confirmParams: {
            return_url: `${window.location.origin}/order/${orderId.value}/confirm`
          },
          redirect: 'if_required'
        })

        if (result.error) {
          paymentStatus.value = 'failed'
        } else if (result.paymentIntent?.status === 'succeeded') {
          paymentStatus.value = 'succeeded'
          startPolling()
        }
      } else {
        // No Stripe key, use PayNow fallback
        await showPaynowFallback()
      }
    } else {
      // No Stripe key, use PayNow fallback
      await showPaynowFallback()
    }
  } catch (e) {
    console.error('Payment init error:', e)
    paymentStatus.value = 'failed'
  } finally {
    loading.value = false
  }
}

async function showPaynowFallback() {
  showPaynow.value = true
  try {
    const res = await confirmPaynow(orderId.value)
    paynowQrUrl.value = res.paynow_qr_url
    expiresAt.value = res.expires_at
    startPolling()
  } catch {
    paymentStatus.value = 'failed'
  }
}

function startPolling() {
  pollTimer = setInterval(async () => {
    try {
      const res = await getPaymentStatus(order.value?.payment_intent_id || '')
      if (res.status === 'succeeded') {
        paymentStatus.value = 'succeeded'
        clearInterval(pollTimer!)
      } else if (res.status === 'failed') {
        paymentStatus.value = 'failed'
        clearInterval(pollTimer!)
      }
    } catch {}
  }, 3000)
}

function retry() {
  paymentStatus.value = 'pending'
  showStripeElement.value = false
  showPaynow.value = false
  initPayment()
}

function goToStatus() {
  router.push({ name: 'order-status', params: { orderId: orderId.value } })
}

function formatExpiry(iso: string) {
  const diff = new Date(iso).getTime() - Date.now()
  if (diff <= 0) return '0:00'
  const mins = Math.floor(diff / 60000)
  const secs = Math.floor((diff % 60000) / 1000)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}
</script>

<style scoped>
.payment-view { min-height: 100vh; background: #F5F0E8; }
.header { background: #fff; padding: 12px 16px; display: flex; align-items: center; gap: 12px; position: sticky; top: 0; z-index: 10; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.back-btn { background: none; border: none; font-size: 24px; color: #3D2B1F; cursor: pointer; }
h1 { flex: 1; font-size: 18px; color: #3D2B1F; margin: 0; }
.content { padding: 16px; max-width: 600px; margin: 0 auto; }
.order-summary { background: #fff; border-radius: 12px; padding: 16px; margin-bottom: 16px; }
.summary-row { display: flex; justify-content: space-between; padding: 6px 0; font-size: 14px; color: #666; }
.order-id { font-family: monospace; color: #3D2B1F; font-weight: 600; }
.amount { font-size: 20px; font-weight: bold; color: #D4A574; }
.status-card { border-radius: 12px; padding: 32px; text-align: center; margin-bottom: 16px; }
.status-card.success { background: #d4edda; color: #155724; }
.status-card.error { background: #f8d7da; color: #721c24; }
.status-icon { font-size: 48px; margin-bottom: 12px; }
.action-btn { padding: 12px 24px; border: none; border-radius: 8px; font-size: 16px; cursor: pointer; margin-top: 12px; background: rgba(0,0,0,0.1); }
.stripe-element-wrapper { background: #fff; border-radius: 12px; padding: 16px; margin-bottom: 16px; }
.stripe-element { min-height: 200px; }
.loading { text-align: center; padding: 20px; color: #888; }
.paynow-section { background: #fff; border-radius: 12px; padding: 24px; text-align: center; }
.paynow-title { font-size: 16px; color: #3D2B1F; margin-bottom: 16px; }
.paynow-qr { max-width: 200px; border: 1px solid #eee; }
.expires { font-size: 12px; color: #888; margin-top: 8px; }
</style>
