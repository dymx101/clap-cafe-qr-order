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
          <input
            id="password"
            v-model="password"
            type="password"
            class="form-input"
            placeholder="••••••••"
            required
            autocomplete="current-password"
          />
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
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const email = ref('')
const password = ref('')

async function handleLogin() {
  try {
    await auth.login(email.value, password.value)
    router.push('/')
  } catch {
    // error is displayed via auth.error
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
}

.login-btn {
  width: 100%;
  justify-content: center;
  padding: var(--space-3) var(--space-4);
  font-size: var(--font-size-base);
  margin-top: var(--space-2);
}
</style>
