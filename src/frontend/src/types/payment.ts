// Types for Payment
export interface PaymentIntentResponse {
  client_secret: string
  payment_intent_id: string
  amount: number
  currency: string
}

export interface PayNowResponse {
  paynow_qr_url: string
  paynow_reference: string
  expires_at: string
}
