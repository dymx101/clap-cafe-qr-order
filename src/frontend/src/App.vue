<template>
  <RouterView />
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: #F5F0E8;
  color: #3D2B1F;
  -webkit-font-smoothing: antialiased;
}
button { font-family: inherit; }
img { max-width: 100%; }
</style>
