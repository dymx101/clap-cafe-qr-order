import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createI18n } from 'vue-i18n'
import App from './App.vue'
import zh from './locales/zh.json'
import en from './locales/en.json'

function getInitialLocale(): string {
  const params = new URLSearchParams(window.location.search)
  const lang = params.get('lang')
  if (lang === 'en' || lang === 'zh') return lang
  return 'zh'
}

const i18n = createI18n({
  legacy: false,
  locale: getInitialLocale(),
  fallbackLocale: 'zh',
  messages: { zh, en }
})

const app = createApp(App)
app.use(createPinia())
app.use(i18n)
app.mount('#app')
