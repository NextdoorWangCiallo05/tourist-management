<template>
  <AppLayout activeMenu="audit-logs" breadcrumb="操作日志" :headerIcon="List">
    <div class="toolbar">
      <el-input v-model="filterAction" placeholder="按操作类型筛选" clearable style="width:200px" @keyup.enter="loadLogs" />
      <el-button type="primary" @click="loadLogs"><el-icon><Search /></el-icon> 查询</el-button>
      <span style="color:#94a3b8;font-size:13px">共 {{ total }} 条记录</span>
    </div>
    <el-table :data="logs" class="data-table" v-loading="loading">
      <el-table-column prop="created_at" label="时间" width="170" />
      <el-table-column prop="username" label="操作人" width="100" />
      <el-table-column prop="action" label="操作" width="120">
        <template #default="scope">
          <el-tag :type="getActionType(scope.row.action)" size="small" effect="plain">{{ scope.row.action }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="target_type" label="对象类型" width="100" />
      <el-table-column prop="target_id" label="对象编号" width="160" />
      <el-table-column prop="detail" label="详情" min-width="300" />
    </el-table>
    <div class="pagination-wrap" v-if="pages > 1">
      <el-pagination background layout="prev, pager, next" :total="total" :page-size="50" v-model:current-page="page" @current-change="loadLogs" />
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '../utils/request'
import {
  Monitor, Plus, Document, Search, Suitcase, MapLocation,
  Printer, Download, SwitchButton, Calendar, List
} from '@element-plus/icons-vue'
import AppLayout from '../components/AppLayout.vue'

const logs = ref([])
const total = ref(0)
const pages = ref(1)
const page = ref(1)
const filterAction = ref('')
const loading = ref(false)

const loadLogs = async () => {
  loading.value = true
  try {
    const params = { page: page.value, per_page: 50 }
    if (filterAction.value) params.action = filterAction.value
    const res = await request.get('/audit_logs', { params })
    logs.value = res.logs
    total.value = res.total
    pages.value = res.pages
  } catch (error) {
    console.error('Failed to load audit logs:', error)
  } finally {
    loading.value = false
  }
}

const getActionType = (action) => {
  if (action.includes('登录')) return ''
  if (action.includes('新建') || action.includes('导入')) return 'success'
  if (action.includes('取消') || action.includes('失败')) return 'danger'
  if (action.includes('支付')) return 'warning'
  return 'info'
}

onMounted(() => { loadLogs() })
</script>

<style scoped>
.toolbar { display: flex; gap: 12px; margin-bottom: 20px; align-items: center; }
.data-table { width: 100%; }
.data-table :deep(.el-table__header th) { background: #f8fafc; color: #475569; font-weight: 600; }
.pagination-wrap { margin-top: 20px; display: flex; justify-content: center; }
</style>
