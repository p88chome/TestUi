<template>
  <router-view />
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useAuthStore } from './stores/auth';
import axios from 'axios';

const auth = useAuthStore();

onMounted(async () => {
  // Restore user session if token exists but user is null (e.g. refresh)
  if (auth.state.token && !auth.state.user) {
    try {
      const res = await axios.get('/api/v1/users/me', {
        headers: { Authorization: `Bearer ${auth.state.token}` }
      });
      auth.setUser(res.data);
    } catch (e) {
      console.error('Failed to restore session', e);
      // Optional: auth.logout() if token is invalid
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
