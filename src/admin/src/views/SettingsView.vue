<template>
  <div class="settings-view fade-in">
    <div class="page-header">
      <h1 class="page-title">Settings</h1>
    </div>

    <div class="card settings-card">
      <h2 class="section-title">Change Password</h2>

      <div v-if="success" class="success-msg">
        Password updated successfully!
      </div>

      <div v-if="error" class="error-msg">
        {{ error }}
      </div>

      <form @submit.prevent="handleChange" class="settings-form">
        <div class="form-group">
          <label class="form-label" for="current">Current Password</label>
          <input
            id="current"
            v-model="currentPassword"
            type="password"
            class="form-input"
            placeholder="••••••••"
            required
          />
        </div>

        <div class="form-group">
          <label class="form-label" for="new-pass">New Password</label>
          <input
            id="new-pass"
            v-model="newPassword"
            type="password"
            class="form-input"
            placeholder="••••••••"
            required
            minlength="6"
          />
        </div>

        <div class="form-group">
          <label class="form-label" for="confirm">Confirm New Password</label>
          <input
            id="confirm"
            v-model="confirmPassword"
            type="password"
            class="form-input"
            placeholder="••••••••"
            required
            minlength="6"
          />
        </div>

        <div class="form-actions">
          <button type="submit" class="btn btn-primary" :disabled="loading">
            <span v-if="loading" class="spinner"></span>
            <span v-else>Update Password</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const currentPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const error = ref('')
const success = ref(false)

async function handleChange() {
  error.value = ''
  success.value = false
  if (newPassword.value !== confirmPassword.value) {
    error.value = 'New passwords do not match'
    return
  }
  if (newPassword.value.length < 6) {
    error.value = 'Password must be at least 6 characters'
    return
  }
  loading.value = true
  try {
    await auth.changePassword(currentPassword.value, newPassword.value)
    success.value = true
    currentPassword.value = ''
    newPassword.value = ''
    confirmPassword.value = ''
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Failed to update password'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.settings-card {
  max-width: 480px;
}

.section-title {
  font-size: var(--font-size-lg);
  font-weight: 600;
  margin-bottom: var(--space-5);
}

.settings-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: var(--space-2);
}

.success-msg {
  padding: var(--space-3);
  background: var(--color-success-soft);
  color: var(--color-success);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  text-align: center;
  border: 1px solid var(--color-success);
  margin-bottom: var(--space-4);
}

.error-msg {
  padding: var(--space-3);
  background: var(--color-danger-soft);
  color: var(--color-danger);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  text-align: center;
  border: 1px solid var(--color-danger);
  margin-bottom: var(--space-4);
}
</style>
