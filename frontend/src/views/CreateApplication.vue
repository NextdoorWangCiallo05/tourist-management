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
        <el-menu default-active="create-app" class="sidebar-menu">
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
            <el-icon class="header-icon"><Plus /></el-icon>
            <span class="breadcrumb">新建申请</span>
          </div>
          <div class="header-right">
            <el-tag type="info" effect="plain" class="date-tag">
              <el-icon style="margin-right:4px"><Calendar /></el-icon>
              {{ currentDate }}
            </el-tag>
          </div>
        </el-header>
        <el-main class="content-area">
          <div class="form-card">
            <div class="form-card-header"><el-icon><InfoFilled /></el-icon> 选择旅游团</div>
            <div class="form-card-body">
              <el-form :model="form" label-width="100px">
                <el-form-item label="旅游团">
                  <el-select v-model="form.group_id" placeholder="请选择旅游团" style="width:100%" @change="onGroupChange">
                    <el-option v-for="g in groups" :key="g.id" :label="`${g.group_code} - ${g.route_name}`" :value="g.id" />
                  </el-select>
                </el-form-item>
                <el-form-item label="责任人">
                  <el-input v-model="form.responsible_name" placeholder="请输入责任人姓名" />
                </el-form-item>
                <el-form-item label="联系电话">
                  <el-input v-model="form.responsible_phone" placeholder="请输入联系电话" />
                </el-form-item>
              </el-form>
            </div>
          </div>
          <div v-if="selectedGroup" class="form-card">
            <div class="form-card-header"><el-icon><UserFilled /></el-icon> 参加者信息</div>
            <div class="form-card-body">
              <div class="participant-inputs">
                <div class="participant-row">
                  <el-input v-model="newParticipant.name" placeholder="姓名" style="width:140px" />
                  <el-select v-model="newParticipant.id_type" style="width:120px">
                    <el-option label="身份证" value="身份证" />
                    <el-option label="护照" value="护照" />
                  </el-select>
                  <el-input v-model="newParticipant.id_number" placeholder="证件号码" style="width:200px" />
                  <el-input v-model="newParticipant.phone" placeholder="电话" style="width:140px" />
                  <el-radio-group v-model="newParticipant.is_adult">
                    <el-radio :label="true">成人</el-radio>
                    <el-radio :label="false">儿童</el-radio>
                  </el-radio-group>
                  <el-button type="primary" @click="addParticipant"><el-icon><Plus /></el-icon> 添加</el-button>
                </div>
              </div>
              <el-table :data="participants" class="data-table" style="margin-top:12px">
                <el-table-column prop="name" label="姓名" width="120" />
                <el-table-column prop="id_type" label="证件类型" width="100" />
                <el-table-column prop="id_number" label="证件号码" width="200" />
                <el-table-column prop="phone" label="电话" width="140" />
                <el-table-column prop="is_adult" label="类型" width="80">
                  <template #default="scope">
                    <el-tag :type="scope.row.is_adult ? 'primary' : 'success'" size="small" effect="plain">
                      {{ scope.row.is_adult ? '成人' : '儿童' }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="80">
                  <template #default="scope">
                    <el-button size="small" type="danger" plain @click="removeParticipant(scope.$index)">删除</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </div>
          <div v-if="selectedGroup" class="form-card">
            <div class="form-card-header"><el-icon><Money /></el-icon> 费用预估</div>
            <div class="form-card-body">
              <div class="fee-grid">
                <div class="fee-item">
                  <span class="fee-label">成人单价</span>
                  <span class="fee-value">¥{{ selectedGroup.adult_price }}</span>
                </div>
                <div class="fee-item">
                  <span class="fee-label">儿童单价</span>
                  <span class="fee-value">¥{{ selectedGroup.child_price }}</span>
                </div>
                <div class="fee-item">
                  <span class="fee-label">成人人数</span>
                  <span class="fee-value">{{ adultCount }} 人</span>
                </div>
                <div class="fee-item">
                  <span class="fee-label">儿童人数</span>
                  <span class="fee-value">{{ childCount }} 人</span>
                </div>
                <div class="fee-item total">
                  <span class="fee-label">预估总费用</span>
                  <span class="fee-value highlight">¥{{ estimatedTotal }}</span>
                </div>
                <div class="fee-item">
                  <span class="fee-label">预估订金</span>
                  <span class="fee-value deposit">¥{{ estimatedDeposit }}</span>
                </div>
              </div>
            </div>
          </div>
          <div class="form-actions">
            <el-button size="large" @click="navigate('/applications')"><el-icon><Back /></el-icon> 返回</el-button>
            <el-button type="primary" size="large" :disabled="!canSubmit" @click="submitApplication">
              <el-icon><CircleCheck /></el-icon> 提交申请
            </el-button>
          </div>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'
import {
  Monitor, Plus, Document, Search, Suitcase, MapLocation,
  Printer, Download, SwitchButton, Calendar, InfoFilled,
  UserFilled, Money, Back, CircleCheck
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const groups = ref([])
const selectedGroup = ref(null)
const participants = ref([])
const newParticipant = ref({ name: '', id_type: '身份证', id_number: '', phone: '', is_adult: true })
const form = ref({ group_id: null, responsible_name: '', responsible_phone: '' })

const currentDate = new Date().toLocaleDateString('zh-CN', {
  year: 'numeric', month: '2-digit', day: '2-digit', weekday: 'long'
})

const adultCount = computed(() => participants.value.filter(p => p.is_adult).length)
const childCount = computed(() => participants.value.filter(p => !p.is_adult).length)
const estimatedTotal = computed(() => {
  if (!selectedGroup.value) return '0.00'
  return (adultCount.value * selectedGroup.value.adult_price + childCount.value * selectedGroup.value.child_price).toFixed(2)
})
const estimatedDeposit = computed(() => {
  if (!selectedGroup.value) return '0.00'
  const total = adultCount.value * selectedGroup.value.adult_price + childCount.value * selectedGroup.value.child_price
  return (total * 0.2).toFixed(2)
})
const canSubmit = computed(() => form.value.group_id && form.value.responsible_name && participants.value.length > 0)

const navigate = (path) => { router.push(path) }
const handleLogout = () => { localStorage.removeItem('token'); router.push('/') }

const loadGroups = async () => {
  try {
    const token = localStorage.getItem('token')
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
    const res = await axios.get('/api/tour_groups')
    groups.value = res.data
    if (route.query.groupId) {
      form.value.group_id = parseInt(route.query.groupId)
      onGroupChange(form.value.group_id)
    }
  } catch (error) {
    console.error('Failed to load groups:', error)
  }
}

const onGroupChange = (groupId) => {
  selectedGroup.value = groups.value.find(g => g.id === groupId) || null
}

const addParticipant = () => {
  if (!newParticipant.value.name || !newParticipant.value.id_number) {
    alert('请填写参加者姓名和证件号码')
    return
  }
  participants.value.push({ ...newParticipant.value })
  newParticipant.value = { name: '', id_type: '身份证', id_number: '', phone: '', is_adult: true }
}

const removeParticipant = (index) => {
  participants.value.splice(index, 1)
}

const submitApplication = async () => {
  try {
    const token = localStorage.getItem('token')
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
    const adultCount = participants.value.filter(p => p.is_adult).length
    const childCount = participants.value.filter(p => !p.is_adult).length
    const payload = {
      group_id: form.value.group_id,
      responsible_name: form.value.responsible_name,
      phone_number: form.value.responsible_phone,
      adult_count: adultCount,
      child_count: childCount
    }
    const res = await axios.post('/api/applications', payload)
    const appNo = res.data.application_no
    const participantPayload = {
      participants: participants.value.map(p => ({
        name: p.name,
        id_number: p.id_number,
        phone_number: p.phone,
        is_adult: p.is_adult
      }))
    }
    await axios.post(`/api/applications/${appNo}/participants`, participantPayload)
    alert(`申请创建成功！申请编号: ${appNo}`)
    router.push(`/applications/detail/${appNo}`)
  } catch (error) {
    alert('创建申请失败')
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

.form-card {
  background: white; border-radius: 14px; overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04); margin-bottom: 20px;
}
.form-card-header {
  display: flex; align-items: center; gap: 8px;
  padding: 16px 20px; background: #f8fafc; border-bottom: 1px solid #e2e8f0;
  font-weight: 600; color: #0f172a; font-size: 15px;
}
.form-card-header .el-icon { color: #3b82f6; }
.form-card-body { padding: 20px; }

.participant-row { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
.data-table { width: 100%; }
.data-table :deep(.el-table__header th) { background: #f8fafc; color: #475569; font-weight: 600; }

.fee-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.fee-item {
  display: flex; flex-direction: column; gap: 4px;
  padding: 16px; background: #f8fafc; border-radius: 10px;
}
.fee-label { font-size: 13px; color: #64748b; }
.fee-value { font-size: 20px; font-weight: 700; color: #0f172a; }
.fee-value.highlight { color: #3b82f6; font-size: 24px; }
.fee-value.deposit { color: #f59e0b; }
.fee-item.total { background: linear-gradient(135deg, #eff6ff, #dbeafe); }

.form-actions {
  display: flex; gap: 12px; justify-content: center;
  padding: 20px; background: white; border-radius: 14px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
</style>