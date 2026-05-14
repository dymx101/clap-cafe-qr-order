// Types for Seat
export interface Seat {
  id: string
  label_zh: string
  label_en: string
  zone: 'indoor' | 'outdoor' | 'bar'
  status: 'vacant' | 'occupied' | 'reserved' | 'inactive'
  is_active: boolean
}

export interface SeatsResponse {
  seats: Seat[]
}
