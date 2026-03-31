<template>
  <div class="verify-wrapper">
    <!-- Animated background -->
    <div class="bg-orbs">
      <div class="orb orb-1"></div>
      <div class="orb orb-2"></div>
    </div>

    <div class="verify-card">
      <!-- Logo -->
      <div class="auth-logo">
        <span class="logo-symbol">Ɐ</span>
        <span class="logo-text">Platform<span class="logo-dot">.</span></span>
      </div>

      <!-- Loading State -->
      <div v-if="state === 'loading'" class="state-view">
        <div class="loading-ring">
          <div></div><div></div><div></div><div></div>
        </div>
        <h2 class="state-title">正在驗證您的帳號…</h2>
        <p class="state-desc">請稍候，這只需要一秒鐘。</p>
      </div>

      <!-- Success State -->
      <div v-else-if="state === 'success'" class="state-view">
        <div class="state-icon success-icon">✅</div>
        <h2 class="state-title success">帳號驗證成功！</h2>
        <p class="state-desc">歡迎加入 AI Platform，您的帳號已啟用。</p>
        <p class="state-email">{{ userEmail }}</p>
        <button id="btn-go-login" class="btn btn-primary" @click="goLogin">
          立即登入
        </button>
        <p class="auto-redirect">{{ redirectCountdown }} 秒後自動跳轉…</p>
      </div>

      <!-- Error State -->
      <div v-else-if="state === 'error'" class="state-view">
        <div class="state-icon error-icon">❌</div>
        <h2 class="state-title error">驗證失敗</h2>
        <p class="state-desc">{{ errorMessage }}</p>

        <div class="error-actions">
          <div class="resend-form">
            <label for="resend-email" class="resend-label">重新寄送驗證信：</label>
            <input
              id="resend-email"
              v-model="resendEmail"
              type="email"
              placeholder="your@email.com"
              class="resend-input"
            />
          </div>
          <button
            id="btn-resend"
            class="btn btn-ghost"
            @click="handleResend"
            :disabled="resending || resendCooldown > 0"
          >
            <span v-if="resending" class="spinner"></span>
            <span v-else-if="resendCooldown > 0">重寄（{{ resendCooldown }}s）</span>
            <span v-else>重新寄送驗證信</span>
          </button>
          <div v-if="resendSuccess" class="resend-success">✉️ 驗證信已重新寄出，請至信箱確認。</div>
          <button class="btn btn-link" @click="goLogin">返回登入頁</button>
        </div>
      </div>

      <!-- No Token State -->
      <div v-else class="state-view">
        <div class="state-icon">🔗</div>
        <h2 class="state-title error">連結無效</h2>
        <p class="state-desc">此頁面需要一個有效的驗證連結。<br />請從您的信箱中點擊驗證連結。</p>
        <button class="btn btn-primary" @click="goLogin">回到登入頁</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import apiClient from '../api/client';

const router = useRouter();
const route = useRoute();

type State = 'loading' | 'success' | 'error' | 'no-token';
const state = ref<State>('loading');
const errorMessage = ref('驗證連結無效或已過期，請重新申請驗證信。');
const userEmail = ref('');

// Redirect countdown
const redirectCountdown = ref(5);
let redirectTimer: ReturnType<typeof setInterval> | null = null;

// Resend form
const resendEmail = ref('');
const resending = ref(false);
const resendCooldown = ref(0);
const resendSuccess = ref(false);
let cooldownTimer: ReturnType<typeof setInterval> | null = null;

const goLogin = () => router.push('/login');

const startRedirectTimer = () => {
  redirectTimer = setInterval(() => {
    redirectCountdown.value--;
    if (redirectCountdown.value <= 0) {
      clearInterval(redirectTimer!);
      goLogin();
    }
  }, 1000);
};

const startCooldown = () => {
  resendCooldown.value = 60;
  cooldownTimer = setInterval(() => {
    resendCooldown.value--;
    if (resendCooldown.value <= 0) clearInterval(cooldownTimer!);
  }, 1000);
};

const handleResend = async () => {
  if (!resendEmail.value || resendCooldown.value > 0) return;
  resending.value = true;
  resendSuccess.value = false;
  try {
    await apiClient.post(`/resend-verification?email=${encodeURIComponent(resendEmail.value)}`);
    resendSuccess.value = true;
    startCooldown();
  } catch {
    // API returns generic message anyway
    resendSuccess.value = true;
  } finally {
    resending.value = false;
  }
};

onMounted(async () => {
  const token = route.query.token as string | undefined;

  if (!token) {
    state.value = 'no-token';
    return;
  }

  try {
    const res: any = await apiClient.get(`/verify-email?token=${encodeURIComponent(token)}`);
    userEmail.value = res?.email || '';
    state.value = 'success';
    startRedirectTimer();
  } catch (e: any) {
    const detail = e?.response?.data?.detail || '驗證連結無效或已過期。';
    errorMessage.value = detail;
    state.value = 'error';
  }
});

onUnmounted(() => {
  if (redirectTimer) clearInterval(redirectTimer);
  if (cooldownTimer) clearInterval(cooldownTimer);
});
</script>

<style scoped>
/* ── Layout ── */
.verify-wrapper {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #080810;
  position: relative;
  overflow: hidden;
  font-family: 'Segoe UI', 'Inter', system-ui, sans-serif;
}

/* ── Animated Background ── */
.bg-orbs { position: fixed; inset: 0; pointer-events: none; z-index: 0; }
.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.15;
  animation: float 8s ease-in-out infinite;
}
.orb-1 { width: 600px; height: 600px; background: #4ade80; top: -200px; left: -200px; }
.orb-2 { width: 400px; height: 400px; background: #3b82f6; bottom: -150px; right: -150px; animation-delay: -4s; }
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}

/* ── Card ── */
.verify-card {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 420px;
  margin: 24px;
  background: rgba(18, 18, 28, 0.9);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 20px;
  padding: 36px;
  box-shadow: 0 24px 64px rgba(0,0,0,0.5);
  text-align: center;
}

/* ── Logo ── */
.auth-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-bottom: 32px;
}
.logo-symbol { font-size: 28px; font-weight: 900; color: #fff; }
.logo-text { font-size: 22px; font-weight: 800; color: #f1f5f9; letter-spacing: -0.5px; }
.logo-dot { color: #4ade80; }

/* ── State View ── */
.state-view { display: flex; flex-direction: column; align-items: center; gap: 12px; }

.state-icon { font-size: 56px; animation: popIn 0.6s cubic-bezier(0.34, 1.56, 0.64, 1); }
.success-icon {}
.error-icon {}

@keyframes popIn {
  0% { transform: scale(0); opacity: 0; }
  100% { transform: scale(1); opacity: 1; }
}

.state-title {
  font-size: 20px;
  font-weight: 800;
  color: #f1f5f9;
  margin: 4px 0 0;
}
.state-title.success { color: #4ade80; }
.state-title.error { color: #f87171; }

.state-desc {
  font-size: 14px;
  color: #94a3b8;
  line-height: 1.7;
  margin: 0;
}

.state-email {
  font-size: 14px;
  color: #4ade80;
  font-weight: 600;
  margin: 4px 0;
}

.auto-redirect {
  font-size: 12px;
  color: #475569;
  margin-top: 4px;
}

/* ── Loading Ring ── */
.loading-ring {
  display: inline-block;
  position: relative;
  width: 56px;
  height: 56px;
}
.loading-ring div {
  box-sizing: border-box;
  display: block;
  position: absolute;
  width: 44px;
  height: 44px;
  margin: 6px;
  border: 4px solid transparent;
  border-top-color: #4ade80;
  border-radius: 50%;
  animation: spin 1s cubic-bezier(0.5, 0, 0.5, 1) infinite;
}
.loading-ring div:nth-child(1) { animation-delay: -0.45s; }
.loading-ring div:nth-child(2) { animation-delay: -0.3s; }
.loading-ring div:nth-child(3) { animation-delay: -0.15s; }
@keyframes spin { 0% { transform: rotate(0); } 100% { transform: rotate(360deg); } }

/* ── Error Actions ── */
.error-actions { display: flex; flex-direction: column; gap: 12px; width: 100%; margin-top: 8px; }

.resend-form { display: flex; flex-direction: column; gap: 6px; text-align: left; }
.resend-label { font-size: 13px; color: #64748b; font-weight: 600; }
.resend-input {
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 10px;
  padding: 10px 14px;
  color: #f1f5f9;
  font-size: 14px;
  outline: none;
  width: 100%;
  box-sizing: border-box;
  transition: border-color 0.2s;
}
.resend-input:focus { border-color: rgba(74,222,128,0.5); }
.resend-input::placeholder { color: #475569; }

.resend-success {
  font-size: 13px;
  color: #4ade80;
  background: rgba(74,222,128,0.08);
  border: 1px solid rgba(74,222,128,0.2);
  border-radius: 8px;
  padding: 8px 12px;
}

/* ── Buttons ── */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 24px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 700;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
  width: 100%;
}
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-primary {
  background: linear-gradient(135deg, #4ade80, #22c55e);
  color: #000;
  box-shadow: 0 4px 16px rgba(74,222,128,0.25);
}
.btn-primary:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 6px 24px rgba(74,222,128,0.35); }
.btn-ghost {
  background: rgba(255,255,255,0.05);
  color: #94a3b8;
  border: 1px solid rgba(255,255,255,0.1);
}
.btn-ghost:hover:not(:disabled) { background: rgba(255,255,255,0.08); color: #f1f5f9; }
.btn-link { background: none; color: #64748b; font-size: 13px; padding: 8px; text-decoration: underline; }
.btn-link:hover { color: #4ade80; }

/* ── Spinner ── */
.spinner {
  width: 16px; height: 16px;
  border: 2px solid rgba(0,0,0,0.2);
  border-top-color: #000;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
</style>
