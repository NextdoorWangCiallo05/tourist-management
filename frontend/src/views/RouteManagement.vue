<template>
  <AppLayout activeMenu="routes" breadcrumb="路线管理" :headerIcon="MapLocation">
    <div class="toolbar">
      <el-button type="success" @click="showAddDialog = true"><el-icon><Plus /></el-icon> 新增路线</el-button>
    </div>
    <el-table :data="routes" class="data-table">
      <el-table-column prop="route_code" label="路线代码" width="120" />
      <el-table-column prop="route_name" label="路线名称" min-width="200" />
      <el-table-column prop="description" label="描述" min-width="250" />
      <el-table-column prop="version" label="版本" width="80" />
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
          <el-button size="small" :type="scope.row.is_active ? 'danger' : 'success'" plain @click="toggleActive(scope.row)">
            {{ scope.row.is_active ? '停用' : '启用' }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </AppLayout>
  <el-dialog v-model="showAddDialog" :title="isEditing ? '编辑路线' : '新增路线'" width="500px">
    <el-form :model="routeForm" label-width="100px">
      <el-form-item label="路线代码"><el-input v-model="routeForm.route_code" :disabled="isEditing" /></el-form-item>
      <el-form-item label="路线名称"><el-input v-model="routeForm.route_name" /></el-form-item>
      <el-form-item label="描述"><el-input v-model="routeForm.description" type="textarea" :rows="3" /></el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="showAddDialog = false">取消</el-button>
      <el-button type="primary" @click="saveRoute">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import request from '../utils/request'
import { ElMessage } from 'element-plus'
import {
  Monitor, Plus, Document, Search, Suitcase, MapLocation,
  Printer, Download, SwitchButton, Calendar
} from '@element-plus/icons-vue'
import AppLayout from '../components/AppLayout.vue'

const router = useRouter()
const routes = ref([])
const showAddDialog = ref(false)
const isEditing = ref(false)
const editingId = ref(null)
const routeForm = ref({ route_code: '', route_name: '', description: '' })

const navigate = (path) => { router.push(path) }

const loadRoutes = async () => {
  try {
    const res = await request.get('/routes')
    routes.value = res
  } catch (error) {
    console.error('Failed to load routes:', error)
  }
}

const editRoute = (route) => {
  isEditing.value = true
  editingId.value = route.id
  routeForm.value = { route_code: route.route_code, route_name: route.route_name, description: route.description }
  showAddDialog.value = true
}

const saveRoute = async () => {
  try {
    if (isEditing.value) {
      await request.put(`/routes/${editingId.value}`, { route_name: routeForm.value.route_name, description: routeForm.value.description })
    } else {
      await request.post('/routes', routeForm.value)
    }
    showAddDialog.value = false
    isEditing.value = false
    editingId.value = null
    routeForm.value = { route_code: '', route_name: '', description: '' }
    loadRoutes()
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const toggleActive = async (route) => {
  try {
    if (route.is_active) {
      await request.post(`/routes/${route.id}/deactivate`)
    } else {
      await request.post(`/routes/${route.id}/activate`)
    }
    ElMessage.success(route.is_active ? '路线已停用' : '路线已启用')
    loadRoutes()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

onMounted(() => { loadRoutes() })
</script>

<style scoped>
.toolbar { display: flex; gap: 12px; margin-bottom: 20px; align-items: center; }
.data-table { width: 100%; }
.data-table :deep(.el-table__header th) { background: #f8fafc; color: #475569; font-weight: 600; }
</style>
