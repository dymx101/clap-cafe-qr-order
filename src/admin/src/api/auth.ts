// src/api/auth.ts
import client from './client'

export const authApi = {
  login(email: string, password: string) {
    return client.post('/admin/login', { email, password })
  },

  me() {
    return client.get('/admin/me')
  },

  changePassword(currentPassword: string, newPassword: string) {
    return client.post('/admin/change-password', {
      current_password: currentPassword,
      new_password: newPassword
    })
  },

  forgotPassword(email: string) {
    return client.post('/admin/forgot-password', { email })
  },

  resetPassword(token: string, newPassword: string) {
    return client.post('/admin/reset-password', {
      token,
      new_password: newPassword
    })
  }
}
