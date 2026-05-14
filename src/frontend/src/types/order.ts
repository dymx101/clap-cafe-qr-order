// Types for Order
export type OrderStatus = 'submitted' | 'confirmed' | 'preparing' | 'ready' | 'completed' | 'cancelled' | 'rejected'
export type PaymentStatus = 'pending' | 'paid' | 'failed' | 'refunded' | 'cancelled'

export interface OrderItem {
  id: string
  order_id: string
  item_id: string
  item_name_zh: string
  item_name_en: string
  quantity: number
  unit_price: number
  options: Record<string, unknown>
  notes?: string
  print_group: string
}

export interface Order {
  id: string
  seat_id: string
  status: OrderStatus
  payment_status: PaymentStatus
  payment_method?: string
  payment_intent_id?: string
  subtotal_sgd: number
  tax_sgd: number
  total_sgd: number
  notes?: string
  customer_notes?: string
  rejected_reason?: string
  items: OrderItem[]
  created_at: string
  updated_at: string
  paid_at?: string
  completed_at?: string
  cancelled_at?: string
}

export interface CreateOrderRequest {
  seat_id: string
  items: {
    item_id: string
    quantity: number
    options: Record<string, unknown>
    notes?: string
  }[]
  customer_notes?: string
}
