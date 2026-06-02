<template>
  <div class="login-page">
    <div class="bg-circle bg-circle-1"></div>
    <div class="bg-circle bg-circle-2"></div>
    <div class="bg-circle bg-circle-3"></div>

    <div class="login-card">
      <div class="login-left">
        <div class="brand">
          <div class="brand-icon-wrap">
            <svg viewBox="0 0 64 64" fill="none">
              <circle cx="32" cy="32" r="30" fill="url(#g)"/>
              <path d="M32 18 L32 46 M20 28 L44 28 M18 36 L46 36" stroke="white" stroke-width="3" stroke-linecap="round"/>
              <circle cx="32" cy="32" r="8" fill="white" opacity="0.3"/>
              <defs>
                <linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stop-color="#1e40af"/>
                  <stop offset="100%" stop-color="#3b82f6"/>
                </linearGradient>
              </defs>
            </svg>
          </div>
          <h1>智游云管</h1>
          <p>旅游业务管理系统</p>
        </div>
        <div class="feature-grid">
          <div class="feature-cell">
            <span class="feature-emoji">✈️</span>
            <span>旅游团管理</span>
          </div>
          <div class="feature-cell">
            <span class="feature-emoji">📋</span>
            <span>申请办理</span>
          </div>
          <div class="feature-cell">
            <span class="feature-emoji">💰</span>
            <span>财务管理</span>
          </div>
          <div class="feature-cell">
            <span class="feature-emoji">📊</span>
            <span>数据分析</span>
          </div>
        </div>
        <div class="login-left-footer">
          <span class="dot active"></span>
          <span class="dot"></span>
          <span class="dot"></span>
        </div>
      </div>
      <div class="login-right">
        <div class="login-header">
          <h2>欢迎回来</h2>
          <p>登录您的账号以继续</p>
        </div>
        <el-form :model="form" class="login-form">
          <el-form-item>
            <div class="input-label">用户名</div>
            <el-input v-model="form.username" placeholder="请输入用户名" />
          </el-form-item>
          <el-form-item>
            <div class="input-label">密码</div>
            <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
          </el-form-item>
          <el-form-item>
            <div class="form-actions">
              <el-checkbox v-model="remember">记住密码</el-checkbox>
              <el-button type="primary" link @click="showForgot = true">忘记密码?</el-button>
            </div>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" class="submit-btn" @click="handleLogin" :loading="loading">
              {{ loading ? '登录中...' : '登 录' }}
            </el-button>
          </el-form-item>
        </el-form>
        <div class="login-divider">
          <span></span>
          <span>提示</span>
          <span></span>
        </div>
        <p class="login-tip">默认账号：<strong>admin</strong> 密码：<strong>admin123</strong></p>
      </div>
    </div>

    <el-dialog v-model="showForgot" title="忘记密码" width="380px">
      <p style="text-align:center;color:#64748b;">请联系管理员重置密码</p>
      <div style="text-align:center;margin-top:16px;">
        <el-button type="primary" @click="showForgot = false">确定</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '../utils/request'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../stores/user'

const router = useRouter()
const store = useUserStore()
const form = ref({ username: '', password: '' })
const remember = ref(false)
const loading = ref(false)
const showForgot = ref(false)

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
  background: linear-gradient(135deg, #f0f4f8 0%, #e2e8f0 50%, #d1d9e6 100%);
  position: relative;
  overflow: hidden;
}

.bg-circle {
  position: absolute;
  border-radius: 50%;
}

.bg-circle-1 {
  top: -20%;
  right: -10%;
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(59,130,246,0.15) 0%, transparent 70%);
}

.bg-circle-2 {
  bottom: -15%;
  left: -8%;
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, rgba(30,64,175,0.1) 0%, transparent 70%);
}

.bg-circle-3 {
  top: 40%;
  left: 15%;
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(96,165,250,0.08) 0%, transparent 70%);
}

.login-card {
  position: relative;
  z-index: 1;
  display: flex;
  width: 900px;
  min-height: 520px;
  background: rgba(255,255,255,0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  box-shadow:
    0 0 0 1px rgba(255,255,255,0.5),
    0 25px 50px -12px rgba(0,0,0,0.25);
  overflow: hidden;
}

.login-left {
  width: 38%;
  background: linear-gradient(160deg, #1e40af 0%, #3b82f6 50%, #60a5fa 100%);
  padding: 48px 32px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: #fff;
  position: relative;
}

.login-left::after {
  content: '';
  position: absolute;
  inset: 0;
  background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.03'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
  pointer-events: none;
}

.brand {
  text-align: center;
  position: relative;
  z-index: 1;
}

.brand-icon-wrap {
  width: 80px;
  height: 80px;
  margin: 0 auto 20px;
  filter: drop-shadow(0 4px 12px rgba(0,0,0,0.2));
}

.brand h1 {
  font-size: 30px;
  font-weight: 700;
  margin: 0 0 8px;
  letter-spacing: 2px;
  text-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.brand p {
  font-size: 14px;
  margin: 0;
  opacity: 0.85;
  font-weight: 300;
  letter-spacing: 1px;
}

.feature-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  width: 100%;
  max-width: 220px;
  margin-top: 40px;
  position: relative;
  z-index: 1;
}

.feature-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 14px 8px;
  background: rgba(255,255,255,0.12);
  border-radius: 12px;
  font-size: 12px;
  transition: all 0.3s ease;
  cursor: default;
}

.feature-cell:hover {
  background: rgba(255,255,255,0.22);
  transform: translateY(-2px);
}

.feature-emoji {
  font-size: 22px;
  line-height: 1;
}

.login-left-footer {
  display: flex;
  gap: 8px;
  margin-top: 36px;
  position: relative;
  z-index: 1;
}

.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: rgba(255,255,255,0.3);
  transition: all 0.3s ease;
}

.dot.active {
  width: 20px;
  border-radius: 3px;
  background: rgba(255,255,255,0.8);
}

.login-right {
  width: 62%;
  padding: 48px 56px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.login-header {
  margin-bottom: 32px;
}

.login-header h2 {
  font-size: 26px;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 8px;
}

.login-header p {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}

.login-form {
  width: 100%;
}

.input-label {
  font-size: 13px;
  font-weight: 500;
  color: #334155;
  margin-bottom: 6px;
}

.form-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.submit-btn {
  width: 100%;
  height: 46px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 12px;
  background: linear-gradient(135deg, #3b82f6, #1e40af);
  border: none;
  transition: all 0.35s ease;
  box-shadow: 0 4px 15px rgba(59,130,246,0.3);
}

.submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(59,130,246,0.4);
}

.submit-btn:active {
  transform: translateY(0);
}

.login-divider {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 28px;
}

.login-divider span:first-child,
.login-divider span:last-child {
  flex: 1;
  height: 1px;
  background: linear-gradient(to right, transparent, #e2e8f0);
}

.login-divider span:last-child {
  background: linear-gradient(to left, transparent, #e2e8f0);
}

.login-divider span:nth-child(2) {
  font-size: 12px;
  color: #94a3b8;
}

.login-tip {
  text-align: center;
  font-size: 13px;
  color: #94a3b8;
  margin: 12px 0 0;
}

.login-tip strong {
  color: #3b82f6;
  font-weight: 600;
}
</style>
