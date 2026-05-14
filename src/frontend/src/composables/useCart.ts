// useCart - alias/re-export for convenience
import { useCartStore } from '@/stores/cart'

export function useCart() {
  return useCartStore()
}
