<template>
  <div :class="['item-card', { unavailable: !item.is_available }]" @click="$emit('click')">
    <div class="image-wrapper">
      <img v-if="item.image_url" :src="item.image_url" :alt="item.name_zh" />
      <div v-else class="placeholder-img">☕</div>
      <span v-if="!item.is_available" class="sold-out">{{ lang === 'zh' ? '售罄' : 'Sold Out' }}</span>
    </div>
    <div class="info">
      <span class="name">{{ lang === 'zh' ? item.name_zh : item.name_en }}</span>
      <span class="price">S$ {{ item.price_sgd.toFixed(2) }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { MenuItem } from '@/types/menu'

defineProps<{ item: MenuItem; lang: 'zh' | 'en' }>()
defineEmits<{ click: [] }>()
</script>

<style scoped>
.item-card { background: #fff; border-radius: 12px; overflow: hidden; cursor: pointer; transition: transform 0.15s, box-shadow 0.15s; }
.item-card:active { transform: scale(0.97); }
.item-card.unavailable { opacity: 0.6; }
.image-wrapper { position: relative; aspect-ratio: 1; background: #f0ebe3; }
.image-wrapper img { width: 100%; height: 100%; object-fit: cover; }
.placeholder-img { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; font-size: 48px; }
.sold-out { position: absolute; top: 8px; right: 8px; background: rgba(0,0,0,0.6); color: #fff; font-size: 11px; padding: 2px 8px; border-radius: 10px; }
.info { padding: 10px; }
.name { display: block; font-size: 13px; font-weight: 600; color: #3D2B1F; margin-bottom: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.price { font-size: 13px; font-weight: bold; color: #D4A574; }
</style>
