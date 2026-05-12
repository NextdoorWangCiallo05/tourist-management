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
        <el-menu default-active="export" class="sidebar-menu">
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
            <el-icon class="header-icon"><Download /></el-icon>
            <span class="breadcrumb">财务数据导出</span>
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
            <el-button type="primary" @click="exportData"><el-icon><Download /></el-icon> 导出昨日数据</el-button>
            <el-button v-if="exportDataList.length > 0" @click="downloadCSV"><el-icon><Document /></el-icon> 下载CSV文件</el-button>
          </div>
          <div v-if="exportDataList.length > 0">
            <div class="summary-cards">
              <div class="summary-card">
                <div class="summary-icon"><el-icon :size="24"><Document /></el-icon></div>
                <div class="summary-info">
                  <span class="summary-label">总笔数</span>
                  <span class="summary-value">{{ exportDataList.length }}</span>
                </div>
              </div>
              <div class="summary-card">
                <div class="summary-icon deposit"><el-icon :size="24"><Money /></el-icon></div>
                <div class="summary-info">
                  <span class="summary-label">订金收入</span>
                  <span class="summary-value deposit">¥{{ depositTotal }}</span>
                </div>
              </div>
              <div class="summary-card">
                <div class="summary-icon balance"><el-icon :size="24"><Money /></el-icon></div>
                <div class="summary-info">
                  <span class="summary-label">余款收入</span>
                  <span class="summary-value balance">¥{{ balanceTotal }}</span>
                </div>
              </div>
              <div class="summary-card">
                <div class="summary-icon total"><el-icon :size="24"><Coin /></el-icon></div>
                <div class="summary-info">
                  <span class="summary-label">总收入</span>
                  <span class="summary-value total">¥{{ totalAmount }}</span>
                </div>
              </div>
            </div>
            <el-table :data="exportDataList" class="data-table">
              <el-table-column prop="payment_id" label="支付ID" width="100" />
              <el-table-column prop="application_no" label="申请编号" width="160" />
              <el-table-column prop="route_name" label="路线名称" min-width="160" />
              <el-table-column prop="group_code" label="旅游团" width="120" />
              <el-table-column prop="responsible_name" label="责任人" width="100" />
              <el-table-column prop="payment_type" label="支付类型" width="100">
                <template #default="scope">
                  <el-tag :type="scope.row.payment_type === 'deposit' ? 'warning' : 'success'" effect="dark" size="small" round>
                    {{ scope.row.payment_type === 'deposit' ? '订金' : '余款' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="amount" label="金额" width="120">
                <template #default="scope">¥{{ scope.row.amount }}</template>
              </el-table-column>
              <el-table-column prop="paid_at" label="支付时间" width="180" />
            </el-table>
          </div>
          <div v-else class="empty-state">
            <el-empty description="暂无需要导出的数据" />
          </div>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import {
  Monitor, Plus, Document, Search, Suitcase, MapLocation,
  Printer, Download, SwitchButton, Calendar, Money, Coin
} from '@element-plus/icons-vue'

const router = useRouter()
const exportDataList = ref([])

const currentDate = new Date().toLocaleDateString('zh-CN', {
  year: 'numeric', month: '2-digit', day: '2-digit', weekday: 'long'
})

const navigate = (path) => { router.push(path) }
const handleLogout = () => { localStorage.removeItem('token'); router.push('/') }

const depositTotal = computed(() => {
  return exportDataList.value
    .filter(item => item.payment_type === 'deposit')
    .reduce((sum, item) => sum + item.amount, 0)
    .toFixed(2)
})

const balanceTotal = computed(() => {
  return exportDataList.value
    .filter(item => item.payment_type === 'balance')
    .reduce((sum, item) => sum + item.amount, 0)
    .toFixed(2)
})

const totalAmount = computed(() => {
  return exportDataList.value
    .reduce((sum, item) => sum + item.amount, 0)
    .toFixed(2)
})

const exportData = async () => {
  try {
    const token = localStorage.getItem('token')
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
    const res = await axios.get('/api/daily_export')
    exportDataList.value = res.data
    alert('数据导出成功')
  } catch (error) {
    console.error('Failed to export data:', error)
  }
}

const downloadCSV = () => {
  if (exportDataList.value.length === 0) {
    alert('请先导出数据')
    return
  }
  const headers = ['支付ID', '申请编号', '路线名称', '旅游团', '责任人', '支付类型', '金额', '支付时间']
  const rows = exportDataList.value.map(item => [
    item.payment_id, item.application_no, item.route_name, item.group_code,
    item.responsible_name, item.payment_type === 'deposit' ? '订金' : '余款', item.amount, item.paid_at
  ])
  const csvContent = [headers.join(','), ...rows.map(row => row.join(','))].join('\n')
  const blob = new Blob([`\uFEFF${csvContent}`], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute('download', `financial_export_${new Date().toISOString().split('T')[0]}.csv`)
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  alert('CSV文件已下载')
}

onMounted(() => { exportData() })
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

.summary-cards { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }
.summary-card {
  display: flex; align-items: center; gap: 16px;
  background: white; padding: 20px; border-radius: 14px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04); transition: all 0.25s ease;
}
.summary-card:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,0,0,0.07); }
.summary-icon {
  width: 48px; height: 48px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  background: #eff6ff; color: #3b82f6;
}
.summary-icon.deposit { background: #fffbeb; color: #f59e0b; }
.summary-icon.balance { background: #f0fdf4; color: #22c55e; }
.summary-icon.total { background: linear-gradient(135deg, #eff6ff, #dbeafe); color: #3b82f6; }
.summary-info { display: flex; flex-direction: column; gap: 4px; }
.summary-label { font-size: 13px; color: #64748b; }
.summary-value { font-size: 22px; font-weight: 700; color: #0f172a; }
.summary-value.deposit { color: #f59e0b; }
.summary-value.balance { color: #22c55e; }
.summary-value.total { color: #3b82f6; }

.data-table { width: 100%; }
.data-table :deep(.el-table__header th) { background: #f8fafc; color: #475569; font-weight: 600; }

.empty-state { padding: 60px 0; }
</style>