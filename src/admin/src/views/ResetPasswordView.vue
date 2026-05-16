<template>
  <div class="reset-page">
    <div class="reset-card fade-in">
      <div class="reset-logo">
        <span class="logo-icon">☕</span>
        <h1>Reset Password</h1>
        <p class="reset-subtitle">Enter your new password</p>
      </div>

      <div v-if="success" class="reset-success">
        <p>Password reset successfully!</p>
        <router-link to="/login" class="btn btn-primary">Go to Login</router-link>
      </div>

      <form v-else @submit.prevent="handleReset" class="reset-form">
        <div v-if="error" class="login-error">
          {{ error }}
        </div>

        <div class="form-group">
          <label class="form-label" for="new-password">New Password</label>
          <input
            id="new-password"
            v-model="newPassword"
            type="password"
            class="form-input"
            placeholder="••••••••"
            required
            minlength="6"
          />
        </div>

        <div class="form-group">
          <label class="form-label" for="confirm-password">Confirm Password</label>
          <input
            id="confirm-password"
            v-model="confirmPassword"
            type="password"
            class="form-input"
            placeholder="••••••••"
            required
            minlength="6"
          />
        </div>

        <button
          type="submit"
          class="btn btn-primary reset-btn"
          :disabled="loading"
        >
          {{ loading ? 'Resetting...' : 'Reset Password' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { authApi } from '@/api/auth'

const route = useRoute()
const router = useRouter()
const newPassword = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const error = ref('')
const success = ref(false)

onMounted(() => {
  const token = route.query.token as string
  if (!token) {
    error.value = 'Missing reset token. Please use the link from your email.'
  }
})

async function handleReset() {
  error.value = ''
  if (newPassword.value !== confirmPassword.value) {
    error.value = 'Passwords do not match'
    return
  }
  if (newPassword.value.length < 6) {
    error.value = 'Password must be at least 6 characters'
    return
  }
  loading.value = true
  try {
    const token = route.query.token as string
    await authApi.resetPassword(token, newPassword.value)
    success.value = true
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Failed to reset password'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.reset-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: radial-gradient(ellipse at 20% 50%, rgba(108, 99, 255, 0.08), transparent 60%),
    radial-gradient(ellipse at 80% 20%, rgba(99, 179, 255, 0.06), transparent 50%),
    var(--color-bg);
}

.reset-card {
  width: 100%;
  max-width: 400px;
  padding: var(--space-10);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-lg);
}

.reset-logo {
  text-align: center;
  margin-bottom: var(--space-8);
}

.logo-icon {
  font-size: 3rem;
  display: block;
  margin-bottom: var(--space-2);
}

.reset-logo h1 {
  font-size: var(--font-size-2xl);
  font-weight: 700;
  letter-spacing: -0.03em;
  background: linear-gradient(135deg, var(--color-primary), #a78bfa);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.reset-subtitle {
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
  margin-top: var(--space-1);
}

.reset-form {
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

.reset-btn {
  width: 100%;
  justify-content: center;
  padding: var(--space-3) var(--space-4);
  font-size: var(--font-size-base);
  margin-top: var(--space-2);
}

.reset-success {
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  align-items: center;
  color: var(--color-success);
}
</style>
