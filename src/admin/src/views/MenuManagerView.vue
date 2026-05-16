<template>
  <div class="menu-manager fade-in">
    <div class="page-header">
      <h1 class="page-title">Menu Manager</h1>
      <div class="header-actions">
        <button class="btn btn-outline" @click="showCategoryModal = true" id="add-category-btn">
          + Category
        </button>
        <button class="btn btn-primary" @click="openItemModal()" id="add-item-btn">
          + New Item
        </button>
      </div>
    </div>

    <!-- Categories -->
    <div class="categories-bar">
      <button
        v-for="cat in categories"
        :key="cat.id"
        class="cat-chip"
        :class="{ active: selectedCategoryId === cat.id, inactive: !cat.is_active }"
        @click="selectedCategoryId = cat.id"
      >
        {{ cat.name_en }}
        <span v-if="!cat.is_active" class="badge badge-warning" style="margin-left: 4px;">off</span>
      </button>
      <button
        class="cat-chip"
        :class="{ active: selectedCategoryId === '' }"
        @click="selectedCategoryId = ''"
      >
        All
      </button>
    </div>

    <!-- Bulk Actions Bar -->
    <div v-if="selectedItems.length > 0" class="bulk-actions">
      <span class="bulk-count">{{ selectedItems.length }} selected</span>
      <button class="btn btn-sm" :disabled="bulkLoading" @click="bulkSetAvailability(true)">Mark Available</button>
      <button class="btn btn-sm" :disabled="bulkLoading" @click="bulkSetAvailability(false)">Mark Sold Out</button>
      <button class="btn btn-sm btn-text" @click="selectedItems = []">Clear</button>
    </div>

    <!-- Items Table -->
    <div class="card" style="padding: 0; overflow: hidden;">
      <div v-if="loading" class="table-loading"><span class="spinner"></span></div>
      <table v-else class="data-table">
        <thead>
          <tr>
            <th style="width: 40px;">
              <input type="checkbox" @change="toggleSelectAll" :checked="isAllSelected" />
            </th>
            <th>Item</th>
            <th>Price (SGD)</th>
            <th>Stock</th>
            <th>Status</th>
            <th>Active</th>
            <th style="width: 100px;">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in filteredItems" :key="item.id">
            <td>
              <input
                type="checkbox"
                :value="item.id"
                v-model="selectedItems"
                @change="handleSelectionChange"
              />
            </td>
            <td>
              <div class="item-name">{{ item.name_en }}</div>
              <div class="item-name-zh">{{ item.name_zh }}</div>
            </td>
            <td>${{ item.price_sgd.toFixed(2) }}</td>
            <td>
              <div class="stock-cell">
                <span v-if="item.stock !== null && item.stock !== undefined">{{ item.stock }}</span>
                <span v-else class="text-muted">∞</span>
                <span v-if="item.is_low_stock" class="stock-warning" title="Low stock">⚠️</span>
              </div>
            </td>
            <td>
              <span class="badge" :class="item.is_available ? 'badge-success' : 'badge-danger'">
                {{ item.is_available ? 'Available' : 'Sold Out' }}
              </span>
            </td>
            <td>
              <span class="badge" :class="item.is_active ? 'badge-success' : 'badge-warning'">
                {{ item.is_active ? 'Yes' : 'No' }}
              </span>
            </td>
            <td>
              <div class="row-actions">
                <button class="btn-icon" title="Edit" @click="openItemModal(item)">✏️</button>
                <button class="btn-icon" title="Toggle availability" @click="toggleAvailability(item)">
                  {{ item.is_available ? '🔴' : '🟢' }}
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="filteredItems.length === 0">
            <td colspan="8" class="empty-state">No items found.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Item Modal -->
    <div v-if="showItemModal" class="modal-overlay" @click.self="showItemModal = false">
      <div class="modal card">
        <h2 class="modal-title">{{ editingItem ? 'Edit Item' : 'New Item' }}</h2>
        <form @submit.prevent="saveItem" class="modal-form">
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Name (EN)</label>
              <input v-model="itemForm.name_en" class="form-input" required />
            </div>
            <div class="form-group">
              <label class="form-label">Name (ZH)</label>
              <input v-model="itemForm.name_zh" class="form-input" required />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Category</label>
              <select v-model="itemForm.category_id" class="form-input" required>
                <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name_en }}</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Price (SGD)</label>
              <input v-model.number="itemForm.price_sgd" type="number" step="0.01" min="0.01" class="form-input" required />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Description (EN)</label>
              <textarea v-model="itemForm.description_en" class="form-input" rows="2"></textarea>
            </div>
            <div class="form-group">
              <label class="form-label">Description (ZH)</label>
              <textarea v-model="itemForm.description_zh" class="form-input" rows="2"></textarea>
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Image URL</label>
              <input v-model="itemForm.image_url" class="form-input" placeholder="https://..." />
            </div>
            <div class="form-group">
              <label class="form-label">Stock (leave empty for unlimited)</label>
              <input v-model.number="itemForm.stock" type="number" min="0" class="form-input" />
            </div>
            <div class="form-group">
              <label class="form-label">Low Stock Alert Threshold</label>
              <input v-model.number="itemForm.low_stock_threshold" type="number" min="0" class="form-input" />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Sort Order</label>
              <input v-model.number="itemForm.sort_order" type="number" class="form-input" />
            </div>
            <div class="form-group" style="display: flex; flex-direction: row; align-items: center; gap: var(--space-4); padding-top: var(--space-6);">
              <label><input type="checkbox" v-model="itemForm.is_available" /> Available</label>
              <label><input type="checkbox" v-model="itemForm.is_active" /> Active</label>
            </div>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn btn-outline" @click="showItemModal = false">Cancel</button>
            <button type="submit" class="btn btn-primary" :disabled="saving">
              <span v-if="saving" class="spinner"></span>
              <span v-else>{{ editingItem ? 'Update' : 'Create' }}</span>
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Category Modal -->
    <div v-if="showCategoryModal" class="modal-overlay" @click.self="showCategoryModal = false">
      <div class="modal card">
        <h2 class="modal-title">New Category</h2>
        <form @submit.prevent="saveCategory" class="modal-form">
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Name (EN)</label>
              <input v-model="catForm.name_en" class="form-input" required />
            </div>
            <div class="form-group">
              <label class="form-label">Name (ZH)</label>
              <input v-model="catForm.name_zh" class="form-input" required />
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Sort Order</label>
            <input v-model.number="catForm.sort_order" type="number" class="form-input" />
          </div>
          <div class="modal-actions">
            <button type="button" class="btn btn-outline" @click="showCategoryModal = false">Cancel</button>
            <button type="submit" class="btn btn-primary" :disabled="saving">
              {{ saving ? 'Saving...' : 'Create' }}
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

interface Category {
  id: string; name_zh: string; name_en: string; sort_order: number; is_active: boolean
}
interface Item {
  id: string; category_id: string; name_zh: string; name_en: string
  description_zh: string | null; description_en: string | null
  price_sgd: number; image_url: string | null; options_config: any
  is_available: boolean; stock: number | null; low_stock_threshold: number
  is_low_stock: boolean; sort_order: number; is_active: boolean
}

const categories = ref<Category[]>([])
const items = ref<Item[]>([])
const loading = ref(true)
const saving = ref(false)
const selectedCategoryId = ref('')
const showItemModal = ref(false)
const showCategoryModal = ref(false)
const editingItem = ref<Item | null>(null)
const selectedItems = ref<string[]>([])
const bulkLoading = ref(false)

const isAllSelected = computed(() =>
  filteredItems.value.length > 0 && selectedItems.value.length === filteredItems.value.length
)

function toggleSelectAll(e: Event) {
  const checked = (e.target as HTMLInputElement).checked
  selectedItems.value = checked ? filteredItems.value.map(i => i.id) : []
}

function handleSelectionChange() {
  // no-op, selectedItems is already updated via v-model
}

async function bulkSetAvailability(available: boolean) {
  if (!selectedItems.value.length) return
  bulkLoading.value = true
  try {
    await Promise.all(
      selectedItems.value.map(id =>
        client.put(`/admin/items/${id}`, { is_available: available })
      )
    )
    selectedItems.value = []
    await fetchData()
  } finally {
    bulkLoading.value = false
  }
}

const itemForm = reactive({
  category_id: '',
  name_en: '', name_zh: '',
  description_en: '', description_zh: '',
  price_sgd: 0, image_url: '',
  stock: null as number | null,
  low_stock_threshold: 5,
  sort_order: 0,
  is_available: true, is_active: true
})

const catForm = reactive({
  name_en: '', name_zh: '', sort_order: 0
})

const filteredItems = computed(() => {
  if (!selectedCategoryId.value) return items.value
  return items.value.filter(i => i.category_id === selectedCategoryId.value)
})

async function fetchData() {
  loading.value = true
  try {
    console.log('[MenuManager] Fetching categories and items...')
    const [catRes, itemRes] = await Promise.all([
      client.get('/admin/categories/'),
      client.get('/admin/items/')
    ])
    console.log('[MenuManager] Categories response:', catRes.data.length, catRes.data)
    console.log('[MenuManager] Items response:', itemRes.data.length, itemRes.data)
    categories.value = catRes.data
    items.value = itemRes.data
  } catch (err: any) {
    console.error('[MenuManager] Fetch error:', err.response?.data || err.message)
  } finally {
    loading.value = false
  }
}

function openItemModal(item?: Item) {
  if (item) {
    editingItem.value = item
    Object.assign(itemForm, {
      category_id: item.category_id,
      name_en: item.name_en, name_zh: item.name_zh,
      description_en: item.description_en || '',
      description_zh: item.description_zh || '',
      price_sgd: item.price_sgd,
      image_url: item.image_url || '',
      stock: item.stock,
      low_stock_threshold: item.low_stock_threshold,
      sort_order: item.sort_order,
      is_available: item.is_available,
      is_active: item.is_active
    })
  } else {
    editingItem.value = null
    Object.assign(itemForm, {
      category_id: categories.value[0]?.id || '',
      name_en: '', name_zh: '',
      description_en: '', description_zh: '',
      price_sgd: 0, image_url: '',
      stock: null, low_stock_threshold: 5, sort_order: 0,
      is_available: true, is_active: true
    })
  }
  showItemModal.value = true
}

async function saveItem() {
  saving.value = true
  try {
    const payload = { ...itemForm }
    if (payload.stock === null || payload.stock === undefined || (payload.stock as any) === '') {
      payload.stock = null
    }
    if (editingItem.value) {
      await client.put(`/admin/items/${editingItem.value.id}`, payload)
    } else {
      await client.post('/admin/items/', payload)
    }
    showItemModal.value = false
    await fetchData()
  } finally {
    saving.value = false
  }
}

async function toggleAvailability(item: Item) {
  await client.put(`/admin/items/${item.id}`, { is_available: !item.is_available })
  await fetchData()
}

async function saveCategory() {
  saving.value = true
  try {
    await client.post('/admin/categories/', catForm)
    showCategoryModal.value = false
    catForm.name_en = ''; catForm.name_zh = ''; catForm.sort_order = 0
    await fetchData()
  } finally {
    saving.value = false
  }
}

onMounted(fetchData)
</script>

<style scoped>
.header-actions {
  display: flex;
  gap: var(--space-3);
}

.categories-bar {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
  margin-bottom: var(--space-5);
}

.cat-chip {
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
.cat-chip:hover { border-color: var(--color-text-muted); color: var(--color-text); }
.cat-chip.active { background: var(--color-primary); border-color: var(--color-primary); color: #fff; }
.cat-chip.inactive { opacity: 0.5; }

.item-name { font-weight: 500; }
.item-name-zh { font-size: var(--font-size-xs); color: var(--color-text-muted); }

.row-actions { display: flex; gap: var(--space-1); }

.text-muted { color: var(--color-text-muted); }
.stock-cell { display: flex; align-items: center; gap: 6px; }
.stock-warning { font-size: 1rem; }

.bulk-actions {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  background: var(--color-primary-soft);
  border: 1px solid var(--color-primary);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-4);
}
.bulk-count { font-weight: 600; color: var(--color-primary); font-size: var(--font-size-sm); flex: 1; }
.btn-sm { padding: var(--space-2) var(--space-3); font-size: var(--font-size-sm); }
.btn-text { background: none; border: none; color: var(--color-text-muted); cursor: pointer; }
.btn-text:hover { color: var(--color-text); }

.table-loading {
  display: flex; justify-content: center; padding: var(--space-10);
}

.empty-state {
  text-align: center; color: var(--color-text-muted); padding: var(--space-10) !important;
}

/* Modal */
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.6); display: flex;
  align-items: center; justify-content: center; z-index: 200;
  backdrop-filter: blur(4px);
}
.modal {
  width: 100%; max-width: 600px; max-height: 90vh; overflow-y: auto;
  animation: fadeIn 0.2s ease;
}
.modal-title { font-size: var(--font-size-xl); font-weight: 600; margin-bottom: var(--space-5); }
.modal-form { display: flex; flex-direction: column; gap: var(--space-4); }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-4); }
.modal-actions { display: flex; justify-content: flex-end; gap: var(--space-3); margin-top: var(--space-4); }

textarea.form-input { resize: vertical; }
</style>
