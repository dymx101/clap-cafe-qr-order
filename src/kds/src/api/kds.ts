import client from './client'
import type { KDSOrder } from '@/types/kds'

interface OrdersResponse {
  orders: KDSOrder[]
}

interface StatusUpdateResponse {
  ok: boolean
}

export const kdsApi = {
  /** 获取所有活跃订单 */
  async getOrders(): Promise<OrdersResponse> {
    return client.get('/kds/orders')
  },

  /** 更新订单状态 */
  async updateStatus(orderId: string, status: string): Promise<StatusUpdateResponse> {
    return client.put(`/kds/orders/${orderId}/status`, { status })
  },

  /** SSE 流地址 */
  getStreamUrl(): string {
    const baseURL = import.meta.env.VITE_API_BASE_URL || ''
    const apiBase = baseURL || '/api'
    // Ensure proper URL format: if baseURL is empty, use relative /api path
    if (!baseURL) {
      return '/api/kds/orders/stream'
    }
    const normalizedBase = apiBase.replace(/\/+$/, '')
    return `${normalizedBase}/kds/orders/stream`
  }
}
