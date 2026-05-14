<template>
  <span :class="['status-badge', status]">{{ label }}</span>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { OrderStatus } from '@/types/order'

const props = defineProps<{ status: OrderStatus | string; lang: 'zh' | 'en' }>()
const { t } = useI18n()

const label = computed(() => {
  const key = `order.${props.status}`
  return t(key)
})
</script>

<style scoped>
.status-badge { display: inline-block; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 600; }
.status-badge.submitted { background: #fff3cd; color: #856404; }
.status-badge.confirmed { background: #cce5ff; color: #004085; }
.status-badge.preparing { background: #e2d9f3; color: #5a3d7a; }
.status-badge.ready { background: #d4edda; color: #155724; }
.status-badge.completed { background: #e2e3e5; color: #383d41; }
.status-badge.cancelled { background: #f8d7da; color: #721c24; }
.status-badge.rejected { background: #f8d7da; color: #721c24; }
</style>
