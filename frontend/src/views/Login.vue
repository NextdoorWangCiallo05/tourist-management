<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-header">
        <div class="login-logo">
          <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
            <rect x="2" y="2" width="28" height="28" rx="8" fill="var(--accent)"/>
            <path d="M10 16L14 20L22 12" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <h1 class="login-title">{{ $t('app.name') }}</h1>
        <p class="login-subtitle">{{ $t('app.subtitle') }}</p>
      </div>
      <el-form class="login-form" @submit.prevent="handleLogin">
        <div class="form-group">
          <label class="form-label">{{ $t('login.username') }}</label>
          <el-input v-model="form.username" :placeholder="$t('login.usernamePlaceholder')" size="large" :prefix-icon="User" clearable />
        </div>
        <div class="form-group">
          <label class="form-label">{{ $t('login.password') }}</label>
          <el-input v-model="form.password" type="password" :placeholder="$t('login.passwordPlaceholder')" size="large" :prefix-icon="Lock" show-password @keyup.enter="handleLogin" />
        </div>
        <div class="form-options">
          <label class="remember-me">
            <input type="checkbox" v-model="remember" />
            <span class="checkmark"></span>
            <span>{{ $t('login.remember') }}</span>
          </label>
          <a class="forgot-link" @click="showForgot = true">{{ $t('login.forgotPassword') }}</a>
        </div>
        <el-button type="primary" size="large" class="login-btn" :loading="loading" @click="handleLogin" round>
          {{ loading ? $t('login.loggingIn') : $t('login.loginBtn') }}
        </el-button>
      </el-form>
      <div class="login-footer">
        <span class="footer-text">{{ $t('login.defaultAccount') }}</span>
        <br>
        <span class="footer-link" @click="showRegister = true">{{ $t('login.noAccount') }}<a>{{ $t('login.register') }}</a></span>
      </div>
    </div>

    <el-dialog v-model="showForgot" title="忘记密码" width="400px">
      <p style="text-align:center;color:var(--text-secondary);margin:0;">请联系管理员重置密码</p>
      <template #footer>
        <el-button type="primary" @click="showForgot = false" round>确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showRegister" :title="$t('login.registerTitle')" width="420px">
      <el-form :model="regForm" :label-width="locale === 'en' ? '100px' : '70px'">
        <el-form-item :label="$t('login.username')"><el-input v-model="regForm.username" placeholder="4-20位字母或数字" /></el-form-item>
        <el-form-item label="显示名称"><el-input v-model="regForm.display_name" placeholder="如：李四" /></el-form-item>
        <el-form-item :label="$t('login.password')"><el-input v-model="regForm.password" type="password" show-password placeholder="不少于6位" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showRegister = false">{{ $t('common.cancel') }}</el-button>
        <el-button type="primary" @click="handleRegister" :loading="regLoading">{{ $t('login.registerBtn') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '../utils/request'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { useUserStore } from '../stores/user'
import { useI18n } from 'vue-i18n'

const router = useRouter()
const store = useUserStore()
const { locale } = useI18n()
const form = ref({ username: '', password: '' })
const remember = ref(false)
const loading = ref(false)
const showForgot = ref(false)
const showRegister = ref(false)
const regLoading = ref(false)
const regForm = ref({ username: '', display_name: '', password: '' })

const handleLogin = async () => {
  if (!form.value.username || !form.value.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  loading.value = true
  try {
    const res = await request.post('/login', form.value)
    store.setUser(res.access_token, res.display_name, res.role)
    if (remember.value) {
      localStorage.setItem('rememberedUser', form.value.username)
    } else {
      localStorage.removeItem('rememberedUser')
    }
    ElMessage.success('登录成功')
    router.push('/dashboard')
  } catch {
    ElMessage.error('登录失败，请检查用户名和密码')
  } finally {
    loading.value = false
  }
}

const handleRegister = async () => {
  if (!regForm.value.username || !regForm.value.password) {
    ElMessage.warning('用户名和密码不能为空')
    return
  }
  regLoading.value = true
  try {
    await request.post('/register', regForm.value)
    showRegister.value = false
    form.value.username = regForm.value.username
    form.value.password = regForm.value.password
    ElMessage.success('注册成功，请登录')
  } catch {
    ElMessage.error('注册失败')
  } finally {
    regLoading.value = false
  }
}

onMounted(() => {
  const u = localStorage.getItem('rememberedUser')
  if (u) {
    form.value.username = u
    remember.value = true
  }
})
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: var(--bg);
}

.login-card {
  width: 400px;
  background: var(--bg-card);
  border-radius: var(--radius-xl);
  padding: 44px 36px 36px;
  box-shadow: var(--shadow-lg);
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}
.login-logo {
  display: inline-flex;
  margin-bottom: 16px;
}
.login-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 6px;
  letter-spacing: 0.5px;
}
.login-subtitle {
  font-size: 14px;
  color: var(--text-muted);
  margin: 0;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.form-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.remember-me {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--text-secondary);
  cursor: pointer;
}
.remember-me input { display: none; }
.checkmark {
  width: 16px;
  height: 16px;
  border-radius: 4px;
  border: 1.5px solid var(--text-muted);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;
}
.remember-me input:checked + .checkmark {
  background: var(--accent);
  border-color: var(--accent);
}
.remember-me input:checked + .checkmark::after {
  content: '';
  width: 5px;
  height: 8px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
  margin-top: -1px;
}
.forgot-link {
  font-size: 13px;
  color: var(--accent);
  cursor: pointer;
  text-decoration: none;
}
.forgot-link:hover { opacity: 0.8; }

.login-btn {
  width: 100%;
  height: 44px;
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 2px;
}

.login-footer {
  text-align: center;
  margin-top: 24px;
}
.footer-text {
  font-size: 12px;
  color: var(--text-muted);
}
.footer-link { font-size: 13px; color: var(--text-muted); cursor: pointer; }
.footer-link a { color: var(--accent); text-decoration: none; }
.footer-link a:hover { opacity: 0.8; }
</style>
