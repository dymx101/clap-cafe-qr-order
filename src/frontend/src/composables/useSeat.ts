// useSeat - composable for seat management
import { useSeatStore } from '@/stores/seat'

export function useSeat() {
  const store = useSeatStore()
  return store
}
