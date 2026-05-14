import client from './client'
import type { SeatsResponse } from '@/types/seat'

export function getSeats() {
  return client.get<SeatsResponse>('/seats').then(res => res.data)
}

export function getSeat(seatId: string) {
  return client.get(`/seats/${seatId}`).then(res => res.data)
}

export function updateSeatStatus(seatId: string, status: string) {
  return client.put(`/seats/${seatId}/status`, { status }).then(res => res.data)
}
