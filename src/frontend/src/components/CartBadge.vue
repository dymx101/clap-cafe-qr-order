<template>
  <button class="cart-badge" @click="$emit('click')">
    🛒
    <span class="count">{{ count }}</span>
  </button>
</template>

<script setup lang="ts">
defineProps<{ count: number }>()
defineEmits<{ click: [] }>()
</script>

<style scoped>
.cart-badge {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: #D4A574;
  border: none;
  font-size: 24px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(212,165,116,0.4);
  position: relative;
}
.count {
  position: absolute;
  top: -2px;
  right: -2px;
  background: #e74c3c;
  color: #fff;
  font-size: 11px;
  font-weight: bold;
  min-width: 18px;
  height: 18px;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
}
</style>
