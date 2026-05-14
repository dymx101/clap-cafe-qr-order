import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface CartItem {
  item_id: string
  name_zh: string
  name_en: string
  price_sgd: number
  quantity: number
  options: {
    size?: string
    sweetness?: string
    temperature?: string
    extras?: string[]
  }
  notes?: string
}

export const useCartStore = defineStore('cart', () => {
  const items = ref<CartItem[]>([])
  const seatId = ref<string>('')

  const subtotal = computed(() =>
    items.value.reduce((sum, i) => sum + i.price_sgd * i.quantity, 0)
  )
  const tax = computed(() => Math.round(subtotal.value * 0.09 * 100) / 100)
  const total = computed(() => subtotal.value + tax.value)
  const itemCount = computed(() =>
    items.value.reduce((sum, i) => sum + i.quantity, 0)
  )

  function addItem(item: CartItem) {
    const key = JSON.stringify({ item_id: item.item_id, options: item.options })
    const existing = items.value.find(
      i => JSON.stringify({ item_id: i.item_id, options: i.options }) === key
    )
    if (existing) {
      existing.quantity += item.quantity
    } else {
      items.value.push({ ...item })
    }
  }

  function removeItem(index: number) {
    items.value.splice(index, 1)
  }

  function updateQuantity(index: number, qty: number) {
    if (qty <= 0) removeItem(index)
    else items.value[index].quantity = qty
  }

  function clear() {
    items.value = []
  }

  function setSeat(id: string) {
    seatId.value = id
  }

  return { items, seatId, subtotal, tax, total, itemCount, addItem, removeItem, updateQuantity, clear, setSeat }
})
