import client from './client'
import type { Order, CreateOrderRequest } from '@/types/order'

export function createOrder(data: CreateOrderRequest) {
  return client.post<Order>('/orders', data).then(res => res.data)
}

export function getOrder(orderId: string) {
  return client.get<Order>(`/orders/${orderId}`).then(res => res.data)
}

export function getOrderStatus(orderId: string) {
  return client.get<{ id: string; status: string; updated_at: string }>(`/orders/${orderId}/status`).then(res => res.data)
}

export function cancelOrder(orderId: string, reason: string) {
  return client.put(`/orders/${orderId}/cancel`, { reason }).then(res => res.data)
}
