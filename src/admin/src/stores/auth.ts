// src/stores/auth.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import client from '@/api/client'

export interface AdminUser {
  id: string
  email: string
  display_name: string
  role: string
  is_active: boolean
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('admin_token') || '')
  const admin = ref<AdminUser | null>(null)
  const loading = ref(false)
  const error = ref('')

  const isAuthenticated = computed(() => !!token.value)

  async function login(email: string, password: string) {
    loading.value = true
    error.value = ''
    try {
      const res = await client.post('/admin/login', { email, password })
      token.value = res.data.access_token
      admin.value = res.data.admin
      localStorage.setItem('admin_token', token.value)
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Login failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchMe() {
    if (!token.value) return
    try {
      const res = await client.get('/admin/me')
      admin.value = res.data
    } catch {
      logout()
    }
  }

  function logout() {
    token.value = ''
    admin.value = null
    localStorage.removeItem('admin_token')
  }

  return { token, admin, loading, error, isAuthenticated, login, fetchMe, logout }
})
