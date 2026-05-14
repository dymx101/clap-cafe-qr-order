// Types for Menu
export interface ItemOptions {
  size?: 'S' | 'M' | 'L'
  sweetness?: string
  temperature?: string
  extras?: string[]
}

export interface MenuItem {
  id: string
  category_id: string
  name_zh: string
  name_en: string
  description_zh?: string
  description_en?: string
  price_sgd: number
  image_url?: string
  options_config: {
    sizes?: string[]
    sweetness?: string[]
    temperature?: string[]
    extras?: { name: string; price: number }[]
  }
  is_available: boolean
  stock?: number | null
  sort_order: number
}

export interface Category {
  id: string
  name_zh: string
  name_en: string
  sort_order: number
  items: MenuItem[]
}

export interface MenuResponse {
  categories: Category[]
}
