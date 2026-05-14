<script setup lang="ts">
import { onMounted, onUnmounted, ref, computed, watch } from 'vue'
import { useKDSStore } from '@/stores/kds'
import { useAudioAlert } from '@/composables/useAudioAlert'
import OrderList from '@/components/OrderList.vue'
import FilterTabs from '@/components/FilterTabs.vue'
import ConnectionStatus from '@/components/ConnectionStatus.vue'
import AudioToggle from '@/components/AudioToggle.vue'
import RejectModal from '@/components/RejectModal.vue'

const store = useKDSStore()
const { playAlert } = useAudioAlert()
const audioToggleRef = ref<InstanceType<typeof AudioToggle> | null>(null)

const showRejectModal = ref(false)
const rejectingOrderId = ref<string | undefined>(undefined)
const previousOrderCount = ref(0)

const statusCounts = computed(() => ({
  all: store.orders.length,
  submitted: store.ordersByStatus.submitted.length,
  confirmed: store.ordersByStatus.confirmed.length,
  preparing: store.ordersByStatus.preparing.length,
  ready: store.ordersByStatus.ready.length
}))

// Watch for new orders to play sound
watch(() => store.orders.length, (newCount, oldCount) => {
  if (newCount > oldCount && store.soundEnabled) {
    audioToggleRef.value?.playAlert()
  }
  previousOrderCount.value = newCount
})

onMounted(async () => {
  await store.fetchOrders()
  store.connectSSE()
})

onUnmounted(() => {
  store.disconnectSSE()
})

async function handleAccept(orderId: string) {
  await store.updateOrderStatus(orderId, 'confirmed')
}

async function handleStart(orderId: string) {
  await store.updateOrderStatus(orderId, 'preparing')
}

async function handleComplete(orderId: string) {
  await store.updateOrderStatus(orderId, 'ready')
}

function handleReject(orderId: string, _reason: string) {
  rejectingOrderId.value = orderId
  showRejectModal.value = true
}

async function handleRejectConfirm(reason: string) {
  if (rejectingOrderId.value) {
    await store.updateOrderStatus(rejectingOrderId.value, 'rejected')
    showRejectModal.value = false
    rejectingOrderId.value = undefined
  }
}
</script>

<template>
  <div class="kds-app">
    <header class="app-header">
      <div class="header-left">
        <h1 class="app-title">KDS 后厨端</h1>
        <ConnectionStatus :status="store.sseStatus" />
      </div>
      <div class="header-right">
        <div class="stats">
          <span class="stats-label">今日完成</span>
          <span class="stats-value">{{ store.todayCompletedCount }}</span>
        </div>
        <AudioToggle
          ref="audioToggleRef"
          :enabled="store.soundEnabled"
          @toggle="store.toggleSound"
        />
      </div>
    </header>

    <FilterTabs
      v-model="store.selectedFilter"
      :counts="statusCounts"
    />

    <main class="app-main">
      <OrderList
        :orders="store.filteredOrders"
        @accept="handleAccept"
        @start="handleStart"
        @complete="handleComplete"
        @reject="handleReject"
      />
    </main>

    <RejectModal
      :visible="showRejectModal"
      :order-id="rejectingOrderId"
      @close="showRejectModal = false"
      @confirm="handleRejectConfirm"
    />
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background: #0f0f1a;
  color: #f3f4f6;
  overflow-x: hidden;
  -webkit-tap-highlight-color: transparent;
}

#app {
  min-height: 100vh;
  min-height: 100dvh;
}

.kds-app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  min-height: 100dvh;
}

.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: #16213e;
  border-bottom: 1px solid #1e3a5f;
  gap: 16px;
  flex-wrap: wrap;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.app-title {
  font-size: 24px;
  font-weight: 800;
  color: #fbbf24;
}

.stats {
  display: flex;
  flex-direction: column;
  align-items: center;
  background: #1e1e2e;
  padding: 8px 16px;
  border-radius: 8px;
}

.stats-label {
  font-size: 12px;
  color: #9ca3af;
}

.stats-value {
  font-size: 28px;
  font-weight: 800;
  color: #10b981;
}

.app-main {
  flex: 1;
  overflow-y: auto;
}

/* Scrollbar styling */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #1e1e2e;
}

::-webkit-scrollbar-thumb {
  background: #374151;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #4b5563;
}

/* Touch optimization */
@media (pointer: coarse) {
  .btn {
    min-height: 56px;
  }
}
</style>
