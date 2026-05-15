<template>
  <div class="admin-layout">
    <aside class="sidebar">
      <div class="sidebar-header">
        <span class="sidebar-logo">☕</span>
        <div>
          <div class="sidebar-brand">Clap Cafe</div>
          <div class="sidebar-role">{{ auth.admin?.role || 'Admin' }}</div>
        </div>
      </div>

      <nav class="sidebar-nav">
        <router-link to="/" class="nav-item" :class="{ active: $route.path === '/' }">
          <span class="nav-icon">📊</span>
          Dashboard
        </router-link>
        <router-link to="/menu" class="nav-item" :class="{ active: $route.path === '/menu' }">
          <span class="nav-icon">🍽️</span>
          Menu Manager
        </router-link>
        <router-link to="/seats" class="nav-item" :class="{ active: $route.path === '/seats' }">
          <span class="nav-icon">💺</span>
          Seat Manager
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <div class="admin-info">
          <div class="admin-email">{{ auth.admin?.email }}</div>
        </div>
        <button class="btn btn-outline btn-sm" @click="handleLogout" id="logout-btn">
          Sign Out
        </button>
      </div>
    </aside>

    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

onMounted(() => {
  auth.fetchMe()
})

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.admin-layout {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  width: var(--sidebar-width);
  background: var(--color-surface);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  z-index: 100;
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-6) var(--space-5);
  border-bottom: 1px solid var(--color-border);
}

.sidebar-logo {
  font-size: 1.75rem;
}

.sidebar-brand {
  font-weight: 700;
  font-size: var(--font-size-lg);
  letter-spacing: -0.02em;
}

.sidebar-role {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  text-transform: capitalize;
}

.sidebar-nav {
  flex: 1;
  padding: var(--space-4) var(--space-3);
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-md);
  color: var(--color-text-muted);
  font-weight: 500;
  font-size: var(--font-size-sm);
  transition: all var(--transition-fast);
  text-decoration: none;
}

.nav-item:hover {
  background: var(--color-surface-hover);
  color: var(--color-text);
}

.nav-item.active {
  background: var(--color-primary-soft);
  color: var(--color-primary);
}

.nav-icon {
  font-size: 1.1rem;
  width: 24px;
  text-align: center;
}

.sidebar-footer {
  padding: var(--space-4) var(--space-5);
  border-top: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
}

.admin-email {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 140px;
}

.main-content {
  flex: 1;
  margin-left: var(--sidebar-width);
  padding: var(--space-8);
  min-height: 100vh;
}
</style>
