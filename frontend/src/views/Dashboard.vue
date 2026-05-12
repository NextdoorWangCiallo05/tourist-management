<template>
  <div class="dashboard">
    <el-container class="main-container">
      <el-aside width="240px" class="sidebar">
        <div class="sidebar-header">
          <div class="logo-wrapper">
            <svg class="logo-icon" viewBox="0 0 64 64" fill="none">
              <circle cx="32" cy="32" r="30" fill="url(#logoGradient)"/>
              <path d="M32 18 L32 46 M20 28 L44 28 M18 36 L46 36" stroke="white" stroke-width="3" stroke-linecap="round"/>
              <circle cx="32" cy="32" r="8" fill="white" opacity="0.3"/>
              <defs>
                <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stop-color="#3b82f6"/>
                  <stop offset="100%" stop-color="#1e40af"/>
                </linearGradient>
              </defs>
            </svg>
            <div class="logo-text">
              <h1 class="logo-title">智游云管</h1>
              <p class="logo-subtitle">旅游业务管理系统</p>
            </div>
          </div>
        </div>
        <el-menu default-active="dashboard" class="sidebar-menu">
          <el-menu-item index="dashboard" @click="navigate('/dashboard')">
            <el-icon><Monitor /></el-icon>
            <span>首页概览</span>
          </el-menu-item>
          <el-menu-item index="create-app" @click="navigate('/applications/create')">
            <el-icon><Plus /></el-icon>
            <span>新建申请</span>
          </el-menu-item>
          <el-menu-item index="applications" @click="navigate('/applications')">
            <el-icon><Document /></el-icon>
            <span>申请管理</span>
          </el-menu-item>
          <el-menu-item index="tour-groups" @click="navigate('/tour-groups')">
            <el-icon><Search /></el-icon>
            <span>旅游团查询</span>
          </el-menu-item>
          <el-menu-item index="tour-group-mgmt" @click="navigate('/tour-group-management')">
            <el-icon><Suitcase /></el-icon>
            <span>旅游团管理</span>
          </el-menu-item>
          <el-menu-item index="routes" @click="navigate('/routes')">
            <el-icon><MapLocation /></el-icon>
            <span>路线管理</span>
          </el-menu-item>
          <el-menu-item index="confirmations" @click="navigate('/confirmations')">
            <el-icon><Printer /></el-icon>
            <span>确认书打印</span>
          </el-menu-item>
          <el-menu-item index="export" @click="navigate('/daily-export')">
            <el-icon><Download /></el-icon>
            <span>财务导出</span>
          </el-menu-item>
        </el-menu>
        <div class="sidebar-footer">
          <div class="user-info">
            <div class="user-avatar">
              <span class="avatar-text">王</span>
            </div>
            <div class="user-detail">
              <span class="user-name">王经理</span>
              <span class="user-role">高级操作员</span>
            </div>
          </div>
          <el-button @click="handleLogout" class="logout-btn">
            <el-icon><SwitchButton /></el-icon> 退出登录
          </el-button>
        </div>
      </el-aside>
      <el-container class="main-content">
        <el-header class="top-header">
          <div class="header-left">
            <el-icon class="header-icon"><Odometer /></el-icon>
            <span class="breadcrumb">首页概览</span>
          </div>
          <div class="header-right">
            <el-tag type="info" effect="plain" class="date-tag">
              <el-icon style="margin-right:4px"><Calendar /></el-icon>
              {{ currentDate }}
            </el-tag>
          </div>
        </el-header>
        <el-main class="content-area">
          <div class="welcome-banner">
            <div class="welcome-text">
              <h2>上午好，王经理 👋</h2>
              <p>欢迎回来，以下是今日业务概览</p>
            </div>
            <div class="welcome-stats">
              <div class="welcome-stat-item">
                <span class="welcome-stat-value">{{ stats.totalApplications }}</span>
                <span class="welcome-stat-label">今日申请</span>
              </div>
              <div class="welcome-stat-divider"></div>
              <div class="welcome-stat-item">
                <span class="welcome-stat-value">{{ stats.totalParticipants }}</span>
                <span class="welcome-stat-label">参加者</span>
              </div>
              <div class="welcome-stat-divider"></div>
              <div class="welcome-stat-item">
                <span class="welcome-stat-value">{{ stats.activeGroups }}</span>
                <span class="welcome-stat-label">进行中团</span>
              </div>
            </div>
          </div>

          <div class="stats-grid">
            <div class="stat-card">
              <div class="stat-icon-wrap blue">
                <el-icon><Document /></el-icon>
              </div>
              <div class="stat-info">
                <span class="stat-value">{{ stats.totalApplications }}</span>
                <span class="stat-label">今日申请</span>
              </div>
              <div class="stat-trend up">
                <el-icon><Top /></el-icon> 12%
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon-wrap green">
                <el-icon><User /></el-icon>
              </div>
              <div class="stat-info">
                <span class="stat-value">{{ stats.totalParticipants }}</span>
                <span class="stat-label">今日参加者</span>
              </div>
              <div class="stat-trend up">
                <el-icon><Top /></el-icon> 8%
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon-wrap purple">
                <el-icon><Wallet /></el-icon>
              </div>
              <div class="stat-info">
                <span class="stat-value">¥{{ stats.totalPayments }}</span>
                <span class="stat-label">今日收款</span>
              </div>
              <div class="stat-trend up">
                <el-icon><Top /></el-icon> 15%
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon-wrap orange">
                <el-icon><Suitcase /></el-icon>
              </div>
              <div class="stat-info">
                <span class="stat-value">{{ stats.activeGroups }}</span>
                <span class="stat-label">进行中旅游团</span>
              </div>
              <div class="stat-trend down">
                <el-icon><Bottom /></el-icon> 3%
              </div>
            </div>
          </div>

          <div class="content-grid">
            <div class="quick-section">
              <div class="section-header">
                <el-icon class="section-icon"><Lightning /></el-icon>
                <h3>快捷操作</h3>
              </div>
              <div class="quick-actions">
                <button class="action-btn primary" @click="navigate('/applications/create')">
                  <el-icon><CirclePlus /></el-icon>
                  <span>新建申请</span>
                </button>
                <button class="action-btn" @click="navigate('/tour-groups')">
                  <el-icon><Search /></el-icon>
                  <span>查询旅游团</span>
                </button>
                <button class="action-btn" @click="navigate('/applications')">
                  <el-icon><List /></el-icon>
                  <span>申请列表</span>
                </button>
                <button class="action-btn" @click="navigate('/confirmations')">
                  <el-icon><Printer /></el-icon>
                  <span>打印确认书</span>
                </button>
              </div>
            </div>

            <div class="info-section">
              <div class="section-header">
                <el-icon class="section-icon"><Bell /></el-icon>
                <h3>待办提醒</h3>
              </div>
              <div class="info-list">
                <div class="info-item">
                  <el-tag size="small" type="danger" effect="dark" round>紧急</el-tag>
                  <span class="info-text">3个旅游团即将出发</span>
                </div>
                <div class="info-item">
                  <el-tag size="small" type="warning" effect="dark" round>待办</el-tag>
                  <span class="info-text">5笔余款待确认</span>
                </div>
                <div class="info-item">
                  <el-tag size="small" type="primary" effect="dark" round>通知</el-tag>
                  <span class="info-text">2条路线信息已更新</span>
                </div>
                <div class="info-item">
                  <el-tag size="small" type="success" effect="dark" round>完成</el-tag>
                  <span class="info-text">今日数据已同步</span>
                </div>
              </div>
            </div>
          </div>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import {
  Monitor, Plus, Document, Search, Suitcase, MapLocation,
  Printer, Download, SwitchButton, Odometer, Calendar,
  Top, Bottom, User, Wallet, Lightning, CirclePlus,
  List, Bell, InfoFilled
} from '@element-plus/icons-vue'

const router = useRouter()
const currentDate = new Date().toLocaleDateString('zh-CN', {
  year: 'numeric',
  month: '2-digit',
  day: '2-digit',
  weekday: 'long'
})
const stats = ref({
  totalApplications: 0,
  totalParticipants: 0,
  totalPayments: '0.00',
  activeGroups: 0
})

const navigate = (path) => {
  router.push(path)
}

const handleLogout = () => {
  localStorage.removeItem('token')
  router.push('/')
}

const loadStats = async () => {
  try {
    const token = localStorage.getItem('token')
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`

    const [groupsRes, appsRes] = await Promise.all([
      axios.get('/api/tour_groups'),
      axios.get('/api/applications')
    ])

    stats.value.activeGroups = groupsRes.data.length
    stats.value.totalApplications = appsRes.data.length
    stats.value.totalParticipants = appsRes.data.reduce((sum, app) => sum + app.adult_count + app.child_count, 0) || 0
    stats.value.totalPayments = (appsRes.data.reduce((sum, app) => sum + app.deposit_amount, 0) || 0).toFixed(2)
  } catch (error) {
    console.error('Failed to load stats:', error)
  }
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.dashboard {
  min-height: 100vh;
  display: flex;
}

.main-container {
  width: 100%;
  height: 100vh;
}

.sidebar {
  background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
  color: white;
  display: flex;
  flex-direction: column;
  padding: 0;
  border-right: 1px solid rgba(255,255,255,0.05);
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.logo-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  width: 44px;
  height: 44px;
}

.logo-text {
  display: flex;
  flex-direction: column;
}

.logo-title {
  font-size: 18px;
  font-weight: 700;
  margin: 0;
  color: white;
  letter-spacing: 1px;
}

.logo-subtitle {
  font-size: 10px;
  margin: 2px 0 0 0;
  color: rgba(255, 255, 255, 0.5);
}

.sidebar-menu {
  flex: 1;
  border-right: none;
  background: transparent;
  padding: 8px 0;
}

.sidebar-menu .el-menu-item {
  color: rgba(255, 255, 255, 0.65);
  height: 46px;
  line-height: 46px;
  margin: 2px 12px;
  border-radius: 10px;
  font-size: 14px;
}

.sidebar-menu .el-menu-item:hover {
  background: rgba(59, 130, 246, 0.12);
  color: rgba(255, 255, 255, 0.9);
}

.sidebar-menu .el-menu-item.is-active {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(30, 64, 175, 0.2));
  color: #93c5fd;
  font-weight: 500;
}

.sidebar-menu .el-menu-item .el-icon {
  margin-right: 10px;
  font-size: 18px;
}

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.user-avatar {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  background: linear-gradient(135deg, #3b82f6, #1e40af);
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-text {
  color: white;
  font-weight: 600;
  font-size: 15px;
}

.user-detail {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
  color: white;
}

.user-role {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.45);
}

.logout-btn {
  width: 100%;
  height: 36px;
  border-radius: 8px;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.6);
  font-size: 13px;
}

.logout-btn:hover {
  background: rgba(239, 68, 68, 0.12);
  color: #fca5a5;
  border-color: rgba(239, 68, 68, 0.25);
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #f1f5f9;
}

.top-header {
  background: white;
  padding: 0 28px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e2e8f0;
  height: 60px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-icon {
  font-size: 18px;
  color: #3b82f6;
}

.breadcrumb {
  font-size: 15px;
  color: #1e293b;
  font-weight: 600;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.date-tag {
  font-size: 13px;
  padding: 4px 12px;
  border-radius: 20px;
}

.content-area {
  flex: 1;
  padding: 24px 28px;
  overflow-y: auto;
}

.welcome-banner {
  background: linear-gradient(135deg, #1e40af 0%, #3b82f6 50%, #60a5fa 100%);
  border-radius: 16px;
  padding: 28px 32px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  color: white;
  position: relative;
  overflow: hidden;
}

.welcome-banner::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -10%;
  width: 300px;
  height: 300px;
  background: rgba(255,255,255,0.05);
  border-radius: 50%;
}

.welcome-banner::after {
  content: '';
  position: absolute;
  bottom: -30%;
  right: 20%;
  width: 200px;
  height: 200px;
  background: rgba(255,255,255,0.03);
  border-radius: 50%;
}

.welcome-text {
  position: relative;
  z-index: 1;
}

.welcome-text h2 {
  font-size: 22px;
  font-weight: 700;
  margin: 0 0 6px;
}

.welcome-text p {
  font-size: 14px;
  margin: 0;
  opacity: 0.8;
}

.welcome-stats {
  display: flex;
  align-items: center;
  gap: 24px;
  position: relative;
  z-index: 1;
}

.welcome-stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.welcome-stat-value {
  font-size: 28px;
  font-weight: 700;
  line-height: 1.2;
}

.welcome-stat-label {
  font-size: 12px;
  opacity: 0.75;
  margin-top: 2px;
}

.welcome-stat-divider {
  width: 1px;
  height: 40px;
  background: rgba(255,255,255,0.2);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 14px;
  padding: 22px 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
  transition: all 0.25s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.08);
}

.stat-icon-wrap {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-icon-wrap .el-icon {
  font-size: 22px;
}

.stat-icon-wrap.blue {
  background: linear-gradient(135deg, rgba(59,130,246,0.12), rgba(30,64,175,0.12));
  color: #3b82f6;
}

.stat-icon-wrap.green {
  background: linear-gradient(135deg, rgba(34,197,94,0.12), rgba(22,163,74,0.12));
  color: #22c55e;
}

.stat-icon-wrap.purple {
  background: linear-gradient(135deg, rgba(168,85,247,0.12), rgba(126,34,206,0.12));
  color: #a855f7;
}

.stat-icon-wrap.orange {
  background: linear-gradient(135deg, rgba(249,115,22,0.12), rgba(234,88,12,0.12));
  color: #f97316;
}

.stat-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.stat-info .stat-value {
  font-size: 26px;
  font-weight: 700;
  color: #0f172a;
  line-height: 1.2;
}

.stat-info .stat-label {
  font-size: 13px;
  color: #94a3b8;
  margin-top: 2px;
}

.stat-trend {
  font-size: 12px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  gap: 2px;
  flex-shrink: 0;
}

.stat-trend .el-icon {
  font-size: 12px;
}

.stat-trend.up {
  color: #22c55e;
  background: rgba(34,197,94,0.08);
}

.stat-trend.down {
  color: #f97316;
  background: rgba(249,115,22,0.08);
}

.content-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.quick-section,
.info-section {
  background: white;
  border-radius: 14px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 20px;
}

.section-icon {
  font-size: 18px;
  color: #3b82f6;
}

.section-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #0f172a;
  margin: 0;
}

.quick-actions {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px 20px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  background: white;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 14px;
  color: #475569;
}

.action-btn:hover {
  border-color: #3b82f6;
  background: rgba(59,130,246,0.03);
  transform: translateY(-1px);
}

.action-btn .el-icon {
  font-size: 20px;
  color: #64748b;
}

.action-btn.primary {
  background: linear-gradient(135deg, #3b82f6, #1e40af);
  border: none;
  color: white;
}

.action-btn.primary .el-icon {
  color: white;
}

.action-btn.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(59,130,246,0.3);
}

.info-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 10px;
  background: #f8fafc;
  transition: all 0.2s ease;
}

.info-item:hover {
  background: #f1f5f9;
}

.info-text {
  font-size: 14px;
  color: #334155;
}
</style>