<template>
  <div class="login-page">
    <div class="login-card fade-in">
      <div class="login-logo">
        <span class="logo-icon">☕</span>
        <h1>Clap Cafe</h1>
        <p class="login-subtitle">Admin Dashboard</p>
      </div>

      <form @submit.prevent="handleLogin" class="login-form">
        <div v-if="auth.error" class="login-error">
          {{ auth.error }}
          <div class="login-error-detail">Check browser console (F12) for details</div>
        </div>

        <div class="form-group">
          <label class="form-label" for="email">Email</label>
          <input
            id="email"
            v-model="email"
            type="email"
            class="form-input"
            placeholder="admin@clapcafe.sg"
            required
            autocomplete="email"
          />
        </div>

        <div class="form-group">
          <label class="form-label" for="password">Password</label>
          <div class="password-wrapper">
            <input
              id="password"
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              class="form-input"
              placeholder="••••••••"
              required
              autocomplete="current-password"
            />
            <button
              type="button"
              class="password-toggle"
              @click="showPassword = !showPassword"
              :title="showPassword ? 'Hide password' : 'Show password'"
            >
              {{ showPassword ? '👁️' : '👁️‍🗨️' }}
            </button>
          </div>
        </div>

        <button
          id="login-submit"
          type="submit"
          class="btn btn-primary login-btn"
          :disabled="auth.loading"
        >
          <span v-if="auth.loading" class="spinner"></span>
          <span v-else>Sign In</span>
        </button>

        <div class="forgot-link">
          <button type="button" class="btn-link" @click="handleForgot">
            Forgot password?
          </button>
        </div>
      </form>

      <!-- Forgot Password Modal -->
      <div v-if="showForgot" class="modal-overlay" @click.self="showForgot = false">
        <div class="modal card">
          <h2 class="modal-title">Reset Password</h2>
          <div v-if="forgotSent" class="forgot-success">
            <div class="success-icon">✓</div>
            <p>Check <strong>clapcafe001@gmail.com</strong> for a reset link.</p>
            <p class="success-note">The link expires in 1 hour.</p>
          </div>
          <div v-else class="forgot-sending">
            <div class="spinner"></div>
            <p>Sending reset link...</p>
          </div>
          <div class="modal-actions" v-if="!forgotSent">
            <button type="button" class="btn btn-outline" @click="showForgot = false">Cancel</button>
          </div>
          <div class="modal-actions" v-else>
            <button type="button" class="btn btn-primary" @click="showForgot = false">Got it</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/api/auth'

const auth = useAuthStore()
const router = useRouter()
const email = ref(localStorage.getItem('admin_email') || '')
const password = ref('')
const showPassword = ref(false)
const showForgot = ref(false)
const forgotLoading = ref(false)
const forgotError = ref('')
const forgotSent = ref(false)
const _hardcodedEmail = 'clapcafe001@gmail.com'

async function handleLogin() {
  try {
    await auth.login(email.value, password.value)
    router.push('/')
  } catch {
    // error is displayed via auth.error
  }
}

async function handleForgot() {
  forgotLoading.value = true
  forgotError.value = ''
  try {
    await authApi.forgotPassword(_hardcodedEmail)
    forgotSent.value = true
  } catch (err: any) {
    forgotError.value = err.response?.data?.detail || 'Failed to send reset email'
  } finally {
    forgotLoading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background:
    radial-gradient(ellipse at 20% 50%, rgba(108, 99, 255, 0.08), transparent 60%),
    radial-gradient(ellipse at 80% 20%, rgba(99, 179, 255, 0.06), transparent 50%),
    var(--color-bg);
}

.login-card {
  width: 100%;
  max-width: 400px;
  padding: var(--space-10);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-lg);
}

.login-logo {
  text-align: center;
  margin-bottom: var(--space-8);
}

.logo-icon {
  font-size: 3rem;
  display: block;
  margin-bottom: var(--space-2);
}

.login-logo h1 {
  font-size: var(--font-size-2xl);
  font-weight: 700;
  letter-spacing: -0.03em;
  background: linear-gradient(135deg, var(--color-primary), #a78bfa);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.login-subtitle {
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
  margin-top: var(--space-1);
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}

.login-error {
  padding: var(--space-3);
  background: var(--color-danger-soft);
  color: var(--color-danger);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  text-align: center;
  border: 1px solid var(--color-danger);
}

.password-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.password-wrapper .form-input {
  flex: 1;
  padding-right: 44px;
}

.password-toggle {
  position: absolute;
  right: 10px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  font-size: 1rem;
  line-height: 1;
  opacity: 0.6;
  transition: opacity var(--transition-fast);
}

.password-toggle:hover {
  opacity: 1;
  background: none;
}

.login-btn {
  width: 100%;
  justify-content: center;
  padding: var(--space-3) var(--space-4);
  font-size: var(--font-size-base);
  margin-top: var(--space-2);
}

.forgot-link {
  text-align: center;
  margin-top: calc(var(--space-2) * -1);
}

.btn-link {
  background: none;
  border: none;
  color: var(--color-primary);
  font-size: var(--font-size-sm);
  cursor: pointer;
  padding: var(--space-2);
  text-decoration: underline;
  text-underline-offset: 2px;
  transition: opacity var(--transition-fast);
}
.btn-link:hover {
  opacity: 0.75;
}

.forgot-success {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-5);
  background: var(--color-success-soft);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-success);
  text-align: center;
}

.success-icon {
  width: 48px;
  height: 48px;
  background: var(--color-success);
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: 700;
}

.forgot-success p {
  color: var(--color-success);
  margin: 0;
}

.success-note {
  font-size: var(--font-size-xs) !important;
  opacity: 0.7;
}

.forgot-sending {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-5);
  color: var(--color-text-muted);
}

.forgot-success {
  padding: var(--space-4);
  background: var(--color-success-soft);
  color: var(--color-success);
  border-radius: var(--radius-md);
  text-align: center;
  border: 1px solid var(--color-success);
}

/* Modal */
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.6); display: flex;
  align-items: center; justify-content: center; z-index: 200;
  backdrop-filter: blur(4px);
}
.modal {
  width: 100%; max-width: 400px; max-height: 90vh; overflow-y: auto;
  animation: fadeIn 0.2s ease;
}
.modal-title { font-size: var(--font-size-xl); font-weight: 600; margin-bottom: var(--space-5); }
.modal-form { display: flex; flex-direction: column; gap: var(--space-4); }
.modal-actions { display: flex; justify-content: flex-end; gap: var(--space-3); margin-top: var(--space-4); }
</style>
