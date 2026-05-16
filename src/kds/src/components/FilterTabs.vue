<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps<{
  modelValue: string
  counts: Record<string, number>
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const tabs = [
  { key: 'all', labelKey: 'kds.filter.all' },
  { key: 'submitted', labelKey: 'kds.filter.submitted' },
  { key: 'confirmed', labelKey: 'kds.filter.confirmed' },
  { key: 'preparing', labelKey: 'kds.filter.preparing' },
  { key: 'ready', labelKey: 'kds.filter.ready' }
]

function selectTab(key: string) {
  emit('update:modelValue', key)
}
</script>

<template>
  <div class="filter-tabs">
    <button
      v-for="tab in tabs"
      :key="tab.key"
      :class="['tab', { active: modelValue === tab.key }]"
      @click="selectTab(tab.key)"
    >
      <span class="tab-label">{{ t(tab.labelKey) }}</span>
      <span
        v-if="counts[tab.key] !== undefined && counts[tab.key] > 0"
        class="tab-count"
      >
        {{ counts[tab.key] }}
      </span>
    </button>
  </div>
</template>

<style scoped>
.filter-tabs {
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  background: #16213e;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.tab {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  background: #1e1e2e;
  border: 2px solid transparent;
  border-radius: 8px;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s;
  min-height: 48px;
}

.tab:hover {
  background: #2a2a3e;
}

.tab.active {
  background: #1e3a5f;
  border-color: #3b82f6;
}

.tab-label {
  font-size: 15px;
  font-weight: 600;
  color: #9ca3af;
}

.tab.active .tab-label {
  color: #f3f4f6;
}

.tab-count {
  background: #ef4444;
  color: white;
  font-size: 12px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 10px;
  min-width: 20px;
  text-align: center;
}

.tab.active .tab-count {
  background: #3b82f6;
}
</style>
