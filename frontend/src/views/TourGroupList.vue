<template>
  <div class="page">
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
        <el-menu default-active="tour-groups" class="sidebar-menu">
          <el-menu-item index="dashboard" @click="navigate('/dashboard')">
            <el-icon><Monitor /></el-icon><span>首页概览</span>
          </el-menu-item>
          <el-menu-item index="create-app" @click="navigate('/applications/create')">
            <el-icon><Plus /></el-icon><span>新建申请</span>
          </el-menu-item>
          <el-menu-item index="applications" @click="navigate('/applications')">
            <el-icon><Document /></el-icon><span>申请管理</span>
          </el-menu-item>
          <el-menu-item index="tour-groups" @click="navigate('/tour-groups')">
            <el-icon><Search /></el-icon><span>旅游团查询</span>
          </el-menu-item>
          <el-menu-item index="tour-group-mgmt" @click="navigate('/tour-group-management')">
            <el-icon><Suitcase /></el-icon><span>旅游团管理</span>
          </el-menu-item>
          <el-menu-item index="routes" @click="navigate('/routes')">
            <el-icon><MapLocation /></el-icon><span>路线管理</span>
          </el-menu-item>
          <el-menu-item index="confirmations" @click="navigate('/confirmations')">
            <el-icon><Printer /></el-icon><span>确认书打印</span>
          </el-menu-item>
          <el-menu-item index="export" @click="navigate('/daily-export')">
            <el-icon><Download /></el-icon><span>财务导出</span>
          </el-menu-item>
        </el-menu>
        <div class="sidebar-footer">
          <div class="user-info">
            <div class="user-avatar"><span class="avatar-text">王</span></div>
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
            <el-icon class="header-icon"><Search /></el-icon>
            <span class="breadcrumb">旅游团查询</span>
          </div>
          <div class="header-right">
            <el-tag type="info" effect="plain" class="date-tag">
              <el-icon style="margin-right:4px"><Calendar /></el-icon>
              {{ currentDate }}
            </el-tag>
          </div>
        </el-header>
        <el-main class="content-area">
          <div class="search-section">
            <div class="search-box">
              <el-input v-model="searchText" placeholder="搜索旅游团名称或代码" clearable @keyup.enter="searchGroups" />
              <el-button type="primary" @click="searchGroups">
                <el-icon><Search /></el-icon> 检索旅游团
              </el-button>
            </div>
          </div>
          <div class="tour-group-grid">
            <div v-for="group in filteredGroups" :key="group.id" class="tour-card">
              <div class="card-header">
                <div class="card-header-left">
                  <el-tag size="small" :type="canApply(group) ? 'success' : 'danger'" effect="dark" round>
                    {{ canApply(group) ? '可报名' : '已截止' }}
                  </el-tag>
                  <span class="group-code">{{ group.group_code }}</span>
                </div>
                <el-tag size="small" effect="plain" type="info">{{ group.route_code }}</el-tag>
              </div>
              <div class="card-body">
                <h3 class="route-name">{{ group.route_name }}</h3>
                <div class="info-rows">
                  <div class="info-row">
                    <el-icon><Calendar /></el-icon>
                    <span>出发：{{ group.departure_date }}</span>
                  </div>
                  <div class="info-row">
                    <el-icon><Timer /></el-icon>
                    <span>截止：{{ group.deadline_date }}</span>
                  </div>
                  <div class="info-row">
                    <el-icon><UserFilled /></el-icon>
                    <span>剩余：<strong>{{ getRemainingCapacity(group) }} / {{ group.max_capacity }}</strong> 人</span>
                  </div>
                </div>
                <div class="price-row">
                  <div class="price-item">
                    <span class="price-label">成人</span>
                    <span class="price-value">¥{{ group.adult_price }}</span>
                  </div>
                  <div class="price-divider"></div>
                  <div class="price-item">
                    <span class="price-label">儿童</span>
                    <span class="price-value">¥{{ group.child_price }}</span>
                  </div>
                </div>
              </div>
              <div class="card-footer">
                <el-button @click="checkAvailability(group)" :icon="InfoFilled">检查可用性</el-button>
                <el-button type="primary" @click="createApplication(group.id)" :disabled="!canApply(group)">
                  立即报名
                </el-button>
              </div>
            </div>
          </div>
          <div v-if="filteredGroups.length === 0" class="empty-state">
            <el-empty description="未找到匹配的旅游团" />
          </div>
        </el-main>
      </el-container>
    </el-container>
    <el-dialog v-model="showAvailability" title="可用性检查结果" width="420px">
      <div class="availability-result">
        <div :class="['result-icon', availabilityResult?.available ? 'success' : 'error']">
          <el-icon v-if="availabilityResult?.available" :size="32"><CircleCheck /></el-icon>
          <el-icon v-else :size="32"><CircleClose /></el-icon>
        </div>
        <p :class="['result-text', availabilityResult?.available ? 'success' : 'error']">
          {{ availabilityResult?.reason }}
        </p>
        <div v-if="availabilityResult?.available" class="apply-info">
          <div class="apply-info-row">
            <span>旅游团代码</span>
            <span>{{ currentGroupForCheck?.group_code }}</span>
          </div>
          <div class="apply-info-row">
            <span>路线名称</span>
            <span>{{ currentGroupForCheck?.route_name }}</span>
          </div>
          <el-button type="primary" class="apply-btn" @click="proceedToApply">立即申请</el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import {
  Monitor, Plus, Document, Search, Suitcase, MapLocation,
  Printer, Download, SwitchButton, Calendar, Timer, UserFilled,
  InfoFilled, CircleCheck, CircleClose
} from '@element-plus/icons-vue'

const router = useRouter()
const groups = ref([])
const searchText = ref('')
const showAvailability = ref(false)
const availabilityResult = ref(null)
const currentGroupForCheck = ref(null)

const currentDate = new Date().toLocaleDateString('zh-CN', {
  year: 'numeric', month: '2-digit', day: '2-digit', weekday: 'long'
})

const filteredGroups = computed(() => {
  if (!searchText.value) return groups.value
  const q = searchText.value
  return groups.value.filter(g =>
    g.route_name?.includes(q) || g.group_code?.includes(q)
  )
})

const navigate = (path) => { router.push(path) }
const handleLogout = () => { localStorage.removeItem('token'); router.push('/') }

const loadGroups = async () => {
  try {
    const token = localStorage.getItem('token')
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
    const res = await axios.get('/api/tour_groups')
    groups.value = res.data
  } catch (error) {
    console.error('Failed to load tour groups:', error)
  }
}

const searchGroups = () => {}

const getRemainingCapacity = (group) => Math.max(0, group.max_capacity - 0)

const canApply = (group) => {
  const today = new Date()
  const deadline = new Date(group.deadline_date)
  return today <= deadline && getRemainingCapacity(group) > 0
}

const checkAvailability = async (group) => {
  currentGroupForCheck.value = group
  try {
    const token = localStorage.getItem('token')
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
    const res = await axios.get(`/api/tour_groups/${group.id}/check_availability`)
    availabilityResult.value = res.data
    showAvailability.value = true
  } catch (error) {
    console.error('Failed to check availability:', error)
  }
}

const createApplication = (groupId) => {
  router.push({ path: '/applications/create', query: { groupId } })
}

const proceedToApply = () => {
  showAvailability.value = false
  if (currentGroupForCheck.value) {
    createApplication(currentGroupForCheck.value.id)
  }
}

onMounted(() => { loadGroups() })
</script>

<style scoped>
.page { min-height: 100vh; display: flex; }
.main-container { width: 100%; height: 100vh; }

.sidebar {
  background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
  color: white; display: flex; flex-direction: column;
  border-right: 1px solid rgba(255,255,255,0.05);
}
.sidebar-header { padding: 20px; border-bottom: 1px solid rgba(255,255,255,0.06); }
.logo-wrapper { display: flex; align-items: center; gap: 12px; }
.logo-icon { width: 44px; height: 44px; }
.logo-text { display: flex; flex-direction: column; }
.logo-title { font-size: 18px; font-weight: 700; margin: 0; color: white; letter-spacing: 1px; }
.logo-subtitle { font-size: 10px; margin: 2px 0 0; color: rgba(255,255,255,0.5); }
.sidebar-menu { flex: 1; border-right: none; background: transparent; padding: 8px 0; }
.sidebar-menu .el-menu-item {
  color: rgba(255,255,255,0.65); height: 46px; line-height: 46px;
  margin: 2px 12px; border-radius: 10px; font-size: 14px;
}
.sidebar-menu .el-menu-item:hover { background: rgba(59,130,246,0.12); color: rgba(255,255,255,0.9); }
.sidebar-menu .el-menu-item.is-active {
  background: linear-gradient(135deg, rgba(59,130,246,0.2), rgba(30,64,175,0.2));
  color: #93c5fd; font-weight: 500;
}
.sidebar-menu .el-menu-item .el-icon { margin-right: 10px; font-size: 18px; }
.sidebar-footer { padding: 16px; border-top: 1px solid rgba(255,255,255,0.06); }
.user-info { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
.user-avatar {
  width: 38px; height: 38px; border-radius: 10px;
  background: linear-gradient(135deg, #3b82f6, #1e40af);
  display: flex; align-items: center; justify-content: center;
}
.avatar-text { color: white; font-weight: 600; font-size: 15px; }
.user-detail { display: flex; flex-direction: column; }
.user-name { font-size: 14px; font-weight: 600; color: white; }
.user-role { font-size: 11px; color: rgba(255,255,255,0.45); }
.logout-btn {
  width: 100%; height: 36px; border-radius: 8px; background: transparent;
  border: 1px solid rgba(255,255,255,0.1); color: rgba(255,255,255,0.6); font-size: 13px;
}
.logout-btn:hover { background: rgba(239,68,68,0.12); color: #fca5a5; border-color: rgba(239,68,68,0.25); }

.main-content { flex: 1; display: flex; flex-direction: column; background: #f1f5f9; }
.top-header {
  background: white; padding: 0 28px; display: flex; justify-content: space-between;
  align-items: center; border-bottom: 1px solid #e2e8f0; height: 60px;
}
.header-left { display: flex; align-items: center; gap: 8px; }
.header-icon { font-size: 18px; color: #3b82f6; }
.breadcrumb { font-size: 15px; color: #1e293b; font-weight: 600; }
.header-right { display: flex; align-items: center; gap: 12px; }
.date-tag { font-size: 13px; padding: 4px 12px; border-radius: 20px; }
.content-area { flex: 1; padding: 24px 28px; overflow-y: auto; }

.search-section { margin-bottom: 24px; }
.search-box { display: flex; gap: 12px; max-width: 520px; }

.tour-group-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
.tour-card {
  background: white; border-radius: 14px; overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04); transition: all 0.25s ease;
}
.tour-card:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(0,0,0,0.08); }
.card-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 16px 20px; background: #f8fafc; border-bottom: 1px solid #e2e8f0;
}
.card-header-left { display: flex; align-items: center; gap: 10px; }
.group-code { font-size: 13px; font-weight: 600; color: #3b82f6; }
.card-body { padding: 20px; }
.route-name { font-size: 17px; font-weight: 600; color: #0f172a; margin: 0 0 14px; }
.info-rows { display: flex; flex-direction: column; gap: 8px; }
.info-row { display: flex; align-items: center; gap: 6px; font-size: 13px; color: #64748b; }
.info-row .el-icon { font-size: 14px; }
.info-row strong { color: #3b82f6; }
.price-row {
  display: flex; align-items: center; gap: 16px; margin-top: 16px;
  padding-top: 14px; border-top: 1px dashed #e2e8f0;
}
.price-item { display: flex; flex-direction: column; gap: 2px; }
.price-label { font-size: 12px; color: #94a3b8; }
.price-value { font-size: 18px; font-weight: 700; color: #0f172a; }
.price-divider { width: 1px; height: 32px; background: #e2e8f0; }
.card-footer {
  display: flex; gap: 10px; padding: 14px 20px; background: #f8fafc;
  border-top: 1px solid #e2e8f0;
}
.card-footer .el-button { flex: 1; }

.empty-state { padding: 60px 0; }

.availability-result { text-align: center; padding: 20px; }
.result-icon {
  width: 64px; height: 64px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto 16px;
}
.result-icon.success { background: rgba(34,197,94,0.1); color: #22c55e; }
.result-icon.error { background: rgba(239,68,68,0.1); color: #ef4444; }
.result-text { font-size: 15px; font-weight: 500; margin: 0 0 20px; }
.result-text.success { color: #22c55e; }
.result-text.error { color: #ef4444; }
.apply-info { background: #f8fafc; border-radius: 10px; padding: 16px; }
.apply-info-row {
  display: flex; justify-content: space-between; padding: 6px 0;
  font-size: 14px; color: #475569;
}
.apply-btn { width: 100%; margin-top: 16px; }
</style>