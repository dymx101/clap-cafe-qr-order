<script setup lang="ts">
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps<{
  visible: boolean
  orderId?: string
}>()

const emit = defineEmits<{
  close: []
  confirm: [reason: string]
}>()

const selectedReason = ref('')

const reasons = [
  { value: 'sold_out', labelKey: 'kds.reject.soldOut' },
  { value: 'busy', labelKey: 'kds.reject.busy' },
  { value: 'other', labelKey: 'kds.reject.other' }
]

watch(() => props.visible, (val) => {
  if (!val) {
    selectedReason.value = ''
  }
})

function handleConfirm() {
  if (selectedReason.value) {
    emit('confirm', selectedReason.value)
  }
}
</script>

<template>
  <Teleport to="body">
    <div v-if="visible" class="modal-overlay" @click.self="emit('close')">
      <div class="modal">
        <div class="modal-header">
          <h3>{{ t('kds.reject.title') }}</h3>
          <button class="close-btn" @click="emit('close')">✕</button>
        </div>

        <div class="modal-body">
          <label
            v-for="reason in reasons"
            :key="reason.value"
            class="reason-option"
          >
            <input
              type="radio"
              :value="reason.value"
              v-model="selectedReason"
            />
            <span class="radio-circle"></span>
            <span class="reason-label">{{ t(reason.labelKey) }}</span>
          </label>
        </div>

        <div class="modal-footer">
          <button class="btn-cancel" @click="emit('close')">{{ t('common.cancel') }}</button>
          <button
            class="btn-confirm"
            :disabled="!selectedReason"
            @click="handleConfirm"
          >
            {{ t('kds.reject.confirm') }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: #1e1e2e;
  border-radius: 16px;
  width: 90%;
  max-width: 400px;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #374151;
}

.modal-header h3 {
  margin: 0;
  font-size: 20px;
  color: #f3f4f6;
}

.close-btn {
  background: none;
  border: none;
  color: #9ca3af;
  font-size: 24px;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.modal-body {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.reason-option {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  padding: 12px 16px;
  background: #2a2a3e;
  border-radius: 8px;
  transition: background 0.2s;
}

.reason-option:hover {
  background: #374151;
}

.reason-option input {
  display: none;
}

.radio-circle {
  width: 20px;
  height: 20px;
  border: 2px solid #6b7280;
  border-radius: 50%;
  position: relative;
  transition: border-color 0.2s;
}

.reason-option input:checked + .radio-circle {
  border-color: #ef4444;
}

.reason-option input:checked + .radio-circle::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 10px;
  height: 10px;
  background: #ef4444;
  border-radius: 50%;
}

.reason-label {
  color: #f3f4f6;
  font-size: 16px;
}

.modal-footer {
  display: flex;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid #374151;
}

.btn-cancel,
.btn-confirm {
  flex: 1;
  padding: 14px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
}

.btn-cancel {
  background: #374151;
  color: #f3f4f6;
}

.btn-confirm {
  background: #ef4444;
  color: white;
}

.btn-confirm:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
