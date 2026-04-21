import axios from 'axios';
import router from '../router';
import { useAuthStore } from '../stores/auth';

const apiClient = axios.create({
  baseURL: '/api/v1'
});

apiClient.interceptors.request.use((config: any) => {
  const token = sessionStorage.getItem('token');
  if (token) {
    config.headers = config.headers || {};
    (config.headers as any).Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response: any) => response.data,
  (error: any) => {
    if (error.response && error.response.status === 401) {
      try {
        useAuthStore().logout();
      } catch {
        sessionStorage.removeItem('token');
      }
      if (router.currentRoute.value.path !== '/login') {
        router.push('/login');
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;
