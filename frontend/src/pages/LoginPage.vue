<template>
  <div class="auth-wrapper">
    <!-- Animated background -->
    <div class="bg-orbs">
      <div class="orb orb-1"></div>
      <div class="orb orb-2"></div>
      <div class="orb orb-3"></div>
    </div>

    <div class="auth-card">
      <!-- Logo -->
      <div class="auth-logo">
        <span class="logo-symbol">Ɐ</span>
        <span class="logo-text">Platform<span class="logo-dot">.</span></span>
      </div>

      <!-- ═══ SUCCESS STATE: Email Sent ═══ -->
      <transition name="fade-slide" mode="out-in">
        <div v-if="currentView === 'email-sent'" key="sent" class="success-view">
          <div class="success-icon">✉️</div>
          <h2 class="success-title">驗證信已寄出！</h2>
          <p class="success-desc">
            我們已將驗證連結寄至<br />
            <strong class="highlight-email">{{ registeredEmail }}</strong>
          </p>
          <p class="success-hint">請至信箱點擊連結完成帳號驗證（有效期 24 小時）。</p>

          <div class="success-actions">
            <button class="btn btn-ghost" @click="handleResend" :disabled="resendCooldown > 0">
              <span v-if="resendCooldown > 0">重寄（{{ resendCooldown }}s）</span>
              <span v-else>重新寄送驗證信</span>
            </button>
            <button class="btn btn-primary" @click="switchView('login')">
              前往登入
            </button>
          </div>
        </div>

        <!-- ═══ LOGIN / REGISTER VIEWS ═══ -->
        <div v-else key="auth" class="auth-views">
          <!-- Tab Switch -->
          <div class="tab-bar" role="tablist">
            <button
              id="tab-login"
              role="tab"
              :aria-selected="currentView === 'login'"
              class="tab-btn"
              :class="{ active: currentView === 'login' }"
              @click="switchView('login')"
            >登入</button>
            <button
              id="tab-register"
              role="tab"
              :aria-selected="currentView === 'register'"
              class="tab-btn"
              :class="{ active: currentView === 'register' }"
              @click="switchView('register')"
            >註冊</button>
            <div class="tab-indicator" :class="{ right: currentView === 'register' }"></div>
          </div>

          <!-- Error Banner -->
          <transition name="shake">
            <div v-if="error" class="error-banner" role="alert">
              <span class="error-icon">⚠️</span>
              <span>{{ error }}</span>
            </div>
          </transition>

          <!-- ── LOGIN FORM ── -->
          <transition name="slide-tab" mode="out-in">
            <form v-if="currentView === 'login'" key="login" @submit.prevent="handleLogin" class="auth-form" novalidate>
              <div class="field-group">
                <label for="login-email">Email</label>
                <input
                  id="login-email"
                  v-model="loginEmail"
                  type="email"
                  placeholder="name@company.com"
                  autocomplete="email"
                  required
                  :class="{ invalid: error }"
                />
              </div>

              <div class="field-group">
                <label for="login-password">密碼</label>
                <div class="password-wrapper">
                  <input
                    id="login-password"
                    v-model="loginPassword"
                    :type="showLoginPw ? 'text' : 'password'"
                    placeholder="••••••••"
                    autocomplete="current-password"
                    required
                    :class="{ invalid: error }"
                  />
                  <button type="button" class="pw-toggle" @click="showLoginPw = !showLoginPw" :aria-label="showLoginPw ? '隱藏密碼' : '顯示密碼'">
                    {{ showLoginPw ? '🙈' : '👁️' }}
                  </button>
                </div>
              </div>

              <button id="btn-login" type="submit" class="btn btn-primary w-full" :disabled="loading">
                <span v-if="loading" class="spinner"></span>
                <span v-else>登入</span>
              </button>

              <div class="form-footer">
                還沒有帳號？
                <button type="button" class="link-btn" @click="switchView('register')">立即註冊</button>
              </div>
            </form>

            <!-- ── REGISTER FORM ── -->
            <form v-else key="register" @submit.prevent="handleRegister" class="auth-form" novalidate>
              <div class="field-group">
                <label for="reg-name">全名</label>
                <input
                  id="reg-name"
                  v-model="regName"
                  type="text"
                  placeholder="王小明"
                  autocomplete="name"
                  required
                  :class="{ invalid: fieldErrors.name }"
                />
                <span v-if="fieldErrors.name" class="field-error">{{ fieldErrors.name }}</span>
              </div>

              <div class="field-group">
                <label for="reg-email">Email</label>
                <input
                  id="reg-email"
                  v-model="regEmail"
                  type="email"
                  placeholder="name@company.com"
                  autocomplete="email"
                  required
                  :class="{ invalid: fieldErrors.email }"
                />
                <span v-if="fieldErrors.email" class="field-error">{{ fieldErrors.email }}</span>
              </div>

              <div class="field-group">
                <label for="reg-password">密碼</label>
                <div class="password-wrapper">
                  <input
                    id="reg-password"
                    v-model="regPassword"
                    :type="showRegPw ? 'text' : 'password'"
                    placeholder="至少 8 字元，含字母與數字"
                    autocomplete="new-password"
                    required
                    :class="{ invalid: fieldErrors.password }"
                    @input="checkPasswordStrength"
                  />
                  <button type="button" class="pw-toggle" @click="showRegPw = !showRegPw" :aria-label="showRegPw ? '隱藏密碼' : '顯示密碼'">
                    {{ showRegPw ? '🙈' : '👁️' }}
                  </button>
                </div>
                <!-- Password Strength Indicator -->
                <div v-if="regPassword" class="pw-strength">
                  <div class="pw-strength-bar">
                    <div class="pw-strength-fill" :class="pwStrengthClass" :style="{ width: pwStrengthWidth }"></div>
                  </div>
                  <span class="pw-strength-label" :class="pwStrengthClass">{{ pwStrengthLabel }}</span>
                </div>
                <span v-if="fieldErrors.password" class="field-error">{{ fieldErrors.password }}</span>
              </div>

              <div class="field-group">
                <label for="reg-confirm">確認密碼</label>
                <div class="password-wrapper">
                  <input
                    id="reg-confirm"
                    v-model="regConfirm"
                    :type="showConfirmPw ? 'text' : 'password'"
                    placeholder="再次輸入密碼"
                    autocomplete="new-password"
                    required
                    :class="{ invalid: fieldErrors.confirm }"
                  />
                  <button type="button" class="pw-toggle" @click="showConfirmPw = !showConfirmPw" :aria-label="showConfirmPw ? '隱藏密碼' : '顯示密碼'">
                    {{ showConfirmPw ? '🙈' : '👁️' }}
                  </button>
                </div>
                <span v-if="fieldErrors.confirm" class="field-error">{{ fieldErrors.confirm }}</span>
              </div>

              <button id="btn-register" type="submit" class="btn btn-primary w-full" :disabled="loading">
                <span v-if="loading" class="spinner"></span>
                <span v-else>建立帳號</span>
              </button>

              <div class="form-footer">
                已有帳號？
                <button type="button" class="link-btn" @click="switchView('login')">直接登入</button>
              </div>
            </form>
          </transition>
        </div>
      </transition>

      <!-- Debug Info (remove in production) -->
      <div v-if="isDev" class="debug-bar">API: {{ apiUrl }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import apiClient from '../api/client';

const router = useRouter();
const auth = useAuthStore();

// ── State ──────────────────────────────────────────────────────────────────
type View = 'login' | 'register' | 'email-sent';
const currentView = ref<View>('login');
const loading = ref(false);
const error = ref('');
const registeredEmail = ref('');
const resendCooldown = ref(0);
let cooldownTimer: ReturnType<typeof setInterval> | null = null;

// Login fields
const loginEmail = ref('');
const loginPassword = ref('');
const showLoginPw = ref(false);

// Register fields
const regName = ref('');
const regEmail = ref('');
const regPassword = ref('');
const regConfirm = ref('');
const showRegPw = ref(false);
const showConfirmPw = ref(false);
const fieldErrors = reactive({ name: '', email: '', password: '', confirm: '' });

// Misc
const apiUrl = import.meta.env.VITE_API_URL || '(Default /api/v1)';
const isDev = import.meta.env.DEV;

// ── Helpers ────────────────────────────────────────────────────────────────
const switchView = (view: View) => {
  error.value = '';
  Object.keys(fieldErrors).forEach(k => (fieldErrors as any)[k] = '');
  currentView.value = view;
};

// ── Password Strength ──────────────────────────────────────────────────────
const pwScore = ref(0);

const checkPasswordStrength = () => {
  const p = regPassword.value;
  let score = 0;
  if (p.length >= 8) score++;
  if (p.length >= 12) score++;
  if (/[A-Z]/.test(p)) score++;
  if (/\d/.test(p)) score++;
  if (/[^A-Za-z0-9]/.test(p)) score++;
  pwScore.value = score;
};

const pwStrengthClass = computed(() => {
  if (pwScore.value <= 1) return 'weak';
  if (pwScore.value <= 3) return 'fair';
  return 'strong';
});
const pwStrengthWidth = computed(() => `${(pwScore.value / 5) * 100}%`);
const pwStrengthLabel = computed(() => {
  if (pwScore.value <= 1) return '弱';
  if (pwScore.value <= 3) return '中等';
  return '強';
});

// ── Login Handler ──────────────────────────────────────────────────────────
const handleLogin = async () => {
  if (!loginEmail.value || !loginPassword.value) {
    error.value = '請填寫 Email 和密碼';
    return;
  }
  loading.value = true;
  error.value = '';
  try {
    const params = new URLSearchParams();
    params.append('username', loginEmail.value);
    params.append('password', loginPassword.value);

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
    const detail = e?.response?.data?.detail || e.message || '登入失敗，請稍後再試';
    error.value = detail;
  } finally {
    loading.value = false;
  }
};

// ── Register Handler ───────────────────────────────────────────────────────
const validateRegister = (): boolean => {
  let valid = true;
  fieldErrors.name = '';
  fieldErrors.email = '';
  fieldErrors.password = '';
  fieldErrors.confirm = '';

  if (!regName.value.trim()) {
    fieldErrors.name = '請填寫姓名';
    valid = false;
  }
  if (!regEmail.value || !/\S+@\S+\.\S+/.test(regEmail.value)) {
    fieldErrors.email = '請輸入有效的 Email 地址';
    valid = false;
  }
  if (regPassword.value.length < 8) {
    fieldErrors.password = '密碼需至少 8 個字元';
    valid = false;
  } else if (!/[A-Za-z]/.test(regPassword.value) || !/\d/.test(regPassword.value)) {
    fieldErrors.password = '密碼需包含至少一個英文字母與一個數字';
    valid = false;
  }
  if (regPassword.value !== regConfirm.value) {
    fieldErrors.confirm = '兩次輸入的密碼不一致';
    valid = false;
  }
  return valid;
};

const handleRegister = async () => {
  if (!validateRegister()) return;
  loading.value = true;
  error.value = '';
  try {
    await apiClient.post('/register', {
      email: regEmail.value,
      password: regPassword.value,
      full_name: regName.value.trim(),
    });
    registeredEmail.value = regEmail.value;
    switchView('email-sent');
    startResendCooldown();
  } catch (e: any) {
    const detail = e?.response?.data?.detail || e.message || '註冊失敗，請稍後再試';
    error.value = detail;
  } finally {
    loading.value = false;
  }
};

// ── Resend Verification ────────────────────────────────────────────────────
const startResendCooldown = () => {
  resendCooldown.value = 60;
  cooldownTimer = setInterval(() => {
    resendCooldown.value--;
    if (resendCooldown.value <= 0 && cooldownTimer) {
      clearInterval(cooldownTimer);
      cooldownTimer = null;
    }
  }, 1000);
};

const handleResend = async () => {
  if (resendCooldown.value > 0) return;
  try {
    await apiClient.post(`/resend-verification?email=${encodeURIComponent(registeredEmail.value)}`);
    startResendCooldown();
  } catch (e) {
    // Silent fail (API already returns generic message)
  }
};

onUnmounted(() => {
  if (cooldownTimer) clearInterval(cooldownTimer);
});
</script>

<style scoped>
/* ── Layout ── */
.auth-wrapper {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #080810;
  position: relative;
  overflow: hidden;
  font-family: 'Segoe UI', 'Inter', system-ui, sans-serif;
}

/* ── Animated Background Orbs ── */
.bg-orbs { position: fixed; inset: 0; pointer-events: none; z-index: 0; }
.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.18;
  animation: float 8s ease-in-out infinite;
}
.orb-1 { width: 500px; height: 500px; background: #4ade80; top: -150px; left: -150px; animation-delay: 0s; }
.orb-2 { width: 400px; height: 400px; background: #3b82f6; bottom: -100px; right: -100px; animation-delay: -3s; }
.orb-3 { width: 300px; height: 300px; background: #a855f7; top: 50%; left: 50%; transform: translate(-50%,-50%); animation-delay: -6s; }
@keyframes float {
  0%, 100% { transform: translateY(0) scale(1); }
  50% { transform: translateY(-30px) scale(1.05); }
}

/* ── Card ── */
.auth-card {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 420px;
  margin: 24px;
  background: rgba(18, 18, 28, 0.85);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 20px;
  padding: 36px 36px 28px;
  box-shadow: 0 24px 64px rgba(0,0,0,0.5), 0 0 0 1px rgba(255,255,255,0.04) inset;
}

/* ── Logo ── */
.auth-logo {
  text-align: center;
  margin-bottom: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}
.logo-symbol { font-size: 28px; font-weight: 900; color: #fff; }
.logo-text { font-size: 22px; font-weight: 800; color: #f1f5f9; letter-spacing: -0.5px; }
.logo-dot { color: #4ade80; }

/* ── Tab Bar ── */
.tab-bar {
  display: flex;
  background: rgba(255,255,255,0.04);
  border-radius: 10px;
  padding: 4px;
  margin-bottom: 24px;
  position: relative;
}
.tab-btn {
  flex: 1;
  padding: 9px;
  background: transparent;
  border: none;
  color: #64748b;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  border-radius: 8px;
  transition: color 0.25s;
  position: relative;
  z-index: 1;
}
.tab-btn.active { color: #f1f5f9; }
.tab-indicator {
  position: absolute;
  top: 4px; bottom: 4px; left: 4px;
  width: calc(50% - 4px);
  background: rgba(74, 222, 128, 0.12);
  border: 1px solid rgba(74, 222, 128, 0.25);
  border-radius: 8px;
  transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.tab-indicator.right { transform: translateX(100%); }

/* ── Forms ── */
.auth-form { display: flex; flex-direction: column; gap: 16px; }

.field-group { display: flex; flex-direction: column; gap: 6px; }
.field-group label {
  font-size: 13px;
  font-weight: 600;
  color: #94a3b8;
  letter-spacing: 0.3px;
}

.field-group input {
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 10px;
  padding: 11px 14px;
  color: #f1f5f9;
  font-size: 14px;
  transition: border-color 0.2s, box-shadow 0.2s;
  outline: none;
  width: 100%;
  box-sizing: border-box;
}
.field-group input::placeholder { color: #475569; }
.field-group input:focus {
  border-color: rgba(74, 222, 128, 0.5);
  box-shadow: 0 0 0 3px rgba(74, 222, 128, 0.08);
}
.field-group input.invalid { border-color: rgba(248, 113, 113, 0.6); }

.password-wrapper { position: relative; }
.password-wrapper input { padding-right: 44px; }
.pw-toggle {
  position: absolute;
  right: 12px; top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
  padding: 0;
  line-height: 1;
  opacity: 0.6;
  transition: opacity 0.2s;
}
.pw-toggle:hover { opacity: 1; }

.field-error {
  font-size: 12px;
  color: #f87171;
  margin-top: 2px;
}

/* ── Password Strength ── */
.pw-strength { display: flex; align-items: center; gap: 8px; margin-top: 6px; }
.pw-strength-bar { flex: 1; height: 4px; background: rgba(255,255,255,0.06); border-radius: 4px; overflow: hidden; }
.pw-strength-fill { height: 100%; border-radius: 4px; transition: width 0.3s ease, background 0.3s ease; }
.pw-strength-fill.weak { background: #f87171; }
.pw-strength-fill.fair { background: #fbbf24; }
.pw-strength-fill.strong { background: #4ade80; }
.pw-strength-label { font-size: 11px; font-weight: 600; min-width: 24px; }
.pw-strength-label.weak { color: #f87171; }
.pw-strength-label.fair { color: #fbbf24; }
.pw-strength-label.strong { color: #4ade80; }

/* ── Buttons ── */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 20px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 700;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-primary {
  background: linear-gradient(135deg, #4ade80, #22c55e);
  color: #000;
  box-shadow: 0 4px 16px rgba(74, 222, 128, 0.25);
}
.btn-primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 24px rgba(74, 222, 128, 0.35);
}
.btn-ghost {
  background: rgba(255,255,255,0.05);
  color: #94a3b8;
  border: 1px solid rgba(255,255,255,0.1);
}
.btn-ghost:hover:not(:disabled) { background: rgba(255,255,255,0.08); color: #f1f5f9; }
.w-full { width: 100%; }

/* ── Spinner ── */
.spinner {
  width: 16px; height: 16px;
  border: 2px solid rgba(0,0,0,0.2);
  border-top-color: #000;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Error Banner ── */
.error-banner {
  background: rgba(248, 113, 113, 0.08);
  border: 1px solid rgba(248, 113, 113, 0.25);
  border-radius: 10px;
  padding: 10px 14px;
  font-size: 13px;
  color: #fca5a5;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* ── Form Footer ── */
.form-footer {
  text-align: center;
  font-size: 13px;
  color: #64748b;
  margin-top: 4px;
}
.link-btn {
  background: none;
  border: none;
  color: #4ade80;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  padding: 0;
  text-decoration: underline;
  text-underline-offset: 2px;
}
.link-btn:hover { color: #86efac; }

/* ── Success View ── */
.success-view { text-align: center; padding: 8px 0; }
.success-icon { font-size: 52px; margin-bottom: 16px; animation: bounce 0.6s ease; }
@keyframes bounce {
  0% { transform: scale(0.5); opacity: 0; }
  70% { transform: scale(1.1); }
  100% { transform: scale(1); opacity: 1; }
}
.success-title { font-size: 20px; font-weight: 800; color: #f1f5f9; margin: 0 0 12px; }
.success-desc { font-size: 14px; color: #94a3b8; line-height: 1.7; margin: 0 0 8px; }
.highlight-email { color: #4ade80; font-size: 14px; }
.success-hint { font-size: 12px; color: #475569; margin: 0 0 24px; }
.success-actions { display: flex; flex-direction: column; gap: 10px; }

/* ── Debug Bar ── */
.debug-bar {
  margin-top: 20px;
  padding: 8px 12px;
  background: rgba(255,255,255,0.03);
  border-radius: 8px;
  font-size: 11px;
  color: #374151;
  text-align: center;
}

/* ── Transitions ── */
.slide-tab-enter-active,
.slide-tab-leave-active { transition: all 0.25s ease; }
.slide-tab-enter-from { opacity: 0; transform: translateX(16px); }
.slide-tab-leave-to { opacity: 0; transform: translateX(-16px); }

.fade-slide-enter-active,
.fade-slide-leave-active { transition: all 0.3s ease; }
.fade-slide-enter-from { opacity: 0; transform: translateY(12px); }
.fade-slide-leave-to { opacity: 0; transform: translateY(-12px); }

.shake-enter-active { animation: shake 0.4s ease; }
@keyframes shake {
  0%, 100% { transform: translateX(0); }
  20% { transform: translateX(-6px); }
  40% { transform: translateX(6px); }
  60% { transform: translateX(-4px); }
  80% { transform: translateX(4px); }
}
</style>
