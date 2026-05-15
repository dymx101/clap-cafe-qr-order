<template>
  <div class="dashboard fade-in">
    <div class="page-header">
      <h1 class="page-title">Dashboard</h1>
      <span class="page-date">{{ formattedDate }}</span>
    </div>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon" style="background: var(--color-primary-soft); color: var(--color-primary);">🍽️</div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.categories }}</div>
          <div class="stat-label">Categories</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: var(--color-success-soft); color: var(--color-success);">☕</div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.items }}</div>
          <div class="stat-label">Menu Items</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: var(--color-warning-soft); color: var(--color-warning);">💺</div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.seats }}</div>
          <div class="stat-label">Active Seats</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: var(--color-danger-soft); color: var(--color-danger);">🔴</div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.unavailable }}</div>
          <div class="stat-label">Unavailable Items</div>
        </div>
      </div>
    </div>

    <div class="quick-links card">
      <h2 class="section-title">Quick Actions</h2>
      <div class="actions-grid">
        <router-link to="/menu" class="action-card">
          <span class="action-icon">📝</span>
          <span class="action-label">Edit Menu</span>
          <span class="action-desc">Manage categories and items</span>
        </router-link>
        <router-link to="/seats" class="action-card">
          <span class="action-icon">🪑</span>
          <span class="action-label">Manage Seats</span>
          <span class="action-desc">Toggle seat availability</span>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import client from '@/api/client'

const stats = ref({
  categories: 0,
  items: 0,
  seats: 0,
  unavailable: 0
})

const formattedDate = computed(() =>
  new Date().toLocaleDateString('en-SG', {
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
  })
)

onMounted(async () => {
  try {
    const [catRes, itemRes, seatRes] = await Promise.all([
      client.get('/admin/categories/'),
      client.get('/admin/items/'),
      client.get('/admin/seats/')
    ])
    stats.value.categories = catRes.data.length
    stats.value.items = itemRes.data.length
    stats.value.seats = seatRes.data.filter((s: any) => s.is_active).length
    stats.value.unavailable = itemRes.data.filter((i: any) => !i.is_available).length
  } catch {
    // stats remain at 0
  }
})
</script>

<style scoped>
.page-date {
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--space-4);
  margin-bottom: var(--space-8);
}

.stat-card {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-5);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  transition: transform var(--transition-fast), box-shadow var(--transition-fast);
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.stat-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
  font-size: 1.25rem;
  flex-shrink: 0;
}

.stat-value {
  font-size: var(--font-size-2xl);
  font-weight: 700;
  letter-spacing: -0.02em;
}

.stat-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.section-title {
  font-size: var(--font-size-lg);
  font-weight: 600;
  margin-bottom: var(--space-5);
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: var(--space-4);
}

.action-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-6);
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  text-decoration: none;
  color: var(--color-text);
  transition: all var(--transition-fast);
  text-align: center;
}

.action-card:hover {
  border-color: var(--color-primary);
  background: var(--color-primary-soft);
  transform: translateY(-2px);
}

.action-icon {
  font-size: 2rem;
}

.action-label {
  font-weight: 600;
  font-size: var(--font-size-base);
}

.action-desc {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}
</style>
