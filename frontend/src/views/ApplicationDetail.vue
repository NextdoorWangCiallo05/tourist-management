<template>
  <AppLayout activeMenu="applications" :breadcrumb="'申请详情 / ' + (application?.application_no || '')" :headerIcon="Document">
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
            <div class="detail-row"><span class="detail-label">旅游团代码</span><span>{{ application.tour_group_code }}</span></div>
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
            <div class="detail-row"><span class="detail-label">成人单价</span><span>¥{{ fmt(application.adult_price) }}</span></div>
            <div class="detail-row"><span class="detail-label">儿童单价</span><span>¥{{ fmt(application.child_price) }}</span></div>
            <div class="detail-row"><span class="detail-label">总费用</span><span class="amount">¥{{ fmt(application.total_amount) }}</span></div>
            <div class="detail-row"><span class="detail-label">订金金额</span><span class="amount deposit">¥{{ fmt(application.deposit_amount) }}</span></div>
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
          <el-icon><Money /></el-icon> 支付订金 (¥{{ fmt(application.deposit_amount) }})
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
  </AppLayout>
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
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import request from '../utils/request'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Monitor, Plus, Document, Search, Suitcase, MapLocation,
  Printer, Download, SwitchButton, Calendar, InfoFilled,
  Money, UserFilled, Back, Close, CircleCheck, Loading
} from '@element-plus/icons-vue'
import AppLayout from '../components/AppLayout.vue'

const router = useRouter()
const route = useRoute()
const application = ref(null)
const loading = ref(true)
const showAddParticipant = ref(false)
const newParticipant = ref({ name: '', id_type: '身份证', id_number: '', phone: '', is_adult: true })

const navigate = (path) => { router.push(path) }

const fmt = (n) => Number(n || 0).toFixed(2)

const loadApplication = async () => {
  try {
    const appNo = route.params.appNo
    const res = await request.get(`/applications/${appNo}`)
    application.value = res
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
  try {
    await ElMessageBox.confirm('确定要取消此申请吗？', '确认取消', { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' })
    const res = await request.post(`/applications/${application.value.application_no}/cancel`)
    ElMessage.success(`取消成功！手续费: ${res.cancellation_fee}, 退款金额: ${res.refund_amount}`)
    loadApplication()
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('取消失败')
  }
}

const payDeposit = async () => {
  try {
    await ElMessageBox.confirm(`确认支付订金 ¥${application.value.deposit_amount}？`, '支付确认', { confirmButtonText: '确认支付', cancelButtonText: '取消', type: 'warning' })
    await request.post(`/applications/${application.value.application_no}/deposit`, { amount_paid: application.value.deposit_amount })
    ElMessage.success('订金支付成功')
    loadApplication()
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('支付失败')
  }
}

const payBalance = async () => {
  try {
    await ElMessageBox.confirm('确认支付余款？', '支付确认', { confirmButtonText: '确认支付', cancelButtonText: '取消', type: 'warning' })
    await request.post(`/applications/${application.value.application_no}/balance`, { amount_paid: application.value.balance_amount })
    ElMessage.success('余款支付成功')
    loadApplication()
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('支付失败')
  }
}

const completeApplication = async () => {
  try {
    await ElMessageBox.confirm('确认完成此申请？', '完成确认', { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' })
    await request.post(`/applications/${application.value.application_no}/complete`)
    ElMessage.success('申请已完成')
    loadApplication()
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('操作失败')
  }
}

const addParticipant = async () => {
  try {
    await request.post(`/applications/${application.value.application_no}/participants`, newParticipant.value)
    showAddParticipant.value = false
    newParticipant.value = { name: '', id_type: '身份证', id_number: '', phone: '', is_adult: true }
    loadApplication()
    ElMessage.success('参加者添加成功')
  } catch (error) {
    ElMessage.error('添加失败')
  }
}

const editParticipant = (participant) => {
  ElMessage.info(`编辑参加者: ${participant.name}（功能开发中）`)
}

const removeParticipant = async (participantId) => {
  try {
    await ElMessageBox.confirm('确定移除该参加者？', '确认移除', { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' })
    await request.post(`/participants/${participantId}/cancel`)
    ElMessage.success('参加者已移除')
    loadApplication()
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('移除失败')
  }
}

onMounted(() => { loadApplication() })
</script>

<style scoped>
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