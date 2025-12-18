<template>
  <div class="coming-soon-page flex flex-column align-items-center justify-content-center h-full text-center">
    <i class="pi pi-compass text-6xl text-primary mb-4"></i>
    <h1 class="text-4xl font-bold mb-2">{{ title }}</h1>
    <p class="text-xl text-600">This feature is coming soon.</p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const title = computed(() => route.name || 'Coming Soon');
</script>

<style scoped>
.coming-soon-page {
    height: calc(100vh - 100px);
}
</style>
