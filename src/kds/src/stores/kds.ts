import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { KDSOrder, SSEStatus } from '@/types/kds'
import { kdsApi } from '@/api/kds'

export const useKDSStore = defineStore('kds', () => {
  // State
  const orders = ref<KDSOrder[]>([])
  const sseStatus = ref<SSEStatus>('closed')
  const soundEnabled = ref(true)
  const selectedFilter = ref<string>('all')
  let eventSource: EventSource | null = null

  // Getters
  const filteredOrders = computed(() => {
    if (selectedFilter.value === 'all') return orders.value
    return orders.value.filter(o => o.status === selectedFilter.value)
  })

  const ordersByStatus = computed(() => {
    return {
      submitted: orders.value.filter(o => o.status === 'submitted'),
      confirmed: orders.value.filter(o => o.status === 'confirmed'),
      preparing: orders.value.filter(o => o.status === 'preparing'),
      ready: orders.value.filter(o => o.status === 'ready')
    }
  })

  const todayCompletedCount = ref(0)

  // Actions
  async function fetchOrders() {
    try {
      const data = await kdsApi.getOrders()
      orders.value = data.orders
    } catch (err) {
      console.error('Failed to fetch orders:', err)
    }
  }

  async function updateOrderStatus(orderId: string, status: string) {
    try {
      await kdsApi.updateStatus(orderId, status)
      const order = orders.value.find(o => o.id === orderId)
      if (order) {
        order.status = status as KDSOrder['status']
        if (status === 'ready') {
          todayCompletedCount.value++
        }
      }
      return true
    } catch (err) {
      console.error('Failed to update status:', err)
      return false
    }
  }

  function handleStreamMessage(message: KDSOrder) {
    const existingIndex = orders.value.findIndex(o => o.id === message.id)
    if (existingIndex >= 0) {
      orders.value[existingIndex] = message
    } else {
      orders.value.unshift(message)
    }
  }

  function connectSSE() {
    if (eventSource) {
      eventSource.close()
    }

    sseStatus.value = 'reconnecting'
    const url = kdsApi.getStreamUrl()
    eventSource = new EventSource(url)

    eventSource.onopen = () => {
      sseStatus.value = 'connected'
    }

    eventSource.addEventListener('new_order', (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data)
        handleStreamMessage(data)
      } catch (err) {
        console.error('Failed to parse SSE message:', err)
      }
    })

    eventSource.addEventListener('ping', () => {
      // Heartbeat received
    })

    eventSource.onerror = () => {
      sseStatus.value = 'error'
      eventSource?.close()
      // Reconnect after 3 seconds
      setTimeout(connectSSE, 3000)
    }
  }

  function disconnectSSE() {
    eventSource?.close()
    eventSource = null
    sseStatus.value = 'closed'
  }

  function toggleSound() {
    soundEnabled.value = !soundEnabled.value
  }

  function setFilter(filter: string) {
    selectedFilter.value = filter
  }

  return {
    orders,
    sseStatus,
    soundEnabled,
    selectedFilter,
    filteredOrders,
    ordersByStatus,
    todayCompletedCount,
    fetchOrders,
    updateOrderStatus,
    handleStreamMessage,
    connectSSE,
    disconnectSSE,
    toggleSound,
    setFilter
  }
})
