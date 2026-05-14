// Types for KDS - Kitchen Display System

export type OrderStatus = 'submitted' | 'confirmed' | 'preparing' | 'ready' | 'completed' | 'cancelled' | 'rejected'
export type PaymentStatus = 'pending' | 'paid' | 'failed' | 'refunded' | 'cancelled'

export interface KDSOrderItem {
  id: string
  item_name_zh: string
  quantity: number
  options: Record<string, unknown>
  notes?: string
  print_group: string
}

export interface KDSOrder {
  id: string
  seat_id: string
  status: OrderStatus
  payment_status: PaymentStatus
  created_at: string
  items: KDSOrderItem[]
  customer_notes?: string
  rejected_reason?: string
}

export interface KDSStreamMessage {
  event: string
  data: string
}

export type SSEStatus = 'connected' | 'reconnecting' | 'error' | 'closed'
