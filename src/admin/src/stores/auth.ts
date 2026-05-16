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
    console.log('[Auth] Login attempt for:', email)
    try {
      const res = await client.post('/admin/login', { email, password })
      console.log('[Auth] Login success, token received')
      token.value = res.data.access_token
      admin.value = res.data.admin
      localStorage.setItem('admin_token', token.value)
      localStorage.setItem('admin_email', email)
    } catch (err: any) {
      console.error('[Auth] Login error:', {
        url: err.config?.url,
        status: err.response?.status,
        data: err.response?.data,
        headers: err.response?.headers,
      })
      const detail = err.response?.data?.detail || err.message || 'Login failed'
      error.value = detail
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

  async function changePassword(currentPassword: string, newPassword: string) {
    loading.value = true
    error.value = ''
    try {
      await client.post('/admin/change-password', {
        current_password: currentPassword,
        new_password: newPassword
      })
    } catch (err: any) {
      const detail = err.response?.data?.detail || err.message || 'Password change failed'
      error.value = detail
      throw err
    } finally {
      loading.value = false
    }
  }

  function logout() {
    token.value = ''
    admin.value = null
    localStorage.removeItem('admin_token')
  }

  return { token, admin, loading, error, isAuthenticated, login, fetchMe, logout, changePassword }
})
