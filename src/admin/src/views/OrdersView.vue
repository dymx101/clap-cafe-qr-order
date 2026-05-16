<template>
  <div class="orders-view fade-in">
    <div class="page-header">
      <h1 class="page-title">Order Manager</h1>
    </div>

    <!-- Status Filter Tabs -->
    <div class="filter-tabs">
      <button
        v-for="tab in statusTabs"
        :key="tab.value"
        class="filter-tab"
        :class="{ active: filterStatus === tab.value }"
        @click="setStatusFilter(tab.value)"
      >
        {{ tab.label }}
        <span v-if="tab.count !== null" class="tab-count">{{ tab.count }}</span>
      </button>
    </div>

    <!-- Orders Table -->
    <div class="card" style="padding: 0; overflow: hidden;">
      <div v-if="loading" class="table-loading"><span class="spinner"></span></div>
      <table v-else class="data-table">
        <thead>
          <tr>
            <th>Order ID</th>
            <th>Seat</th>
            <th>Total</th>
            <th>Status</th>
            <th>Payment</th>
            <th>Created</th>
            <th style="width: 100px;">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="order in orders" :key="order.id">
            <td class="order-id">{{ order.id }}</td>
            <td>{{ order.seat_id }}</td>
            <td>${{ order.total_sgd.toFixed(2) }}</td>
            <td>
              <span class="badge" :class="statusBadgeClass(order.status)">
                {{ statusLabel(order.status) }}
              </span>
            </td>
            <td>
              <span class="badge" :class="paymentBadgeClass(order.payment_status)">
                {{ order.payment_status }}
              </span>
            </td>
            <td class="text-muted">{{ formatDate(order.created_at) }}</td>
            <td>
              <div class="row-actions">
                <button class="btn-icon" title="View" @click="openDetail(order)">👁️</button>
              </div>
            </td>
          </tr>
          <tr v-if="orders.length === 0">
            <td colspan="7" class="empty-state">No orders found.</td>
          </tr>
        </tbody>
      </table>

      <!-- Pagination -->
      <div v-if="totalCount > limit" class="pagination">
        <button
          class="btn btn-outline btn-sm"
          :disabled="page <= 1"
          @click="loadOrders(page - 1)"
        >Previous</button>
        <span class="page-info">Page {{ page }} of {{ totalPages }}</span>
        <button
          class="btn btn-outline btn-sm"
          :disabled="page >= totalPages"
          @click="loadOrders(page + 1)"
        >Next</button>
      </div>
    </div>

    <!-- Order Detail Modal -->
    <div v-if="showDetailModal" class="modal-overlay" @click.self="showDetailModal = false">
      <div class="modal card" style="max-width: 640px;">
        <div class="modal-header">
          <h2 class="modal-title">Order {{ selectedOrder?.id }}</h2>
          <button class="btn-icon" @click="showDetailModal = false">✕</button>
        </div>

        <div v-if="selectedOrder" class="order-detail">
          <!-- Status -->
          <div class="detail-section">
            <div class="detail-row">
              <span class="detail-label">Status</span>
              <span class="badge" :class="statusBadgeClass(selectedOrder.status)">
                {{ statusLabel(selectedOrder.status) }}
              </span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Payment</span>
              <span class="badge" :class="paymentBadgeClass(selectedOrder.payment_status)">
                {{ selectedOrder.payment_status }}
              </span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Seat</span>
              <span>{{ selectedOrder.seat_id }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Total</span>
              <span class="text-lg">${{ selectedOrder.total_sgd.toFixed(2) }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Created</span>
              <span>{{ formatDate(selectedOrder.created_at) }}</span>
            </div>
            <div v-if="selectedOrder.customer_notes" class="detail-row">
              <span class="detail-label">Customer Notes</span>
              <span class="text-warning">{{ selectedOrder.customer_notes }}</span>
            </div>
            <div v-if="selectedOrder.rejected_reason" class="detail-row">
              <span class="detail-label">Rejection Reason</span>
              <span class="text-danger">{{ selectedOrder.rejected_reason }}</span>
            </div>
          </div>

          <!-- Items -->
          <div class="detail-section">
            <h3 class="section-title">Items</h3>
            <div v-for="item in selectedOrder.items" :key="item.id" class="order-item">
              <div class="item-header">
                <span class="item-qty">{{ item.quantity }}x</span>
                <span class="item-name">{{ item.item_name_en }}</span>
                <span class="item-price">${{ (item.unit_price * item.quantity).toFixed(2) }}</span>
              </div>
              <div v-if="Object.keys(item.options || {}).length > 0" class="item-options">
                {{ formatOptions(item.options) }}
              </div>
              <div v-if="item.notes" class="item-notes">📝 {{ item.notes }}</div>
            </div>
          </div>

          <!-- Notes Edit -->
          <div class="detail-section">
            <h3 class="section-title">Internal Notes</h3>
            <textarea
              v-model="notesForm.notes"
              class="form-input"
              rows="2"
              placeholder="Internal notes (not shown to customer)"
            ></textarea>
          </div>

          <!-- Actions -->
          <div class="modal-actions">
            <button
              v-if="selectedOrder.status === 'submitted'"
              class="btn btn-danger"
              :disabled="actionLoading"
              @click="cancelOrder(selectedOrder.id)"
            >Cancel Order</button>
            <button
              class="btn btn-primary"
              :disabled="actionLoading || !notesChanged"
              @click="saveNotes(selectedOrder.id)"
            >
              <span v-if="actionLoading" class="spinner"></span>
              <span v-else>Save Notes</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ordersApi, type OrderResponse } from '@/api/orders'

const STATUS_TABS = [
  { value: '', label: 'All' },
  { value: 'submitted', label: 'Submitted' },
  { value: 'confirmed', label: 'Confirmed' },
  { value: 'preparing', label: 'Preparing' },
  { value: 'ready', label: 'Ready' },
  { value: 'completed', label: 'Completed' },
  { value: 'cancelled', label: 'Cancelled' },
  { value: 'rejected', label: 'Rejected' },
]

const STATUS_LABELS: Record<string, string> = {
  submitted: 'Submitted',
  confirmed: 'Confirmed',
  preparing: 'Preparing',
  ready: 'Ready',
  completed: 'Completed',
  cancelled: 'Cancelled',
  rejected: 'Rejected',
}

const orders = ref<OrderResponse[]>([])
const loading = ref(false)
const page = ref(1)
const limit = ref(20)
const totalCount = ref(0)
const filterStatus = ref('')
const tabCounts = ref<Record<string, number>>({})

const showDetailModal = ref(false)
const selectedOrder = ref<OrderResponse | null>(null)
const actionLoading = ref(false)
const notesForm = ref({ notes: '' })

const totalPages = computed(() => Math.ceil(totalCount.value / limit.value))
const statusTabs = computed(() =>
  STATUS_TABS.map(t => ({
    ...t,
    count: t.value ? (tabCounts.value[t.value] ?? null) : totalCount.value,
  }))
)
const notesChanged = computed(
  () => notesForm.value.notes !== (selectedOrder.value?.notes || '')
)

onMounted(() => {
  loadOrders(1)
  loadTabCounts()
})

async function loadTabCounts() {
  try {
    const res = await ordersApi.list({ limit: 1 })
    totalCount.value = res.data.total_count
    for (const tab of STATUS_TABS) {
      if (!tab.value) continue
      const r = await ordersApi.list({ status: tab.value, limit: 1 })
      tabCounts.value[tab.value] = r.data.total_count
    }
  } catch { /* ignore */ }
}

async function loadOrders(p = 1) {
  p = Math.max(1, p)
  page.value = p
  loading.value = true
  try {
    const params: any = { page: p, limit: limit.value }
    if (filterStatus.value) params.status = filterStatus.value
    console.log('[Orders] GET /admin/orders with params:', params)
    const res = await ordersApi.list(params)
    console.log('[Orders] Response:', res.data)
    orders.value = res.data.orders
    totalCount.value = res.data.total_count
  } catch (err: any) {
    console.error('[Orders] Error:', err?.response?.data)
  } finally { loading.value = false }
}

function setStatusFilter(status: string) {
  filterStatus.value = status
  loadOrders(1)
}

async function openDetail(order: OrderResponse) {
  selectedOrder.value = order
  notesForm.value.notes = order.notes || ''
  showDetailModal.value = true
}

async function saveNotes(orderId: string) {
  actionLoading.value = true
  try {
    const res = await ordersApi.updateNotes(orderId, { notes: notesForm.value.notes })
    const updated = res.data
    orders.value = orders.value.map(o => o.id === orderId ? updated : o)
    selectedOrder.value = updated
  } finally {
    actionLoading.value = false
  }
}

async function cancelOrder(orderId: string) {
  if (!confirm('Cancel this order?')) return
  actionLoading.value = true
  try {
    const res = await ordersApi.cancel(orderId)
    orders.value = orders.value.map(o => o.id === orderId ? res.data : o)
    selectedOrder.value = res.data
    await loadTabCounts()
  } finally {
    actionLoading.value = false
  }
}

function statusLabel(s: string) { return STATUS_LABELS[s] ?? s }
function statusBadgeClass(s: string) {
  const map: Record<string, string> = {
    submitted: 'badge-default', confirmed: 'badge-info', preparing: 'badge-warning',
    ready: 'badge-success', completed: 'badge-success', cancelled: 'badge-danger', rejected: 'badge-danger',
  }
  return map[s] ?? 'badge-default'
}
function paymentBadgeClass(s: string) {
  const map: Record<string, string> = {
    pending: 'badge-default', paid: 'badge-success', failed: 'badge-danger',
    refunded: 'badge-info', cancelled: 'badge-danger',
  }
  return map[s] ?? 'badge-default'
}
function formatDate(d: string) {
  return new Date(d).toLocaleString('en-SG', { dateStyle: 'short', timeStyle: 'short' })
}
function formatOptions(opts: Record<string, any>) {
  return Object.entries(opts)
    .filter(([, v]) => v != null && v !== '')
    .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`)
    .join(' · ')
}
</script>

<style scoped>
.orders-view { max-width: 1100px; }
.filter-tabs {
  display: flex;
  gap: var(--space-2);
  margin-bottom: var(--space-5);
  flex-wrap: wrap;
}
.filter-tab {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}
.filter-tab:hover { border-color: var(--color-primary); color: var(--color-primary); }
.filter-tab.active {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: white;
}
.tab-count {
  background: rgba(255,255,255,0.3);
  border-radius: 10px;
  padding: 0 6px;
  font-size: 11px;
}
.order-id { font-family: monospace; font-size: var(--font-size-sm); }
.text-lg { font-size: var(--font-size-lg); font-weight: 600; }
.text-warning { color: var(--color-warning); }
.text-danger { color: var(--color-danger); }
.text-muted { color: var(--color-text-muted); font-size: var(--font-size-sm); }

.order-detail { padding: var(--space-2) 0; }
.detail-section {
  padding: var(--space-4) 0;
  border-bottom: 1px solid var(--color-border);
}
.detail-section:last-of-type { border-bottom: none; }
.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-2) 0;
}
.detail-label { color: var(--color-text-muted); font-size: var(--font-size-sm); }
.section-title {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: var(--space-3);
}
.order-item {
  padding: var(--space-3) 0;
  border-bottom: 1px solid var(--color-border);
}
.order-item:last-child { border-bottom: none; }
.item-header { display: flex; gap: var(--space-3); align-items: baseline; }
.item-qty { font-weight: 700; color: var(--color-primary); min-width: 28px; }
.item-name { flex: 1; }
.item-price { font-weight: 600; }
.item-options {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
  padding-left: 28px;
  margin-top: 2px;
}
.item-notes { font-size: var(--font-size-sm); color: var(--color-warning); padding-left: 28px; }

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-5);
}
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-4);
  padding: var(--space-4);
  border-top: 1px solid var(--color-border);
}
.page-info { font-size: var(--font-size-sm); color: var(--color-text-muted); }
</style>
