<template>
  <AppLayout activeMenu="applications" :breadcrumb="$t('application.title')" :headerIcon="Document">
    <div class="page-toolbar">
      <el-input v-model="searchText" :placeholder="$t('common.search') + ' ' + $t('application.appNo') + ' / ' + $t('application.responsiblePerson')" clearable style="width:300px" @keyup.enter="searchApplications" />
      <div class="toolbar-right">
        <el-button @click="searchApplications"><el-icon><Search /></el-icon> {{ $t('common.search') }}</el-button>
        <el-button type="primary" @click="navigate('/applications/create')"><el-icon><Plus /></el-icon> {{ $t('application.create') }}</el-button>
        <el-dropdown v-if="selectedNos.length > 0" @command="handleBatchAction" style="margin-left:8px">
          <el-button type="danger">
            <el-icon><Delete /></el-icon> 批量操作 ({{ selectedNos.length }})<el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="batchDelete" style="color:#ef4444"><el-icon><Delete /></el-icon> 批量删除</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
    <div class="page-card">
      <el-table ref="tableRef" :data="applications" class="data-table" @selection-change="onSelectionChange">
      <el-table-column type="selection" width="45" />
      <el-table-column prop="application_no" :label="$t('application.appNo')" width="160" />
      <el-table-column prop="group_code" :label="$t('application.groupCode')" width="120" />
      <el-table-column prop="route_name" :label="$t('application.routeName')" min-width="160" />
      <el-table-column prop="departure_date" :label="$t('application.departureDate')" width="120" />
      <el-table-column prop="responsible_name" :label="$t('application.responsiblePerson')" width="100" />
      <el-table-column prop="status" :label="$t('common.status')" width="100">
        <template #default="scope">
          <el-tag :type="getStatusType(scope.row.status)" effect="dark" size="small" round>
            {{ getStatusText(scope.row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" :label="$t('common.createdAt')" width="180" />
      <el-table-column :label="$t('common.operation')" width="280" fixed="right">
        <template #default="scope">
          <el-button size="small" @click="viewDetail(scope.row.application_no)">{{ $t('common.detail') || '查看详情' }}</el-button>
          <el-button v-if="scope.row.status === 'pending'" size="small" type="danger" plain @click="cancelApplication(scope.row.application_no)">{{ $t('common.cancel') }}</el-button>
          <el-button size="small" type="danger" plain @click="deleteSingle(scope.row)"><el-icon><Delete /></el-icon> 删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    </div>
    <div class="pagination-wrap" v-if="pages > 1">
      <el-pagination background layout="prev, pager, next" :total="total" :page-size="20" v-model:current-page="page" @current-change="loadApplications" />
    </div>
  </AppLayout>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import request from '../utils/request'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Monitor, Plus, Document, Search, Suitcase, MapLocation,
  Printer, Download, SwitchButton, Calendar, Delete, ArrowDown
} from '@element-plus/icons-vue'
import AppLayout from '../components/AppLayout.vue'

const router = useRouter()
const { t } = useI18n()
const applications = ref([])
const searchText = ref('')
const selectedNos = ref([])
const tableRef = ref(null)
const page = ref(1)
const total = ref(0)
const pages = ref(0)

const navigate = (path) => { router.push(path) }

const loadApplications = async () => {
  try {
    const params = { page: page.value, per_page: 20 }
    if (searchText.value) {
      params.responsible_name = searchText.value
      params.application_no = searchText.value
    }
    const res = await request.get('/applications', { params })
    applications.value = Array.isArray(res) ? res : (res.items || [])
    if (!Array.isArray(res)) {
      total.value = res.total || 0
      pages.value = res.pages || 0
    }
  } catch (error) {
    console.error('Failed to load applications:', error)
  }
}

const searchApplications = async () => {
  page.value = 1
  loadApplications()
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
  const texts = { pending: t('application.statusPending'), completed: t('application.statusCompleted'), cancelled: t('application.statusCancelled') }
  return texts[status] || status
}

const onSelectionChange = (rows) => {
  selectedNos.value = rows.map(r => r.application_no)
}

const deleteSingle = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确认删除申请 <b>${row.application_no}</b>？<br><br><span style="color:#ef4444">⚠️ 此操作将永久删除该申请及其所有参加者、支付记录</span>`,
      '确认删除',
      { confirmButtonText: '确认删除', cancelButtonText: '取消', type: 'error', dangerouslyUseHTMLString: true }
    )
    await request.delete(`/applications/${row.application_no}`)
    ElMessage.success('申请已删除')
    loadApplications()
  } catch (e) { if (e !== 'cancel') ElMessage.error('删除失败') }
}

const handleBatchAction = (command) => {
  if (command === 'batchDelete') batchDelete()
}

const batchDelete = async () => {
  try {
    await ElMessageBox.confirm(
      `确认批量删除 <b>${selectedNos.value.length}</b> 条申请？<br><br><span style="color:#ef4444">⚠️ 此操作将永久删除所选申请及其所有关联数据</span>`,
      '批量删除',
      { confirmButtonText: '确认删除', cancelButtonText: '取消', type: 'error', dangerouslyUseHTMLString: true }
    )
    const res = await request.post('/applications/batch-delete', { application_nos: selectedNos.value })
    ElMessage.success(`已删除 ${res.count} 条申请`)
    selectedNos.value = []
    loadApplications()
  } catch (e) { if (e !== 'cancel') ElMessage.error('批量删除失败') }
}

onMounted(() => { loadApplications() })
</script>

<style scoped>
.page-toolbar { display: flex; gap: 12px; margin-bottom: 16px; align-items: center; justify-content: space-between; }
.toolbar-right { display: flex; gap: 8px; }
.page-card { background: var(--bg-card); border-radius: var(--radius-md); box-shadow: var(--shadow-sm); overflow: hidden; }
.data-table { width: 100%; }
.data-table :deep(.el-table__header th) { background: #f8fafc; color: #475569; font-weight: 600; }
.pagination-wrap { margin-top: 20px; display: flex; justify-content: center; }
</style>
