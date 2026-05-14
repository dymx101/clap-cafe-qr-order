<template>
  <div class="seat-selector">
    <div v-for="zone in zones" :key="zone.key" class="zone">
      <h3 class="zone-title">{{ zone.label }}</h3>
      <div class="seats-grid">
        <button
          v-for="seat in zone.seats"
          :key="seat.id"
          :class="['seat-btn', seat.status, { selected: modelValue === seat.id }]"
          :disabled="seat.status === 'inactive'"
          @click="$emit('update:modelValue', seat.id)"
        >
          {{ seat.id }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { Seat } from '@/types/seat'

const props = defineProps<{ seats: Seat[]; modelValue: string }>()
defineEmits<{ 'update:modelValue': [seatId: string] }>()

const locale = useI18n().locale
const zones = computed(() => {
  const lang = locale.value
  const zoneDefs = [
    { key: 'indoor', label_zh: '室内', label_en: 'Indoor' },
    { key: 'outdoor', label_zh: '户外', label_en: 'Outdoor' },
    { key: 'bar', label_zh: '吧台', label_en: 'Bar' }
  ]
  return zoneDefs.map(z => ({
    key: z.key,
    label: lang === 'zh' ? z.label_zh : z.label_en,
    seats: props.seats.filter(s => s.zone === z.key)
  }))
})
</script>

<style scoped>
.seat-selector { padding: 8px 0; }
.zone { margin-bottom: 16px; }
.zone-title { font-size: 13px; color: #888; margin: 0 0 8px 0; padding-left: 4px; }
.seats-grid { display: flex; flex-wrap: wrap; gap: 8px; }
.seat-btn { width: 44px; height: 44px; border-radius: 8px; border: 1px solid #ddd; background: #fff; font-size: 12px; font-weight: 600; cursor: pointer; transition: all 0.15s; }
.seat-btn.vacant { border-color: #27ae60; color: #27ae60; }
.seat-btn.occupied { background: #f0ebe3; color: #aaa; cursor: not-allowed; }
.seat-btn.reserved { background: #fff3cd; color: #856404; cursor: not-allowed; }
.seat-btn.inactive { background: #eee; color: #ccc; cursor: not-allowed; }
.seat-btn.selected { background: #D4A574; color: #fff; border-color: #D4A574; }
</style>
