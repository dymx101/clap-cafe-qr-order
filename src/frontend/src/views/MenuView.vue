<template>
  <div class="menu-view">
    <header class="header">
      <div class="seat-badge" v-if="seatId">{{ seatStore.currentSeat ? (lang === 'zh' ? seatStore.currentSeat.label_zh : seatStore.currentSeat.label_en) : seatId }}</div>
      <h1>{{ t('menu.title') }}</h1>
      <LanguageSwitch />
    </header>

    <div v-if="menuStore.loading" class="loading">{{ t('common.loading') }}</div>
    <div v-else-if="menuStore.error" class="error">{{ menuStore.error }}</div>

    <div v-else class="categories">
      <div v-for="cat in menuStore.categories" :key="cat.id" class="category">
        <h2 class="category-title">{{ lang === 'zh' ? cat.name_zh : cat.name_en }}</h2>
        <div class="items-grid">
          <ItemCard
            v-for="item in cat.items"
            :key="item.id"
            :item="item"
            :lang="lang"
            @click="goToItem(item.id)"
          />
        </div>
      </div>
    </div>

    <CartBadge v-if="cartStore.itemCount > 0" class="cart-fab" :count="cartStore.itemCount" @click="goCart" />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { useMenuStore } from '@/stores/menu'
import { useCartStore } from '@/stores/cart'
import { useSeatStore } from '@/stores/seat'
import ItemCard from '@/components/ItemCard.vue'
import CartBadge from '@/components/CartBadge.vue'
import LanguageSwitch from '@/components/LanguageSwitch.vue'

const { t, locale } = useI18n()
const router = useRouter()
const menuStore = useMenuStore()
const cartStore = useCartStore()
const seatStore = useSeatStore()

const lang = computed(() => (locale.value === 'zh' ? 'zh' : 'en')) as unknown as 'zh' | 'en'

const seatId = computed(() => {
  const params = new URLSearchParams(window.location.search)
  return params.get('seat') || ''
})

onMounted(async () => {
  const params = new URLSearchParams(window.location.search)
  const langParam = params.get('lang') || 'zh'
  locale.value = langParam
  seatStore.fetchSeats().then(() => {
    if (seatId.value) seatStore.setCurrentSeat(seatId.value)
  })
  await menuStore.fetchMenu(langParam as 'zh' | 'en')
  if (seatId.value) cartStore.setSeat(seatId.value)
})

function goToItem(id: string) {
  router.push({ name: 'item-detail', params: { id } })
}

function goCart() {
  router.push({ name: 'cart' })
}
</script>

<style scoped>
.menu-view {
  min-height: 100vh;
  background: #F5F0E8;
  padding-bottom: 80px;
}
.header {
  background: #fff;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  position: sticky;
  top: 0;
  z-index: 10;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.seat-badge {
  background: #D4A574;
  color: #fff;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}
h1 {
  flex: 1;
  font-size: 20px;
  margin: 0;
  color: #3D2B1F;
}
.loading, .error {
  padding: 40px;
  text-align: center;
  color: #888;
}
.categories {
  padding: 16px;
}
.category {
  margin-bottom: 24px;
}
.category-title {
  font-size: 16px;
  color: #3D2B1F;
  margin: 0 0 12px 0;
  padding-bottom: 6px;
  border-bottom: 2px solid #D4A574;
}
.items-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}
.cart-fab {
  position: fixed;
  bottom: 24px;
  right: 24px;
}
</style>
