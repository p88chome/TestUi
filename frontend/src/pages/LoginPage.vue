<template>
  <div class="login-page flex align-items-center justify-content-center min-h-screen bg-black-alpha-90">
    <div class="login-card surface-card p-4 shadow-8 border-round w-full max-w-sm">
      <div class="text-center mb-5">
        <h1 class="text-2xl font-bold mb-1 text-900">
          Ɐ Platform <span class="text-green-500">.</span>
        </h1>
        <p class="text-600 font-medium">Sign in to continue</p>
      </div>

      <form @submit.prevent="handleLogin" class="flex flex-column gap-3">
        <div class="flex flex-column gap-2">
          <label for="email" class="font-semibold text-900">Email</label>
          <InputText
            id="email"
            v-model="email"
            class="w-full"
            :class="{ 'p-invalid': error }"
            placeholder="name@company.com"
          />
        </div>

        <div class="flex flex-column gap-2">
          <label for="password" class="font-semibold text-900">Password</label>
          <Password
            id="password"
            v-model="password"
            class="w-full"
            :inputClass="'w-full'"
            :class="{ 'p-invalid': error }"
            toggleMask
            :feedback="false"
            placeholder="••••••••"
          />
        </div>

        <div v-if="error" class="text-red-500 text-sm py-2">
          {{ error }}
        </div>

        <Button label="Sign In" type="submit" class="w-full mt-2" :loading="loading" />

        <div class="text-center mt-3 text-sm text-600">
          Contact IT for access
        </div>
        
        <!-- DEBUG INFO: REMOVE IN PRODUCTION -->
        <div class="mt-4 p-2 surface-100 text-xs text-400 border-round">
            API: {{ apiUrl }}
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import InputText from 'primevue/inputtext';
import Password from 'primevue/password';
import Button from 'primevue/button';
import { useAuthStore } from '../stores/auth';
import apiClient from '../api/client';

const router = useRouter();
const auth = useAuthStore();

const email = ref('');
const password = ref('');
const loading = ref(false);
const error = ref('');
const apiUrl = import.meta.env.VITE_API_URL || '(Default /api/v1)';

const handleLogin = async () => {
  loading.value = true;
  error.value = '';
  try {
    const params = new URLSearchParams();
    params.append('username', email.value);
    params.append('password', password.value);

    // 使用共用的 apiClient，會自動用 VITE_API_URL + /api/v1 當 baseURL
    const res: any = await apiClient.post('/login/access-token', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });

    const { access_token } = res;
    auth.setToken(access_token);

    const userRes: any = await apiClient.get('/users/me', {
      headers: { Authorization: `Bearer ${access_token}` },
    });
    auth.setUser(userRes);

    router.push('/dashboard');
  } catch (e: any) {
    console.error(e);
    // DEBUG: Show detailed error to help user
    const detailedError = e?.response?.data?.detail || e.message || 'Unknown Error';
    error.value = `Login failed: ${detailedError}`;
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.login-page {
  background-color: var(--brand-black);
}
</style>
