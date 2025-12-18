<template>
  <header class="topbar">
    <div class="breadcrumbs">
      {{ route.name }}
    </div>
    <div class="actions">
      <!-- Actions moved to Sidebar or specific page controls -->
    </div>
  </header>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router';
const route = useRoute();
</script>

<style scoped>
.topbar {
  height: 64px;
  background-color: var(--brand-white);
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}

.breadcrumbs {
  font-size: 0.875rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.breadcrumbs::before {
  content: '';
  display: inline-block;
  width: 8px;
  height: 8px;
  background-color: var(--brand-green);
  border-radius: 50%;
  margin-right: 8px;
}
</style>
