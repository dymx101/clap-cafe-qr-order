// src/api/orders.ts
import client from './client'

export interface OrderItemResponse {
  id: string
  item_id: string
  item_name_zh: string
  item_name_en: string
  quantity: number
  unit_price: number
  options: Record<string, any>
  notes: string | null
  print_group: string
}

export interface OrderResponse {
  id: string
  seat_id: string
  status: string
  payment_status: string
  payment_method: string | null
  payment_intent_id: string | null
  items: OrderItemResponse[]
  subtotal_sgd: number
  tax_sgd: number
  total_sgd: number
  notes: string | null
  customer_notes: string | null
  rejected_reason: string | null
  created_at: string
  updated_at: string
  paid_at: string | null
  completed_at: string | null
  cancelled_at: string | null
}

export interface OrderListResponse {
  orders: OrderResponse[]
  total_count: number
  page: number
  limit: number
}

export const ordersApi = {
  list(params?: {
    status?: string
    payment_status?: string
    page?: number
    limit?: number
  }) {
    return client.get<OrderListResponse>('/admin/orders', { params })
  },

  get(orderId: string) {
    return client.get<OrderResponse>(`/admin/orders/${orderId}`)
  },

  updateNotes(orderId: string, data: { customer_notes?: string; notes?: string }) {
    return client.put<OrderResponse>(`/admin/orders/${orderId}/notes`, data)
  },

  cancel(orderId: string) {
    return client.post<OrderResponse>(`/admin/orders/${orderId}/cancel`)
  }
}
