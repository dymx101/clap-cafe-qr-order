import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createI18n } from 'vue-i18n'
import App from './App.vue'
import router from './router'
import zh from './locales/zh.json'
import en from './locales/en.json'

const params = new URLSearchParams(window.location.search)
const defaultLang = params.get('lang') || 'zh'

const i18n = createI18n({
  legacy: false,
  locale: defaultLang,
  fallbackLocale: 'zh',
  messages: { zh, en }
})

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(i18n)
app.mount('#app')
