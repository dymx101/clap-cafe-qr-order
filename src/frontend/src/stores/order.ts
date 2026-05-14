import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Order } from '@/types/order'
import { createOrder as apiCreateOrder, getOrder, cancelOrder as apiCancelOrder } from '@/api/order'

export const useOrderStore = defineStore('order', () => {
  const currentOrder = ref<Order | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function submitOrder(seatId: string, items: { item_id: string; quantity: number; options: Record<string, unknown>; notes?: string }[], customerNotes?: string) {
    loading.value = true
    error.value = null
    try {
      const order = await apiCreateOrder({ seat_id: seatId, items, customer_notes: customerNotes })
      currentOrder.value = order
      return order
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : 'Failed to create order'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function fetchOrder(orderId: string) {
    loading.value = true
    error.value = null
    try {
      currentOrder.value = await getOrder(orderId)
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : 'Failed to load order'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function cancelOrder(orderId: string, reason: string) {
    try {
      await apiCancelOrder(orderId, reason)
      if (currentOrder.value?.id === orderId) {
        currentOrder.value.status = 'cancelled'
      }
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : 'Failed to cancel order'
      throw e
    }
  }

  function clearOrder() {
    currentOrder.value = null
  }

  return { currentOrder, loading, error, submitOrder, fetchOrder, cancelOrder, clearOrder }
})
