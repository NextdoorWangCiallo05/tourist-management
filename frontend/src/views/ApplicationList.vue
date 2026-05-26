<template>
  <AppLayout activeMenu="applications" breadcrumb="申请管理" :headerIcon="Document">
    <div class="toolbar">
      <el-input v-model="searchText" placeholder="搜索申请编号或责任人" clearable style="width:300px" @keyup.enter="searchApplications" />
      <el-button type="primary" @click="searchApplications"><el-icon><Search /></el-icon> 搜索</el-button>
      <el-button @click="navigate('/applications/create')"><el-icon><Plus /></el-icon> 新建申请</el-button>
    </div>
    <el-table :data="applications" class="data-table">
      <el-table-column prop="application_no" label="申请编号" width="160" />
      <el-table-column prop="group_code" label="旅游团代码" width="120" />
      <el-table-column prop="route_name" label="路线名称" min-width="160" />
      <el-table-column prop="departure_date" label="出发日期" width="120" />
      <el-table-column prop="responsible_name" label="责任人" width="100" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="scope">
          <el-tag :type="getStatusType(scope.row.status)" effect="dark" size="small" round>
            {{ getStatusText(scope.row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="scope">
          <el-button size="small" @click="viewDetail(scope.row.application_no)">查看详情</el-button>
          <el-button v-if="scope.row.status === 'pending'" size="small" type="danger" plain @click="cancelApplication(scope.row.application_no)">取消</el-button>
        </template>
      </el-table-column>
    </el-table>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import request from '../utils/request'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Monitor, Plus, Document, Search, Suitcase, MapLocation,
  Printer, Download, SwitchButton, Calendar
} from '@element-plus/icons-vue'
import AppLayout from '../components/AppLayout.vue'

const router = useRouter()
const applications = ref([])
const searchText = ref('')

const navigate = (path) => { router.push(path) }

const loadApplications = async () => {
  try {
    const res = await request.get('/applications')
    applications.value = res
  } catch (error) {
    console.error('Failed to load applications:', error)
  }
}

const searchApplications = async () => {
  try {
    const params = searchText.value ? { responsible_name: searchText.value, application_no: searchText.value } : {}
    const res = await request.get('/applications', { params })
    applications.value = res
  } catch (error) {
    console.error('Failed to search applications:', error)
  }
}

const viewDetail = (appNo) => { router.push(`/applications/detail/${appNo}`) }

const cancelApplication = async (appNo) => {
  try {
    await ElMessageBox.confirm('确定要取消此申请吗？', '确认取消', { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' })
    const res = await request.post(`/applications/${appNo}/cancel`)
    ElMessage.success(`取消成功！手续费: ${res.cancellation_fee}, 退款金额: ${res.refund_amount}`)
    loadApplications()
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('取消失败')
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

onMounted(() => { loadApplications() })
</script>

<style scoped>
.toolbar { display: flex; gap: 12px; margin-bottom: 20px; align-items: center; }
.data-table { width: 100%; }
.data-table :deep(.el-table__header th) { background: #f8fafc; color: #475569; font-weight: 600; }
</style>
