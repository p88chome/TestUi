<template>
  <div class="layout">
    <Sidebar />
    <div class="main-content">
      <Topbar />
      <main class="page-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useThemeStore } from '../stores/theme';
import Sidebar from './Sidebar.vue';
import Topbar from './Topbar.vue';

const themeStore = useThemeStore();

onMounted(() => {
  // Initialize theme (injects CSS variables)
  // In a real multi-tenant app, we would fetch the tenant config here
  // and call themeStore.setTheme(tenantTheme)
  console.log(`Theme initialized: ${themeStore.currentTheme.name}`);
});
</script>

<style scoped>
.layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
  background-color: var(--color-bg); /* Use theme bg */
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.page-content {
  flex: 1;
  overflow-y: auto;
  /* padding: 24px; Handled by individual pages for full control */
}
</style>
