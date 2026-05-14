<template>
  <div class="lang-switch">
    <button :class="{ active: locale === 'zh' }" @click="switchLang('zh')">中</button>
    <button :class="{ active: locale === 'en' }" @click="switchLang('en')">EN</button>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const { locale } = useI18n()

function switchLang(lang: 'zh' | 'en') {
  locale.value = lang
  const url = new URL(window.location.href)
  url.searchParams.set('lang', lang)
  window.history.replaceState({}, '', url.toString())
}
</script>

<style scoped>
.lang-switch { display: flex; gap: 4px; background: #f0ebe3; border-radius: 16px; padding: 2px; }
.lang-switch button { border: none; background: none; padding: 4px 8px; border-radius: 14px; font-size: 12px; cursor: pointer; color: #888; transition: all 0.2s; }
.lang-switch button.active { background: #D4A574; color: #fff; }
</style>
