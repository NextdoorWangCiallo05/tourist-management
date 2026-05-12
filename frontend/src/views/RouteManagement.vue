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
        <el-menu default-active="routes" class="sidebar-menu">
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
            <el-icon class="header-icon"><MapLocation /></el-icon>
            <span class="breadcrumb">路线管理</span>
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
            <el-input v-model="searchText" placeholder="搜索路线名称或代码" clearable style="width:300px" @keyup.enter="searchRoutes" />
            <el-button type="primary" @click="searchRoutes"><el-icon><Search /></el-icon> 搜索</el-button>
            <el-button type="success" @click="showAddDialog = true"><el-icon><Plus /></el-icon> 新增路线</el-button>
          </div>
          <el-table :data="filteredRoutes" class="data-table">
            <el-table-column prop="route_code" label="路线代码" width="120" />
            <el-table-column prop="route_name" label="路线名称" min-width="200" />
            <el-table-column prop="destination" label="目的地" width="160" />
            <el-table-column prop="duration" label="行程天数" width="100" />
            <el-table-column prop="adult_price" label="成人价格" width="120">
              <template #default="scope">¥{{ scope.row.adult_price }}</template>
            </el-table-column>
            <el-table-column prop="child_price" label="儿童价格" width="120">
              <template #default="scope">¥{{ scope.row.child_price }}</template>
            </el-table-column>
            <el-table-column prop="is_active" label="状态" width="100">
              <template #default="scope">
                <el-tag :type="scope.row.is_active ? 'success' : 'danger'" effect="dark" size="small" round>
                  {{ scope.row.is_active ? '启用' : '停用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="scope">
                <el-button size="small" @click="editRoute(scope.row)">编辑</el-button>
                <el-button size="small" :type="scope.row.is_active ? 'warning' : 'success'" plain @click="toggleActive(scope.row)">
                  {{ scope.row.is_active ? '停用' : '启用' }}
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-main>
      </el-container>
    </el-container>
    <el-dialog v-model="showAddDialog" :title="isEditing ? '编辑路线' : '新增路线'" width="550px">
      <el-form :model="routeForm" label-width="100px">
        <el-form-item label="路线代码"><el-input v-model="routeForm.route_code" /></el-form-item>
        <el-form-item label="路线名称"><el-input v-model="routeForm.route_name" /></el-form-item>
        <el-form-item label="目的地"><el-input v-model="routeForm.destination" /></el-form-item>
        <el-form-item label="行程天数"><el-input-number v-model="routeForm.duration" :min="1" style="width:100%" /></el-form-item>
        <el-form-item label="成人价格"><el-input-number v-model="routeForm.adult_price" :min="0" :precision="2" style="width:100%" /></el-form-item>
        <el-form-item label="儿童价格"><el-input-number v-model="routeForm.child_price" :min="0" :precision="2" style="width:100%" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="saveRoute">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import {
  Monitor, Plus, Document, Search, Suitcase, MapLocation,
  Printer, Download, SwitchButton, Calendar
} from '@element-plus/icons-vue'

const router = useRouter()
const routes = ref([])
const searchText = ref('')
const showAddDialog = ref(false)
const isEditing = ref(false)
const editingId = ref(null)
const routeForm = ref({ route_code: '', route_name: '', destination: '', duration: 1, adult_price: 0, child_price: 0 })

const currentDate = new Date().toLocaleDateString('zh-CN', {
  year: 'numeric', month: '2-digit', day: '2-digit', weekday: 'long'
})

const filteredRoutes = computed(() => {
  if (!searchText.value) return routes.value
  const q = searchText.value
  return routes.value.filter(r => r.route_name?.includes(q) || r.route_code?.includes(q))
})

const navigate = (path) => { router.push(path) }
const handleLogout = () => { localStorage.removeItem('token'); router.push('/') }

const loadRoutes = async () => {
  try {
    const token = localStorage.getItem('token')
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
    const res = await axios.get('/api/routes')
    routes.value = res.data
  } catch (error) {
    console.error('Failed to load routes:', error)
  }
}

const searchRoutes = () => {}

const editRoute = (route) => {
  isEditing.value = true
  editingId.value = route.id
  routeForm.value = {
    route_code: route.route_code,
    route_name: route.route_name,
    destination: route.destination,
    duration: route.duration,
    adult_price: route.adult_price,
    child_price: route.child_price
  }
  showAddDialog.value = true
}

const saveRoute = async () => {
  try {
    const token = localStorage.getItem('token')
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
    if (isEditing.value) {
      await axios.put(`/api/routes/${editingId.value}`, routeForm.value)
    } else {
      await axios.post('/api/routes', routeForm.value)
    }
    showAddDialog.value = false
    isEditing.value = false
    editingId.value = null
    routeForm.value = { route_code: '', route_name: '', destination: '', duration: 1, adult_price: 0, child_price: 0 }
    loadRoutes()
  } catch (error) {
    alert('保存失败')
  }
}

const toggleActive = async (route) => {
  try {
    const token = localStorage.getItem('token')
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
    await axios.put(`/api/routes/${route.id}/toggle_active`)
    loadRoutes()
  } catch (error) {
    alert('操作失败')
  }
}

onMounted(() => { loadRoutes() })
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
.data-table { width: 100%; }
.data-table :deep(.el-table__header th) { background: #f8fafc; color: #475569; font-weight: 600; }
</style>