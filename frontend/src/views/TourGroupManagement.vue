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
        <el-menu default-active="tour-group-mgmt" class="sidebar-menu">
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
            <el-icon class="header-icon"><Suitcase /></el-icon>
            <span class="breadcrumb">旅游团管理</span>
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
            <el-input v-model="searchText" placeholder="搜索旅游团名称或代码" clearable style="width:300px" @keyup.enter="searchGroups" />
            <el-button type="primary" @click="searchGroups"><el-icon><Search /></el-icon> 搜索</el-button>
            <el-button type="success" @click="showAddDialog = true"><el-icon><Plus /></el-icon> 新增旅游团</el-button>
          </div>
          <el-table :data="filteredGroups" class="data-table">
            <el-table-column prop="group_code" label="旅游团代码" width="130" />
            <el-table-column prop="route_code" label="路线代码" width="100" />
            <el-table-column prop="route_name" label="路线名称" min-width="180" />
            <el-table-column prop="departure_date" label="出发日期" width="120" />
            <el-table-column prop="deadline_date" label="报名截止" width="120" />
            <el-table-column prop="max_capacity" label="最大容量" width="100" />
            <el-table-column prop="adult_price" label="成人价" width="100">
              <template #default="scope">¥{{ scope.row.adult_price }}</template>
            </el-table-column>
            <el-table-column prop="child_price" label="儿童价" width="100">
              <template #default="scope">¥{{ scope.row.child_price }}</template>
            </el-table-column>
            <el-table-column prop="is_public" label="公开" width="80">
              <template #default="scope">
                <el-tag :type="scope.row.is_public ? 'success' : 'info'" effect="dark" size="small" round>
                  {{ scope.row.is_public ? '是' : '否' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="220" fixed="right">
              <template #default="scope">
                <el-button size="small" @click="editGroup(scope.row)">编辑</el-button>
                <el-button size="small" type="warning" plain @click="editPrices(scope.row)">价格</el-button>
                <el-button size="small" :type="scope.row.is_public ? 'success' : 'info'" plain @click="togglePublic(scope.row)">
                  {{ scope.row.is_public ? '公开' : '不公开' }}
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-main>
      </el-container>
    </el-container>
    <el-dialog v-model="showAddDialog" :title="isEditing ? '编辑旅游团' : '新增旅游团'" width="550px">
      <el-form :model="groupForm" label-width="110px">
        <el-form-item label="旅游团代码"><el-input v-model="groupForm.group_code" /></el-form-item>
        <el-form-item label="路线">
          <el-select v-model="groupForm.route_id" placeholder="请选择路线" style="width:100%">
            <el-option v-for="r in routes" :key="r.id" :label="`${r.route_code} - ${r.route_name}`" :value="r.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="出发日期"><el-date-picker v-model="groupForm.departure_date" type="date" style="width:100%" value-format="YYYY-MM-DD" /></el-form-item>
        <el-form-item label="报名截止日期"><el-date-picker v-model="groupForm.deadline_date" type="date" style="width:100%" value-format="YYYY-MM-DD" /></el-form-item>
        <el-form-item label="最大容量"><el-input-number v-model="groupForm.max_capacity" :min="1" style="width:100%" /></el-form-item>
        <el-form-item label="成人价格"><el-input-number v-model="groupForm.adult_price" :min="0" :precision="2" style="width:100%" /></el-form-item>
        <el-form-item label="儿童价格"><el-input-number v-model="groupForm.child_price" :min="0" :precision="2" style="width:100%" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="saveGroup">保存</el-button>
      </template>
    </el-dialog>
    <el-dialog v-model="showPriceDialog" title="编辑价格" width="400px">
      <el-form :model="priceForm" label-width="100px">
        <el-form-item label="成人价格"><el-input-number v-model="priceForm.adult_price" :min="0" :precision="2" style="width:100%" /></el-form-item>
        <el-form-item label="儿童价格"><el-input-number v-model="priceForm.child_price" :min="0" :precision="2" style="width:100%" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPriceDialog = false">取消</el-button>
        <el-button type="primary" @click="savePrices">保存</el-button>
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
const groups = ref([])
const routes = ref([])
const searchText = ref('')
const showAddDialog = ref(false)
const isEditing = ref(false)
const editingId = ref(null)
const showPriceDialog = ref(false)
const priceGroupId = ref(null)
const groupForm = ref({
  group_code: '', route_id: null, departure_date: '', deadline_date: '',
  max_capacity: 20, adult_price: 0, child_price: 0
})
const priceForm = ref({ adult_price: 0, child_price: 0 })

const currentDate = new Date().toLocaleDateString('zh-CN', {
  year: 'numeric', month: '2-digit', day: '2-digit', weekday: 'long'
})

const filteredGroups = computed(() => {
  if (!searchText.value) return groups.value
  const q = searchText.value
  return groups.value.filter(g => g.route_name?.includes(q) || g.group_code?.includes(q))
})

const navigate = (path) => { router.push(path) }
const handleLogout = () => { localStorage.removeItem('token'); router.push('/') }

const loadGroups = async () => {
  try {
    const token = localStorage.getItem('token')
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
    const res = await axios.get('/api/tour_groups/all')
    groups.value = res.data
  } catch (error) {
    console.error('Failed to load groups:', error)
  }
}

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

const searchGroups = () => {}

const editGroup = (group) => {
  isEditing.value = true
  editingId.value = group.id
  groupForm.value = {
    group_code: group.group_code,
    route_id: group.route_id,
    departure_date: group.departure_date,
    deadline_date: group.deadline_date,
    max_capacity: group.max_capacity,
    adult_price: group.adult_price,
    child_price: group.child_price
  }
  showAddDialog.value = true
}

const saveGroup = async () => {
  try {
    const token = localStorage.getItem('token')
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
    if (isEditing.value) {
      const { group_code, ...updateData } = groupForm.value
      await axios.put(`/api/tour_groups/${editingId.value}`, updateData)
    } else {
      await axios.post('/api/tour_groups', groupForm.value)
    }
    showAddDialog.value = false
    isEditing.value = false
    editingId.value = null
    groupForm.value = { group_code: '', route_id: null, departure_date: '', deadline_date: '', max_capacity: 20, adult_price: 0, child_price: 0 }
    loadGroups()
  } catch (error) {
    alert('保存失败')
  }
}

const editPrices = (group) => {
  priceGroupId.value = group.id
  priceForm.value = { adult_price: group.adult_price, child_price: group.child_price }
  showPriceDialog.value = true
}

const savePrices = async () => {
  try {
    const token = localStorage.getItem('token')
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
    await axios.put(`/api/tour_groups/${priceGroupId.value}/price`, priceForm.value)
    showPriceDialog.value = false
    loadGroups()
  } catch (error) {
    alert('保存失败')
  }
}

const togglePublic = async (group) => {
  try {
    const token = localStorage.getItem('token')
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
    if (group.is_public) {
      await axios.post(`/api/tour_groups/${group.id}/unpublish`)
    } else {
      await axios.post(`/api/tour_groups/${group.id}/publish`)
    }
    loadGroups()
  } catch (error) {
    alert('操作失败')
  }
}

onMounted(() => { loadGroups(); loadRoutes() })
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