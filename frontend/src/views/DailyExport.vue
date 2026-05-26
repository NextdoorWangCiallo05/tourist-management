<template>
  <AppLayout activeMenu="export" breadcrumb="财务数据导出" :headerIcon="Download">
    <div class="toolbar">
      <el-button type="primary" @click="exportData"><el-icon><Download /></el-icon> 导出昨日数据</el-button>
      <el-button v-if="exportDataList.length > 0" @click="downloadCSV"><el-icon><Document /></el-icon> 下载CSV文件</el-button>
    </div>
    <div v-if="exportDataList.length > 0">
      <div class="summary-cards">
        <div class="summary-card">
          <div class="summary-icon"><el-icon :size="24"><Document /></el-icon></div>
          <div class="summary-info"><span class="summary-label">总笔数</span><span class="summary-value">{{ exportDataList.length }}</span></div>
        </div>
        <div class="summary-card">
          <div class="summary-icon deposit"><el-icon :size="24"><Money /></el-icon></div>
          <div class="summary-info"><span class="summary-label">订金收入</span><span class="summary-value deposit">¥{{ depositTotal }}</span></div>
        </div>
        <div class="summary-card">
          <div class="summary-icon balance"><el-icon :size="24"><Money /></el-icon></div>
          <div class="summary-info"><span class="summary-label">余款收入</span><span class="summary-value balance">¥{{ balanceTotal }}</span></div>
        </div>
        <div class="summary-card">
          <div class="summary-icon total"><el-icon :size="24"><Coin /></el-icon></div>
          <div class="summary-info"><span class="summary-label">总收入</span><span class="summary-value total">¥{{ totalAmount }}</span></div>
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
          <template #default="scope">¥{{ fmt(scope.row.amount) }}</template>
        </el-table-column>
        <el-table-column prop="paid_at" label="支付时间" width="180" />
      </el-table>
    </div>
    <div v-else class="empty-state">
      <el-empty description="暂无需要导出的数据" />
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import request from '../utils/request'
import { ElMessage } from 'element-plus'
import {
  Monitor, Plus, Document, Search, Suitcase, MapLocation,
  Printer, Download, SwitchButton, Calendar, Money, Coin
} from '@element-plus/icons-vue'
import AppLayout from '../components/AppLayout.vue'

const router = useRouter()
const exportDataList = ref([])

const navigate = (path) => { router.push(path) }

const fmt = (n) => Number(n || 0).toFixed(2)

const depositTotal = computed(() => {
  return exportDataList.value.filter(item => item.payment_type === 'deposit').reduce((sum, item) => sum + item.amount, 0).toFixed(2)
})
const balanceTotal = computed(() => {
  return exportDataList.value.filter(item => item.payment_type === 'balance').reduce((sum, item) => sum + item.amount, 0).toFixed(2)
})
const totalAmount = computed(() => {
  return exportDataList.value.reduce((sum, item) => sum + item.amount, 0).toFixed(2)
})

const exportData = async () => {
  try {
    const today = new Date().toISOString().split('T')[0]
    const res = await request.get('/daily_export', { params: { date: today } })
    exportDataList.value = res
    ElMessage.success('数据导出成功')
  } catch (error) {
    console.error('Failed to export data:', error)
  }
}

const downloadCSV = () => {
  if (exportDataList.value.length === 0) { ElMessage.warning('请先导出数据'); return }
  const headers = ['支付ID', '申请编号', '路线名称', '旅游团', '责任人', '支付类型', '金额', '支付时间']
  const rows = exportDataList.value.map(item => [
    item.payment_id, item.application_no, item.route_name, item.group_code,
    item.responsible_name, item.payment_type === 'deposit' ? '订金' : '余款', fmt(item.amount), item.paid_at
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
  ElMessage.success('CSV文件已下载')
}

onMounted(() => { exportData() })
</script>

<style scoped>
.toolbar { display: flex; gap: 12px; margin-bottom: 20px; align-items: center; }
.summary-cards { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 20px; }
.summary-card {
  background: white; border-radius: 12px; padding: 20px; display: flex;
  align-items: center; gap: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.summary-icon {
  width: 44px; height: 44px; border-radius: 10px; background: rgba(59,130,246,0.1);
  display: flex; align-items: center; justify-content: center; color: #3b82f6;
}
.summary-icon.deposit { background: rgba(245,158,11,0.1); color: #f59e0b; }
.summary-icon.balance { background: rgba(34,197,94,0.1); color: #22c55e; }
.summary-icon.total { background: rgba(59,130,246,0.1); color: #3b82f6; }
.summary-info { display: flex; flex-direction: column; gap: 2px; }
.summary-label { font-size: 13px; color: #94a3b8; }
.summary-value { font-size: 22px; font-weight: 700; color: #0f172a; }
.summary-value.deposit { color: #f59e0b; }
.summary-value.balance { color: #22c55e; }
.summary-value.total { color: #3b82f6; }
.data-table { width: 100%; }
.data-table :deep(.el-table__header th) { background: #f8fafc; color: #475569; font-weight: 600; }
.empty-state { padding: 60px 0; }
</style>
