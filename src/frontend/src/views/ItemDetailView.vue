<template>
  <div class="item-detail-view">
    <header class="header">
      <button class="back-btn" @click="router.back()">←</button>
      <h1>{{ lang === 'zh' ? item?.name_zh : item?.name_en }}</h1>
    </header>

    <div v-if="!item" class="loading">{{ t('common.loading') }}</div>

    <div v-else class="content">
      <img v-if="item.image_url" :src="item.image_url" :alt="item.name_zh" class="item-image" />

      <div class="info">
        <p class="description">{{ lang === 'zh' ? item.description_zh : item.description_en }}</p>
        <p class="price">S$ {{ item.price_sgd.toFixed(2) }}</p>
      </div>

      <!-- Options -->
      <div v-if="item.options_config.sizes?.length" class="option-group">
        <label>{{ t('menu.options.size') }}</label>
        <div class="option-btns">
          <button
            v-for="size in item.options_config.sizes"
            :key="size"
            :class="['opt-btn', { active: selectedOptions.size === size }]"
            @click="selectedOptions.size = size"
          >{{ size }}</button>
        </div>
      </div>

      <div v-if="item.options_config.sweetness?.length" class="option-group">
        <label>{{ t('menu.options.sweetness') }}</label>
        <div class="option-btns">
          <button
            v-for="sw in item.options_config.sweetness"
            :key="sw"
            :class="['opt-btn', { active: selectedOptions.sweetness === sw }]"
            @click="selectedOptions.sweetness = sw"
          >{{ sw }}</button>
        </div>
      </div>

      <div v-if="item.options_config.temperature?.length" class="option-group">
        <label>{{ t('menu.options.temperature') }}</label>
        <div class="option-btns">
          <button
            v-for="temp in item.options_config.temperature"
            :key="temp"
            :class="['opt-btn', { active: selectedOptions.temperature === temp }]"
            @click="selectedOptions.temperature = temp"
          >{{ temp }}</button>
        </div>
      </div>

      <div v-if="item.options_config.extras?.length" class="option-group">
        <label>{{ t('menu.options.extras') }}</label>
        <div class="option-btns">
          <button
            v-for="extra in item.options_config.extras"
            :key="extra.name"
            :class="['opt-btn', { active: selectedOptions.extras?.includes(extra.name) }]"
            @click="toggleExtra(extra.name)"
          >{{ extra.name }} (+S${{ extra.price.toFixed(2) }})</button>
        </div>
      </div>

      <div class="option-group">
        <label>{{ t('order.notes') }}</label>
        <textarea
          v-model="notes"
          :placeholder="t('order.notes_placeholder')"
          class="notes-input"
        />
      </div>

      <!-- Quantity -->
      <div class="quantity-row">
        <button @click="qty = Math.max(1, qty - 1)">−</button>
        <span>{{ qty }}</span>
        <button @click="qty++">+</button>
      </div>

      <button class="add-btn" @click="addToCart" :disabled="!item.is_available">
        {{ item.is_available ? t('menu.add_to_cart') : t('menu.sold_out') }}
        S$ {{ totalPrice.toFixed(2) }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useMenuStore } from '@/stores/menu'
import { useCartStore } from '@/stores/cart'
import type { MenuItem } from '@/types/menu'

const { t, locale } = useI18n()
const route = useRoute()
const router = useRouter()
const menuStore = useMenuStore()
const cartStore = useCartStore()

const lang = computed((): 'zh' | 'en' => locale.value as 'zh' | 'en')
const item = ref<MenuItem | null>(null)
const qty = ref(1)
const notes = ref('')
const selectedOptions = ref<{ size?: string; sweetness?: string; temperature?: string; extras?: string[] }>({})

onMounted(async () => {
  if (menuStore.allItems.length === 0) {
    await menuStore.fetchMenu(lang.value)
  }
  item.value = menuStore.getItemById(route.params.id as string) || null
  if (item.value?.options_config.sizes?.length) {
    selectedOptions.value.size = item.value.options_config.sizes[0]
  }
  if (item.value?.options_config.sweetness?.length) {
    selectedOptions.value.sweetness = item.value.options_config.sweetness[0]
  }
  if (item.value?.options_config.temperature?.length) {
    selectedOptions.value.temperature = item.value.options_config.temperature[0]
  }
})

function toggleExtra(name: string) {
  if (!selectedOptions.value.extras) selectedOptions.value.extras = []
  const idx = selectedOptions.value.extras.indexOf(name)
  if (idx >= 0) selectedOptions.value.extras.splice(idx, 1)
  else selectedOptions.value.extras.push(name)
}

const totalPrice = computed(() => {
  if (!item.value) return 0
  let price = item.value.price_sgd
  if (item.value.options_config.extras) {
    for (const extra of item.value.options_config.extras) {
      if (selectedOptions.value.extras?.includes(extra.name)) {
        price += extra.price
      }
    }
  }
  return price * qty.value
})

function addToCart() {
  if (!item.value) return
  cartStore.addItem({
    item_id: item.value.id,
    name_zh: item.value.name_zh,
    name_en: item.value.name_en,
    price_sgd: totalPrice.value / qty.value,
    quantity: qty.value,
    options: { ...selectedOptions.value },
    notes: notes.value || undefined
  })
  router.push({ name: 'cart' })
}
</script>

<style scoped>
.item-detail-view { min-height: 100vh; background: #F5F0E8; }
.header {
  background: #fff;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  position: sticky;
  top: 0;
  z-index: 10;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.back-btn { background: none; border: none; font-size: 24px; color: #3D2B1F; cursor: pointer; }
h1 { flex: 1; font-size: 18px; color: #3D2B1F; margin: 0; }
.content { padding: 16px; max-width: 600px; margin: 0 auto; }
.item-image { width: 100%; max-height: 300px; object-fit: cover; border-radius: 12px; }
.info { margin: 16px 0; }
.description { color: #666; font-size: 14px; }
.price { font-size: 22px; font-weight: bold; color: #D4A574; margin-top: 8px; }
.option-group { margin: 16px 0; }
.option-group label { display: block; font-size: 14px; color: #3D2B1F; margin-bottom: 8px; font-weight: 600; }
.option-btns { display: flex; flex-wrap: wrap; gap: 8px; }
.opt-btn {
  padding: 8px 16px;
  border: 1px solid #D4A574;
  border-radius: 20px;
  background: #fff;
  color: #3D2B1F;
  cursor: pointer;
  font-size: 14px;
}
.opt-btn.active { background: #D4A574; color: #fff; }
.notes-input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; min-height: 60px; }
.quantity-row { display: flex; align-items: center; gap: 16px; margin: 16px 0; justify-content: center; }
.quantity-row button { width: 40px; height: 40px; border-radius: 50%; border: 1px solid #D4A574; background: #fff; font-size: 20px; cursor: pointer; }
.quantity-row span { font-size: 20px; font-weight: 600; min-width: 40px; text-align: center; }
.add-btn {
  width: 100%;
  padding: 16px;
  background: #D4A574;
  color: #fff;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  margin-top: 16px;
}
.add-btn:disabled { background: #ccc; cursor: not-allowed; }
.loading { padding: 40px; text-align: center; color: #888; }
</style>
