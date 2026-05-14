import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Seat } from '@/types/seat'
import { getSeats } from '@/api/seat'

export const useSeatStore = defineStore('seat', () => {
  const seats = ref<Seat[]>([])
  const currentSeat = ref<Seat | null>(null)
  const loading = ref(false)

  async function fetchSeats() {
    loading.value = true
    try {
      const res = await getSeats()
      seats.value = res.seats
    } finally {
      loading.value = false
    }
  }

  function setCurrentSeat(seatId: string) {
    currentSeat.value = seats.value.find(s => s.id === seatId) || null
    if (!currentSeat.value && seatId) {
      currentSeat.value = {
        id: seatId,
        label_zh: seatId,
        label_en: seatId,
        zone: 'indoor',
        status: 'vacant',
        is_active: true
      }
    }
  }

  return { seats, currentSeat, loading, fetchSeats, setCurrentSeat }
})
