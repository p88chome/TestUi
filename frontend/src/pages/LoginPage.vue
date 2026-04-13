<template>
  <div class="auth-wrapper">
    <!-- Left Branding Panel -->
    <div class="brand-panel">
      <div class="brand-content">
        <div class="brand-logo">
          <span class="brand-symbol">Ɐ</span>
          <span class="brand-name">Platform<span class="brand-dot">.</span></span>
        </div>
        <div class="brand-tagline">
          <h1>Enterprise AI<br />Powered by Deloitte</h1>
          <p>Intelligent workflows, models, and analytics — built for your organization.</p>
        </div>
        <div class="brand-features">
          <div class="brand-feature"><span class="feature-dot"></span>Multi-model AI orchestration</div>
          <div class="brand-feature"><span class="feature-dot"></span>Enterprise-grade security</div>
          <div class="brand-feature"><span class="feature-dot"></span>Real-time cost analytics</div>
        </div>
      </div>
      <div class="brand-footer">© {{ new Date().getFullYear() }} Deloitte. All rights reserved.</div>
    </div>

    <!-- Right Form Panel -->
    <div class="form-panel">
    <div class="auth-card">
      <!-- Logo (mobile only) -->
      <div class="auth-logo">
        <span class="logo-symbol">Ɐ</span>
        <span class="logo-text">Platform<span class="logo-dot">.</span></span>
      </div>

      <!-- Card heading -->
      <div class="card-heading">
        <h2 class="card-title">{{ currentView === 'register' ? '建立帳號' : currentView === 'email-sent' ? '確認信箱' : '歡迎回來' }}</h2>
        <p class="card-subtitle">{{ currentView === 'register' ? '加入 AI 平台，開始使用企業 AI 工具' : currentView === 'email-sent' ? '' : '登入以繼續使用平台' }}</p>
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
    </div><!-- /form-panel -->
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
/* ── Layout: Split Panel ── */
.auth-wrapper {
  min-height: 100vh;
  display: flex;
  font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
  background: #F4F4F4;
}

/* ── Left: Brand Panel ── */
.brand-panel {
  width: 480px;
  min-height: 100vh;
  background: #000000;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 48px 52px;
  flex-shrink: 0;
  position: relative;
  overflow: hidden;
}

/* Subtle green accent line at top */
.brand-panel::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: #86BC25;
}

.brand-content {
  display: flex;
  flex-direction: column;
  gap: 52px;
}

.brand-logo {
  display: flex;
  align-items: center;
  gap: 10px;
}
.brand-symbol {
  font-size: 32px;
  font-weight: 900;
  color: #ffffff;
  line-height: 1;
}
.brand-name {
  font-size: 24px;
  font-weight: 800;
  color: #ffffff;
  letter-spacing: -0.5px;
}
.brand-dot { color: #86BC25; }

.brand-tagline h1 {
  font-size: 36px;
  font-weight: 700;
  color: #ffffff;
  line-height: 1.2;
  margin: 0 0 16px;
  letter-spacing: -0.5px;
}
.brand-tagline p {
  font-size: 15px;
  color: #888888;
  line-height: 1.7;
  margin: 0;
}

.brand-features {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.brand-feature {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  color: #aaaaaa;
  font-weight: 500;
}
.feature-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #86BC25;
  flex-shrink: 0;
}

.brand-footer {
  font-size: 12px;
  color: #444444;
}

/* ── Right: Form Panel ── */
.form-panel {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 24px;
  background: #F4F5F7;
}

/* ── Card ── */
.auth-card {
  width: 100%;
  max-width: 420px;
  background: #ffffff;
  border: 1px solid #E5E5E5;
  border-radius: 4px;
  padding: 40px 36px 32px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

/* ── Logo (inside card, shown on mobile only via hidden on desktop) ── */
.auth-logo {
  display: none; /* Hidden: brand panel shows logo on desktop */
  text-align: center;
  margin-bottom: 28px;
  align-items: center;
  justify-content: center;
  gap: 8px;
}
.logo-symbol { font-size: 26px; font-weight: 900; color: #000; }
.logo-text { font-size: 20px; font-weight: 800; color: #000; letter-spacing: -0.5px; }
.logo-dot { color: #86BC25; }

/* Card heading */
.card-heading { margin-bottom: 24px; }
.card-title {
  font-size: 22px;
  font-weight: 700;
  color: #000000;
  margin: 0 0 4px;
  letter-spacing: -0.3px;
}
.card-subtitle {
  font-size: 13px;
  color: #666666;
  margin: 0;
}

/* ── Tab Bar ── */
.tab-bar {
  display: flex;
  background: #F4F4F4;
  border: 1px solid #E5E5E5;
  border-radius: 2px;
  padding: 3px;
  margin-bottom: 24px;
  position: relative;
}
.tab-btn {
  flex: 1;
  padding: 9px;
  background: transparent;
  border: none;
  color: #666666;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  border-radius: 1px;
  transition: color 0.2s;
  position: relative;
  z-index: 1;
}
.tab-btn.active { color: #000000; }
.tab-indicator {
  position: absolute;
  top: 3px; bottom: 3px; left: 3px;
  width: calc(50% - 3px);
  background: #ffffff;
  border: 1px solid #E5E5E5;
  border-radius: 1px;
  transition: transform 0.25s ease;
}
.tab-indicator.right { transform: translateX(100%); }

/* ── Forms ── */
.auth-form { display: flex; flex-direction: column; gap: 16px; }

.field-group { display: flex; flex-direction: column; gap: 6px; }
.field-group label {
  font-size: 12px;
  font-weight: 600;
  color: #2C2C2C;
  letter-spacing: 0.5px;
  text-transform: uppercase;
}

.field-group input {
  background: #ffffff;
  border: 1px solid #D0D0D0;
  border-radius: 2px;
  padding: 11px 14px;
  color: #000000;
  font-size: 14px;
  transition: border-color 0.2s, box-shadow 0.2s;
  outline: none;
  width: 100%;
  box-sizing: border-box;
}
.field-group input::placeholder { color: #AAAAAA; }
.field-group input:focus {
  border-color: #86BC25;
  box-shadow: 0 0 0 2px rgba(134, 188, 37, 0.12);
}
.field-group input.invalid { border-color: #D0021B; }

.password-wrapper { position: relative; }
.password-wrapper input { padding-right: 44px; }
.pw-toggle {
  position: absolute;
  right: 12px; top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  font-size: 15px;
  padding: 0;
  line-height: 1;
  opacity: 0.5;
  transition: opacity 0.2s;
}
.pw-toggle:hover { opacity: 0.9; }

.field-error {
  font-size: 12px;
  color: #D0021B;
  margin-top: 2px;
}

/* ── Password Strength ── */
.pw-strength { display: flex; align-items: center; gap: 8px; margin-top: 6px; }
.pw-strength-bar { flex: 1; height: 3px; background: #E5E5E5; border-radius: 2px; overflow: hidden; }
.pw-strength-fill { height: 100%; border-radius: 2px; transition: width 0.3s ease, background 0.3s ease; }
.pw-strength-fill.weak { background: #D0021B; }
.pw-strength-fill.fair { background: #F5A623; }
.pw-strength-fill.strong { background: #86BC25; }
.pw-strength-label { font-size: 11px; font-weight: 600; min-width: 24px; }
.pw-strength-label.weak { color: #D0021B; }
.pw-strength-label.fair { color: #F5A623; }
.pw-strength-label.strong { color: #86BC25; }

/* ── Buttons ── */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 20px;
  border-radius: 2px;
  font-size: 14px;
  font-weight: 700;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
  letter-spacing: 0.02em;
}
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-primary {
  background: #86BC25;
  color: #000000;
}
.btn-primary:hover:not(:disabled) {
  background: #6B9C1E;
}
.btn-ghost {
  background: transparent;
  color: #666666;
  border: 1px solid #D0D0D0;
}
.btn-ghost:hover:not(:disabled) { background: #F4F4F4; color: #000000; }
.w-full { width: 100%; }

/* ── Spinner ── */
.spinner {
  width: 16px; height: 16px;
  border: 2px solid rgba(0,0,0,0.15);
  border-top-color: #000;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Error Banner ── */
.error-banner {
  background: rgba(208, 2, 27, 0.05);
  border: 1px solid rgba(208, 2, 27, 0.2);
  border-left: 3px solid #D0021B;
  border-radius: 2px;
  padding: 10px 14px;
  font-size: 13px;
  color: #D0021B;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* ── Form Footer ── */
.form-footer {
  text-align: center;
  font-size: 13px;
  color: #666666;
  margin-top: 4px;
}
.link-btn {
  background: none;
  border: none;
  color: #86BC25;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  padding: 0;
  text-decoration: underline;
  text-underline-offset: 2px;
}
.link-btn:hover { color: #6B9C1E; }

/* ── Success View ── */
.success-view { text-align: center; padding: 8px 0; }
.success-icon { font-size: 52px; margin-bottom: 16px; animation: bounce 0.6s ease; }
@keyframes bounce {
  0% { transform: scale(0.5); opacity: 0; }
  70% { transform: scale(1.1); }
  100% { transform: scale(1); opacity: 1; }
}
.success-title { font-size: 20px; font-weight: 700; color: #000000; margin: 0 0 12px; }
.success-desc { font-size: 14px; color: #666666; line-height: 1.7; margin: 0 0 8px; }
.highlight-email { color: #86BC25; font-size: 14px; }
.success-hint { font-size: 12px; color: #999999; margin: 0 0 24px; }
.success-actions { display: flex; flex-direction: column; gap: 10px; }

/* ── Debug Bar ── */
.debug-bar {
  margin-top: 20px;
  padding: 8px 12px;
  background: #F4F4F4;
  border-radius: 2px;
  font-size: 11px;
  color: #999999;
  text-align: center;
}

/* ── Responsive: mobile hides brand panel ── */
@media (max-width: 768px) {
  .brand-panel { display: none; }
  .form-panel { background: #000000; }
  .auth-card {
    background: rgba(18,18,18,0.95);
    border-color: #1f1f1f;
  }
  .auth-card::before { color: #ffffff; }
  .auth-logo { display: flex; }
  .logo-symbol { color: #ffffff; }
  .logo-text { color: #ffffff; }
  .field-group label { color: #aaaaaa; }
  .field-group input { background: rgba(255,255,255,0.05); border-color: rgba(255,255,255,0.12); color: #ffffff; }
  .field-group input::placeholder { color: #555555; }
  .form-footer { color: #666666; }
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
