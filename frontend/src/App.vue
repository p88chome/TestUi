<template>
  <router-view />
  <Toast />
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from './stores/auth';
import { useThemeStore } from './stores/theme';
import apiClient from './api/client';
import Toast from 'primevue/toast';

const auth = useAuthStore();
const router = useRouter();
// Initialize theme store globally so CSS variables are available on ALL pages (including login)
useThemeStore();

onMounted(async () => {
  // Restore user session if token exists but user is null (e.g. refresh)
  if (auth.state.token && !auth.state.user) {
    try {
      const userData: any = await apiClient.get('/users/me');
      auth.setUser(userData);
    } catch (e) {
      console.error('Failed to restore session - clearing stale token', e);
      auth.logout();
      // Ensure we go to login if we were on a protected route
      if (window.location.pathname !== '/login' && window.location.pathname !== '/verify-email') {
        router.push('/login');
      }
    }
  }
});
</script>

<style>
body {
  margin: 0;
  font-family: 'Inter', sans-serif;
  background-color: #f5f7fa;
  color: #1f2937;
}
</style>
