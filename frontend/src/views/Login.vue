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

    <el-dialog v-model="showRegister" :title="$t('login.registerTitle')" width="450px" :close-on-click-modal="false">
      <el-form :model="regForm" :label-width="locale === 'en' ? '120px' : '80px'" :rules="regRules" ref="regFormRef" status-icon>
        <el-form-item :label="$t('login.username')" prop="username">
          <el-input v-model="regForm.username" :placeholder="locale === 'en' ? '2-20 chars, letters/numbers' : '2-20位字母或数字'" />
        </el-form-item>
        <el-form-item label="显示名称" prop="display_name">
          <el-input v-model="regForm.display_name" :placeholder="locale === 'en' ? 'Display name' : '如：李四'" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="regForm.email" placeholder="email@example.com" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="regForm.phone" :placeholder="locale === 'en' ? 'Phone number' : '手机号码（选填）'" />
        </el-form-item>
        <el-form-item :label="$t('login.password')" prop="password">
          <el-input v-model="regForm.password" type="password" show-password :placeholder="locale === 'en' ? 'At least 6 chars' : '不少于6位'" />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirm_password">
          <el-input v-model="regForm.confirm_password" type="password" show-password :placeholder="locale === 'en' ? 'Confirm password' : '再次输入密码'" />
        </el-form-item>
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
const { t, locale } = useI18n()
const form = ref({ username: '', password: '' })
const remember = ref(false)
const loading = ref(false)
const showForgot = ref(false)
const showRegister = ref(false)
const regLoading = ref(false)
const regFormRef = ref(null)
const regForm = ref({ username: '', display_name: '', email: '', phone: '', password: '', confirm_password: '' })
const regRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_\u4e00-\u9fa5]{2,20}$/, message: '2-20位字母、数字或中文', trigger: 'blur' }
  ],
  display_name: [
    { required: true, message: '请输入显示名称', trigger: 'blur' }
  ],
  email: [
    { pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/, message: '邮箱格式不正确', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码不少于6位', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: (rule, value, cb) => value !== regForm.value.password ? cb(new Error('两次密码不一致')) : cb(), trigger: 'blur' }
  ]
}

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
  if (!regFormRef.value) return
  try {
    await regFormRef.value.validate()
  } catch {
    return
  }
  regLoading.value = true
  try {
    const res = await request.post('/register', regForm.value)
    showRegister.value = false
    // 自动登录
    store.setUser(res.access_token, res.display_name, res.role)
    ElMessage.success(t('login.registerTitle') + ' ' + t('common.success'))
    router.push('/dashboard')
  } catch (e) {
    ElMessage.error(typeof e === 'string' ? e : '注册失败')
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
