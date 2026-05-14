import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { MenuItem } from '@/types/menu'
import { getMenu } from '@/api/menu'

export const useMenuStore = defineStore('menu', () => {
  const categories = ref<{ id: string; name_zh: string; name_en: string; sort_order: number; items: MenuItem[] }[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const lang = ref<'zh' | 'en'>('zh')

  const allItems = computed(() => categories.value.flatMap(c => c.items))

  async function fetchMenu(language: 'zh' | 'en' = 'zh') {
    lang.value = language
    loading.value = true
    error.value = null
    try {
      const res = await getMenu(language)
      categories.value = res.categories
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : 'Failed to load menu'
    } finally {
      loading.value = false
    }
  }

  function getItemById(id: string): MenuItem | undefined {
    return allItems.value.find(i => i.id === id)
  }

  return { categories, loading, error, lang, allItems, fetchMenu, getItemById }
})
