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
        <el-menu default-active="confirmations" class="sidebar-menu">
          <el-menu-item index="dashboard" @click="navigate('/dashboard')"><el-icon><Monitor /></el-icon><span>首页概览</span></el-menu-item>
          <el-menu-item index="create-app" @click="navigate('/applications/create')"><el-icon><Plus /></el-icon><span>新建申请</span></el-menu-item>
          <el-menu-item index="applications" @click="navigate('/applications')"><el-icon><Document /></el-icon><span>申请管理</span></el-menu-item>
          <el-menu-item index="tour-groups" @click="navigate('/tour-groups')"><el-icon><Search /></el-icon><span>旅游团查询</span></el-menu-item>
          <el-menu-item index="tour-group-mgmt" @click="navigate('/tour-group-management')"><el-icon><Suitcase /></el-icon><span>旅游团管理</span></el-menu-item>
          <el-menu-item index="routes" @click="navigate('/routes')"><el-icon><MapLocation /></el-icon><span>路线管理</span></el-menu-item>
          <el-menu-item index="confirmations" @click="navigate('/confirmations')"><el-icon><Printer /></el-icon><span>确认书打印</span></el-menu-item>
          <el-menu-item index="export" @click="navigate('/daily-export')"><el-icon><Download /></el-icon><span>财务导出</span></el-menu-item>
        </el-menu>
        <div class="sidebar-footer">
          <div class="user-info">
            <div class="user-avatar"><span class="avatar-text">王</span></div>
            <div class="user-detail">
              <span class="user-name">王经理</span>
              <span class="user-role">高级操作员</span>
            </div>
          </div>
          <el-button @click="handleLogout" class="logout-btn"><el-icon><SwitchButton /></el-icon> 退出登录</el-button>
        </div>
      </el-aside>
      <el-container class="main-content">
        <el-header class="top-header">
          <div class="header-left">
            <el-icon class="header-icon"><Printer /></el-icon>
            <span class="breadcrumb">确认书打印</span>
          </div>
          <div class="header-right">
            <el-tag type="info" effect="plain" class="date-tag">
              <el-icon style="margin-right:4px"><Calendar /></el-icon>
              {{ currentDate }}
            </el-tag>
          </div>
        </el-header>
        <el-main class="content-area">
          <div class="toolbar">
            <el-button type="primary" @click="loadConfirmations"><el-icon><Refresh /></el-icon> 获取昨日确认数据</el-button>
            <el-button v-if="confirmations.length > 0" @click="printAll"><el-icon><Printer /></el-icon> 打印全部</el-button>
          </div>
          <div v-if="confirmations.length > 0" class="confirmation-grid">
            <div v-for="item in confirmations" :key="item.application_no" class="confirmation-card">
              <div class="card-header">
                <div class="card-header-left">
                  <el-icon class="card-icon"><Document /></el-icon>
                  <h3>旅游确认书</h3>
                </div>
                <el-tag size="small" effect="plain" type="primary">{{ item.application_no }}</el-tag>
              </div>
              <div class="card-body">
                <div class="info-grid">
                  <div class="info-item"><span class="label">路线名称</span><span class="value">{{ item.route_name }}</span></div>
                  <div class="info-item"><span class="label">旅游团</span><span class="value">{{ item.group_code }}</span></div>
                  <div class="info-item"><span class="label">出发日期</span><span class="value">{{ item.departure_date }}</span></div>
                  <div class="info-item"><span class="label">责任人</span><span class="value">{{ item.responsible_name }}</span></div>
                  <div class="info-item"><span class="label">联系电话</span><span class="value">{{ item.responsible_phone }}</span></div>
                  <div class="info-item"><span class="label">人数</span><span class="value">成人 {{ item.adult_count }} / 儿童 {{ item.child_count }}</span></div>
                  <div class="info-item highlight"><span class="label">总费用</span><span class="value amount">¥{{ item.total_amount }}</span></div>
                </div>
                <div v-if="item.print_balance_notice" class="balance-section">
                  <div class="balance-header"><el-icon><Money /></el-icon> 余额交款单</div>
                  <div class="info-grid">
                    <div class="info-item"><span class="label">余额金额</span><span class="value amount">¥{{ item.total_amount - (item.deposit_paid ? item.total_amount * 0.2 : 0) }}</span></div>
                    <div class="info-item"><span class="label">支付截止日期</span><span class="value">{{ item.balance_due_date }}</span></div>
                  </div>
                </div>
              </div>
              <div class="card-footer">
                <el-button type="primary" plain @click="printSingle(item.application_no)"><el-icon><Printer /></el-icon> 打印此份</el-button>
              </div>
            </div>
          </div>
          <div v-else class="empty-state">
            <el-empty description="暂无需要打印的确认书" />
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
  Printer, Download, SwitchButton, Calendar, Refresh, Money
} from '@element-plus/icons-vue'

const router = useRouter()
const confirmations = ref([])

const currentDate = new Date().toLocaleDateString('zh-CN', {
  year: 'numeric', month: '2-digit', day: '2-digit', weekday: 'long'
})

const navigate = (path) => { router.push(path) }
const handleLogout = () => { localStorage.removeItem('token'); router.push('/') }

const loadConfirmations = async () => {
  try {
    const token = localStorage.getItem('token')
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
    const res = await axios.get('/api/confirmations')
    confirmations.value = res.data
  } catch (error) {
    console.error('Failed to load confirmations:', error)
  }
}

const printAll = () => { alert('正在打印全部确认书...') }
const printSingle = (appNo) => { alert(`正在打印申请 ${appNo} 的确认书...`) }

onMounted(() => { loadConfirmations() })
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

.toolbar { display: flex; gap: 12px; margin-bottom: 20px; align-items: center; }

.confirmation-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }
.confirmation-card {
  background: white; border-radius: 14px; overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04); transition: all 0.25s ease;
}
.confirmation-card:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,0,0,0.07); }
.card-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 16px 20px; background: #f8fafc; border-bottom: 1px solid #e2e8f0;
}
.card-header-left { display: flex; align-items: center; gap: 8px; }
.card-header-left h3 { margin: 0; font-size: 15px; color: #0f172a; }
.card-icon { color: #3b82f6; font-size: 18px; }
.card-body { padding: 20px; }
.info-grid { display: flex; flex-direction: column; gap: 8px; }
.info-item { display: flex; justify-content: space-between; font-size: 14px; }
.info-item .label { color: #64748b; }
.info-item .value { color: #0f172a; font-weight: 500; }
.info-item.highlight { padding-top: 8px; border-top: 1px solid #e2e8f0; }
.amount { color: #3b82f6; font-weight: 700; font-size: 16px; }
.balance-section {
  margin-top: 16px; padding: 16px; background: #fffbeb; border-radius: 10px;
  border: 1px solid #fde68a;
}
.balance-header {
  display: flex; align-items: center; gap: 6px; font-weight: 600;
  color: #d97706; margin-bottom: 10px; font-size: 14px;
}
.balance-header .el-icon { font-size: 16px; }
.card-footer { padding: 14px 20px; background: #f8fafc; border-top: 1px solid #e2e8f0; }
.card-footer .el-button { width: 100%; }

.empty-state { padding: 60px 0; }
</style>