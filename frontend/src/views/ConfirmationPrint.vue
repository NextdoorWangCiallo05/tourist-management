<template>
  <AppLayout activeMenu="confirmations" :breadcrumb="$t('confirmation.title')" :headerIcon="Printer">
    <div class="page-toolbar">
      <span class="toolbar-title">{{ $t('confirmation.yesterdayList') }}</span>
      <div class="toolbar-right">
        <el-button type="primary" @click="loadConfirmations"><el-icon><Refresh /></el-icon> {{ $t('confirmation.getData') }}</el-button>
        <el-button v-if="confirmations.length > 0" @click="printAll"><el-icon><Printer /></el-icon> {{ $t('confirmation.printAll') }}</el-button>
      </div>
    </div>
    <div v-if="confirmations.length > 0" class="confirmation-grid">
      <div v-for="item in confirmations" :key="item.application_no" class="confirmation-card">
        <div class="card-header">
          <div class="card-header-left">
            <el-icon class="card-icon"><Document /></el-icon>
            <h3>{{ $t('app.name') }}</h3>
          </div>
          <el-tag size="small" effect="plain" type="primary">{{ item.application_no }}</el-tag>
        </div>
        <div class="card-body">
          <div class="info-grid">
            <div class="info-item"><span class="label">{{ $t('confirmation.routeName') }}</span><span class="value">{{ item.route_name }}</span></div>
            <div class="info-item"><span class="label">{{ $t('confirmation.groupCode') }}</span><span class="value">{{ item.group_code }}</span></div>
            <div class="info-item"><span class="label">{{ $t('confirmation.departureDate') }}</span><span class="value">{{ item.departure_date }}</span></div>
            <div class="info-item"><span class="label">{{ $t('confirmation.responsible') }}</span><span class="value">{{ item.responsible_name }}</span></div>
            <div class="info-item"><span class="label">{{ $t('confirmation.phone') }}</span><span class="value">{{ item.responsible_phone }}</span></div>
            <div class="info-item"><span class="label">{{ $t('confirmation.persons') }}</span><span class="value">{{ $t('confirmation.adult') }} {{ item.adult_count }} / {{ $t('confirmation.child') }} {{ item.child_count }}</span></div>
            <div class="info-item highlight"><span class="label">{{ $t('confirmation.totalAmount') }}</span><span class="value amount">¥{{ fmt(item.total_amount) }}</span></div>
          </div>
          <div v-if="item.print_balance_notice" class="balance-section">
            <div class="balance-header"><el-icon><Money /></el-icon> {{ $t('confirmation.printBalanceNotice') }}</div>
            <div class="info-grid">
              <div class="info-item"><span class="label">{{ $t('confirmation.balance') }}</span><span class="value amount">¥{{ fmt(item.total_amount - (item.deposit_paid ? item.total_amount * 0.2 : 0)) }}</span></div>
              <div class="info-item"><span class="label">{{ $t('application.balanceDueDate') }}</span><span class="value">{{ item.balance_due_date }}</span></div>
            </div>
          </div>
        </div>
        <div class="card-footer">
          <el-button type="primary" plain @click="printSingle(item.application_no)"><el-icon><Printer /></el-icon> {{ $t('confirmation.printOne') }}</el-button>
          <el-button type="success" plain @click="downloadPdf(item.application_no)"><el-icon><Download /></el-icon> {{ $t('confirmation.pdf') }}</el-button>
        </div>
      </div>
    </div>
    <div v-else class="empty-state">
      <el-empty :description="$t('confirmation.noData')" />
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import request from '../utils/request'
import { ElMessage } from 'element-plus'
import {
  Monitor, Plus, Document, Search, Suitcase, MapLocation,
  Printer, Download, SwitchButton, Calendar, Refresh, Money
} from '@element-plus/icons-vue'
import AppLayout from '../components/AppLayout.vue'

const router = useRouter()
const confirmations = ref([])

const navigate = (path) => { router.push(path) }

const fmt = (n) => Number(n || 0).toFixed(2)

const loadConfirmations = async () => {
  try {
    const today = new Date().toISOString().split('T')[0]
    const res = await request.get('/confirmations', { params: { date: today } })
    confirmations.value = res
  } catch (error) {
    console.error('Failed to load confirmations:', error)
  }
}

const printAll = () => { window.print() }
const printSingle = (appNo) => { ElMessage.info(`正在打印申请 ${appNo} 的确认书...`) }

const downloadPdf = async (appNo) => {
  const token = localStorage.getItem('token')
  try {
    const res = await fetch(`http://localhost:5000/api/confirmations/${appNo}/pdf`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (!res.ok) { ElMessage.error('下载失败'); return }
    const blob = await res.blob()
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `确认书_${appNo}.pdf`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  } catch (e) {
    ElMessage.error('下载失败：' + e.message)
  }
}

onMounted(() => { loadConfirmations() })
</script>

<style scoped>
.page-toolbar { display: flex; gap: 12px; margin-bottom: 16px; align-items: center; justify-content: space-between; }
.toolbar-right { display: flex; gap: 8px; }
.toolbar-title { font-size: 14px; font-weight: 600; color: var(--text-primary); }
.confirmation-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
.confirmation-card {
  background: var(--bg-card); border-radius: var(--radius-md); overflow: hidden;
  box-shadow: var(--shadow-sm); transition: all 0.2s ease;
}
.confirmation-card:hover { box-shadow: var(--shadow-md); }
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

@media (max-width: 768px) {
  .confirmation-grid { grid-template-columns: 1fr; }
  .toolbar { flex-wrap: wrap; }
  .card-footer { flex-direction: column; }
}
</style>
