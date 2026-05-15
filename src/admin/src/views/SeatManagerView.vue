<template>
  <div class="seat-manager fade-in">
    <div class="page-header">
      <h1 class="page-title">Seat Manager</h1>
      <button class="btn btn-primary" @click="showModal = true" id="add-seat-btn">+ New Seat</button>
    </div>

    <!-- Zone Tabs -->
    <div class="zone-tabs">
      <button
        v-for="z in zones"
        :key="z"
        class="zone-tab"
        :class="{ active: selectedZone === z }"
        @click="selectedZone = z"
      >
        {{ z === 'all' ? 'All' : z.charAt(0).toUpperCase() + z.slice(1) }}
        <span class="zone-count">{{ z === 'all' ? seats.length : seats.filter(s => s.zone === z).length }}</span>
      </button>
    </div>

    <!-- Seats Grid -->
    <div class="seats-grid">
      <div
        v-for="seat in filteredSeats"
        :key="seat.id"
        class="seat-card"
        :class="{ inactive: !seat.is_active }"
      >
        <div class="seat-header">
          <div class="seat-id">{{ seat.id }}</div>
          <span
            class="status-dot"
            :class="statusColor(seat.status)"
            :title="seat.status"
          ></span>
        </div>
        <div class="seat-labels">
          <div class="seat-label-en">{{ seat.label_en }}</div>
          <div class="seat-label-zh">{{ seat.label_zh }}</div>
        </div>
        <div class="seat-zone badge badge-info">{{ seat.zone }}</div>
        <div class="seat-actions">
          <select
            :value="seat.status"
            @change="updateStatus(seat, ($event.target as HTMLSelectElement).value)"
            class="form-input status-select"
          >
            <option value="vacant">Vacant</option>
            <option value="occupied">Occupied</option>
            <option value="reserved">Reserved</option>
            <option value="inactive">Inactive</option>
          </select>
          <button
            class="btn-icon"
            :title="seat.is_active ? 'Deactivate' : 'Activate'"
            @click="toggleActive(seat)"
          >
            {{ seat.is_active ? '🔴' : '🟢' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="filteredSeats.length === 0 && !loading" class="empty-state card">
      No seats found for this zone.
    </div>

    <!-- New Seat Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal card">
        <h2 class="modal-title">Add New Seat</h2>
        <form @submit.prevent="createSeat" class="modal-form">
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Seat ID</label>
              <input v-model="seatForm.id" class="form-input" placeholder="T13, O05, B07..." required />
            </div>
            <div class="form-group">
              <label class="form-label">Zone</label>
              <select v-model="seatForm.zone" class="form-input" required>
                <option value="indoor">Indoor</option>
                <option value="outdoor">Outdoor</option>
                <option value="bar">Bar</option>
              </select>
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Label (EN)</label>
              <input v-model="seatForm.label_en" class="form-input" placeholder="Table 13" required />
            </div>
            <div class="form-group">
              <label class="form-label">Label (ZH)</label>
              <input v-model="seatForm.label_zh" class="form-input" placeholder="13号桌" required />
            </div>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn btn-outline" @click="showModal = false">Cancel</button>
            <button type="submit" class="btn btn-primary" :disabled="saving">
              {{ saving ? 'Creating...' : 'Create' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue'
import client from '@/api/client'

interface Seat {
  id: string; label_zh: string; label_en: string
  zone: string; status: string; is_active: boolean
}

const seats = ref<Seat[]>([])
const loading = ref(true)
const saving = ref(false)
const selectedZone = ref('all')
const showModal = ref(false)

const seatForm = reactive({
  id: '', label_en: '', label_zh: '', zone: 'indoor'
})

const zones = computed(() => {
  const z = new Set(seats.value.map(s => s.zone))
  return ['all', ...z]
})

const filteredSeats = computed(() => {
  if (selectedZone.value === 'all') return seats.value
  return seats.value.filter(s => s.zone === selectedZone.value)
})

function statusColor(status: string): string {
  switch (status) {
    case 'vacant': return 'dot-green'
    case 'occupied': return 'dot-orange'
    case 'reserved': return 'dot-blue'
    default: return 'dot-grey'
  }
}

async function fetchSeats() {
  loading.value = true
  try {
    const res = await client.get('/admin/seats/')
    seats.value = res.data
  } finally {
    loading.value = false
  }
}

async function updateStatus(seat: Seat, newStatus: string) {
  await client.put(`/admin/seats/${seat.id}`, { status: newStatus })
  await fetchSeats()
}

async function toggleActive(seat: Seat) {
  await client.put(`/admin/seats/${seat.id}`, { is_active: !seat.is_active })
  await fetchSeats()
}

async function createSeat() {
  saving.value = true
  try {
    await client.post('/admin/seats/', seatForm)
    showModal.value = false
    Object.assign(seatForm, { id: '', label_en: '', label_zh: '', zone: 'indoor' })
    await fetchSeats()
  } finally {
    saving.value = false
  }
}

onMounted(fetchSeats)
</script>

<style scoped>
.zone-tabs {
  display: flex;
  gap: var(--space-2);
  margin-bottom: var(--space-5);
}

.zone-tab {
  display: flex; align-items: center; gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  border: 1px solid var(--color-border);
  border-radius: 9999px;
  background: transparent;
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}
.zone-tab:hover { border-color: var(--color-text-muted); color: var(--color-text); }
.zone-tab.active { background: var(--color-primary); border-color: var(--color-primary); color: #fff; }

.zone-count {
  font-size: var(--font-size-xs);
  background: rgba(255,255,255,0.15);
  padding: 0 6px;
  border-radius: 9999px;
}

.seats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: var(--space-4);
}

.seat-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  transition: all var(--transition-fast);
}
.seat-card:hover {
  border-color: var(--color-primary);
  box-shadow: var(--shadow-sm);
}
.seat-card.inactive { opacity: 0.5; }

.seat-header {
  display: flex; justify-content: space-between; align-items: center;
}

.seat-id {
  font-size: var(--font-size-xl);
  font-weight: 700;
  letter-spacing: -0.02em;
}

.status-dot {
  width: 10px; height: 10px; border-radius: 50%;
}
.dot-green { background: var(--color-success); box-shadow: 0 0 6px var(--color-success); }
.dot-orange { background: var(--color-warning); box-shadow: 0 0 6px var(--color-warning); }
.dot-blue { background: var(--color-info); box-shadow: 0 0 6px var(--color-info); }
.dot-grey { background: var(--color-text-muted); }

.seat-labels { }
.seat-label-en { font-size: var(--font-size-sm); }
.seat-label-zh { font-size: var(--font-size-xs); color: var(--color-text-muted); }

.seat-actions {
  display: flex; align-items: center; gap: var(--space-2); margin-top: auto;
}

.status-select {
  flex: 1; font-size: var(--font-size-xs); padding: var(--space-1) var(--space-2);
}

.empty-state { text-align: center; color: var(--color-text-muted); padding: var(--space-10); }

/* Modal */
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.6); display: flex;
  align-items: center; justify-content: center; z-index: 200;
  backdrop-filter: blur(4px);
}
.modal {
  width: 100%; max-width: 500px;
  animation: fadeIn 0.2s ease;
}
.modal-title { font-size: var(--font-size-xl); font-weight: 600; margin-bottom: var(--space-5); }
.modal-form { display: flex; flex-direction: column; gap: var(--space-4); }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-4); }
.modal-actions { display: flex; justify-content: flex-end; gap: var(--space-3); margin-top: var(--space-4); }
</style>
