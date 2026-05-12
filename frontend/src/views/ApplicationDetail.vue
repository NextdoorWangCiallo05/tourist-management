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
        <el-menu default-active="applications" class="sidebar-menu">
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
            <el-icon class="header-icon"><Document /></el-icon>
            <span class="breadcrumb">申请详情 / {{ application?.application_no }}</span>
          </div>
          <div class="header-right">
            <el-tag type="info" effect="plain" class="date-tag">
              <el-icon style="margin-right:4px"><Calendar /></el-icon>
              {{ currentDate }}
            </el-tag>
          </div>
        </el-header>
        <el-main class="content-area">
          <div v-if="loading" class="loading-state">
            <el-icon class="loading-icon" :size="32"><Loading /></el-icon>
            <p>加载中...</p>
          </div>
          <template v-else-if="application">
            <div class="detail-header">
              <div class="detail-header-left">
                <h2 class="detail-title">申请详情</h2>
                <el-tag :type="getStatusType(application.status)" effect="dark" size="small" round>
                  {{ getStatusText(application.status) }}
                </el-tag>
              </div>
              <div class="detail-header-actions">
                <el-button @click="navigate('/applications')"><el-icon><Back /></el-icon> 返回列表</el-button>
                <el-button v-if="application.status === 'pending'" type="danger" plain @click="cancelApplication">
                  <el-icon><Close /></el-icon> 取消申请
                </el-button>
              </div>
            </div>
            <div class="detail-grid">
              <div class="detail-card">
                <div class="detail-card-header"><el-icon><InfoFilled /></el-icon> 基本信息</div>
                <div class="detail-card-body">
                  <div class="detail-row"><span class="detail-label">申请编号</span><span>{{ application.application_no }}</span></div>
                  <div class="detail-row"><span class="detail-label">旅游团代码</span><span>{{ application.group_code }}</span></div>
                  <div class="detail-row"><span class="detail-label">路线名称</span><span>{{ application.route_name }}</span></div>
                  <div class="detail-row"><span class="detail-label">出发日期</span><span>{{ application.departure_date }}</span></div>
                  <div class="detail-row"><span class="detail-label">责任人</span><span>{{ application.responsible_name }}</span></div>
                  <div class="detail-row"><span class="detail-label">联系电话</span><span>{{ application.responsible_phone }}</span></div>
                  <div class="detail-row"><span class="detail-label">创建时间</span><span>{{ application.created_at }}</span></div>
                </div>
              </div>
              <div class="detail-card">
                <div class="detail-card-header"><el-icon><Money /></el-icon> 费用信息</div>
                <div class="detail-card-body">
                  <div class="detail-row"><span class="detail-label">成人人数</span><span>{{ application.adult_count }} 人</span></div>
                  <div class="detail-row"><span class="detail-label">儿童人数</span><span>{{ application.child_count }} 人</span></div>
                  <div class="detail-row"><span class="detail-label">成人单价</span><span>¥{{ application.adult_price }}</span></div>
                  <div class="detail-row"><span class="detail-label">儿童单价</span><span>¥{{ application.child_price }}</span></div>
                  <div class="detail-row"><span class="detail-label">总费用</span><span class="amount">¥{{ application.total_amount }}</span></div>
                  <div class="detail-row"><span class="detail-label">订金金额</span><span class="amount deposit">¥{{ application.deposit_amount }}</span></div>
                  <div class="detail-row"><span class="detail-label">订金支付截止</span><span>{{ application.deposit_due_date }}</span></div>
                  <div class="detail-row"><span class="detail-label">余款支付截止</span><span>{{ application.balance_due_date }}</span></div>
                </div>
              </div>
            </div>
            <div class="detail-card participants-card">
              <div class="detail-card-header"><el-icon><UserFilled /></el-icon> 参加者列表</div>
              <div class="detail-card-body">
                <el-table :data="application.participants" class="data-table">
                  <el-table-column prop="name" label="姓名" width="120" />
                  <el-table-column prop="id_type" label="证件类型" width="120" />
                  <el-table-column prop="id_number" label="证件号码" min-width="200" />
                  <el-table-column prop="phone" label="联系电话" width="140" />
                  <el-table-column prop="is_adult" label="类型" width="80">
                    <template #default="scope">
                      <el-tag :type="scope.row.is_adult ? 'primary' : 'success'" size="small" effect="plain">
                        {{ scope.row.is_adult ? '成人' : '儿童' }}
                      </el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column label="操作" width="160">
                    <template #default="scope">
                      <el-button size="small" @click="editParticipant(scope.row)">编辑</el-button>
                      <el-button size="small" type="danger" plain @click="removeParticipant(scope.row.id)">移除</el-button>
                    </template>
                  </el-table-column>
                </el-table>
                <el-button class="add-participant-btn" @click="showAddParticipant = true">
                  <el-icon><Plus /></el-icon> 添加参加者
                </el-button>
              </div>
            </div>
            <div class="action-bar">
              <el-button v-if="application.status === 'pending' && !application.deposit_paid" type="warning" size="large" @click="payDeposit">
                <el-icon><Money /></el-icon> 支付订金 (¥{{ application.deposit_amount }})
              </el-button>
              <el-button v-if="application.status === 'pending' && application.deposit_paid && !application.balance_paid" type="success" size="large" @click="payBalance">
                <el-icon><Money /></el-icon> 支付余款
              </el-button>
              <el-button v-if="application.status === 'pending' && application.deposit_paid" type="primary" size="large" @click="completeApplication">
                <el-icon><CircleCheck /></el-icon> 完成申请
              </el-button>
            </div>
          </template>
          <div v-else class="empty-state">
            <el-empty description="未找到申请信息" />
          </div>
        </el-main>
      </el-container>
    </el-container>
    <el-dialog v-model="showAddParticipant" title="添加参加者" width="500px">
      <el-form :model="newParticipant" label-width="80px">
        <el-form-item label="姓名"><el-input v-model="newParticipant.name" /></el-form-item>
        <el-form-item label="证件类型">
          <el-select v-model="newParticipant.id_type" style="width:100%">
            <el-option label="身份证" value="身份证" />
            <el-option label="护照" value="护照" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="证件号码"><el-input v-model="newParticipant.id_number" /></el-form-item>
        <el-form-item label="联系电话"><el-input v-model="newParticipant.phone" /></el-form-item>
        <el-form-item label="类型">
          <el-radio-group v-model="newParticipant.is_adult">
            <el-radio :label="true">成人</el-radio>
            <el-radio :label="false">儿童</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddParticipant = false">取消</el-button>
        <el-button type="primary" @click="addParticipant">确认添加</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'
import {
  Monitor, Plus, Document, Search, Suitcase, MapLocation,
  Printer, Download, SwitchButton, Calendar, InfoFilled,
  Money, UserFilled, Back, Close, CircleCheck, Loading
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const application = ref(null)
const loading = ref(true)
const showAddParticipant = ref(false)
const newParticipant = ref({ name: '', id_type: '身份证', id_number: '', phone: '', is_adult: true })

const currentDate = new Date().toLocaleDateString('zh-CN', {
  year: 'numeric', month: '2-digit', day: '2-digit', weekday: 'long'
})

const navigate = (path) => { router.push(path) }
const handleLogout = () => { localStorage.removeItem('token'); router.push('/') }

const loadApplication = async () => {
  try {
    const token = localStorage.getItem('token')
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
    const appNo = route.params.application_no
    const res = await axios.get(`/api/applications/${appNo}`)
    application.value = res.data
  } catch (error) {
    console.error('Failed to load application:', error)
  } finally {
    loading.value = false
  }
}

const getStatusType = (status) => {
  const types = { pending: 'warning', completed: 'success', cancelled: 'danger' }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = { pending: '处理中', completed: '已完成', cancelled: '已取消' }
  return texts[status] || status
}

const cancelApplication = async () => {
  if (!confirm('确定要取消此申请吗？')) return
  try {
    const token = localStorage.getItem('token')
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
    const res = await axios.post(`/api/applications/${application.value.application_no}/cancel`)
    alert(`取消成功！手续费: ${res.data.cancellation_fee}, 退款金额: ${res.data.refund_amount}`)
    loadApplication()
  } catch (error) {
    alert('取消失败')
  }
}

const payDeposit = async () => {
  if (!confirm(`确认支付订金 ¥${application.value.deposit_amount}？`)) return
  try {
    const token = localStorage.getItem('token')
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
    await axios.post(`/api/applications/${application.value.application_no}/pay_deposit`)
    alert('订金支付成功')
    loadApplication()
  } catch (error) {
    alert('支付失败')
  }
}

const payBalance = async () => {
  if (!confirm('确认支付余款？')) return
  try {
    const token = localStorage.getItem('token')
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
    await axios.post(`/api/applications/${application.value.application_no}/pay_balance`)
    alert('余款支付成功')
    loadApplication()
  } catch (error) {
    alert('支付失败')
  }
}

const completeApplication = async () => {
  if (!confirm('确认完成此申请？')) return
  try {
    const token = localStorage.getItem('token')
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
    await axios.post(`/api/applications/${application.value.application_no}/complete`)
    alert('申请已完成')
    loadApplication()
  } catch (error) {
    alert('操作失败')
  }
}

const addParticipant = async () => {
  try {
    const token = localStorage.getItem('token')
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
    await axios.post(`/api/applications/${application.value.application_no}/participants`, newParticipant.value)
    showAddParticipant.value = false
    newParticipant.value = { name: '', id_type: '身份证', id_number: '', phone: '', is_adult: true }
    loadApplication()
  } catch (error) {
    alert('添加失败')
  }
}

const editParticipant = (participant) => {
  alert(`编辑参加者: ${participant.name}`)
}

const removeParticipant = async (participantId) => {
  if (!confirm('确定移除该参加者？')) return
  try {
    const token = localStorage.getItem('token')
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
    await axios.delete(`/api/applications/${application.value.application_no}/participants/${participantId}`)
    loadApplication()
  } catch (error) {
    alert('移除失败')
  }
}

onMounted(() => { loadApplication() })
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

.loading-state { text-align: center; padding: 80px 0; color: #64748b; }
.loading-icon { animation: spin 1s linear infinite; }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

.detail-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 24px;
}
.detail-header-left { display: flex; align-items: center; gap: 12px; }
.detail-title { font-size: 20px; font-weight: 700; color: #0f172a; margin: 0; }
.detail-header-actions { display: flex; gap: 10px; }

.detail-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }
.detail-card {
  background: white; border-radius: 14px; overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.detail-card-header {
  display: flex; align-items: center; gap: 8px;
  padding: 16px 20px; background: #f8fafc; border-bottom: 1px solid #e2e8f0;
  font-weight: 600; color: #0f172a; font-size: 15px;
}
.detail-card-header .el-icon { color: #3b82f6; }
.detail-card-body { padding: 16px 20px; }
.detail-row {
  display: flex; justify-content: space-between; padding: 8px 0;
  border-bottom: 1px solid #f1f5f9; font-size: 14px;
}
.detail-row:last-child { border-bottom: none; }
.detail-label { color: #64748b; }
.amount { color: #0f172a; font-weight: 700; font-size: 16px; }
.amount.deposit { color: #f59e0b; }

.participants-card { margin-bottom: 20px; }
.data-table { width: 100%; }
.data-table :deep(.el-table__header th) { background: #f8fafc; color: #475569; font-weight: 600; }
.add-participant-btn { margin-top: 12px; width: 100%; }

.action-bar {
  display: flex; gap: 12px; padding: 20px; background: white;
  border-radius: 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.04);
  justify-content: center;
}

.empty-state { padding: 60px 0; }
</style>