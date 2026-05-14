import client from './client'
import type { PaymentIntentResponse, PayNowResponse } from '@/types/payment'

export function createPaymentIntent(orderId: string, paymentMethodTypes: string[] = ['card', 'grabpay', 'paynow']) {
  return client.post<PaymentIntentResponse>('/payments/create-intent', {
    order_id: orderId,
    payment_method_types: paymentMethodTypes
  }).then(res => res.data)
}

export function getPaymentStatus(paymentIntentId: string) {
  return client.get<{ status: string }>(`/payments/${paymentIntentId}/status`).then(res => res.data)
}

export function confirmPaynow(orderId: string) {
  return client.post<PayNowResponse>(`/payments/confirm-paynow`, {
    order_id: orderId,
    payment_method_type: 'paynow'
  }).then(res => res.data)
}
