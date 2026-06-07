<template>
  <AppLayout activeMenu="routes" :breadcrumb="$t('route.title')" :headerIcon="MapLocation">
    <div class="page-toolbar">
      <el-input v-model="searchText" :placeholder="$t('route.searchPlaceholder')" clearable style="width:300px" @keyup.enter="searchRoutes" />
      <div class="toolbar-right">
        <el-button @click="searchRoutes"><el-icon><Search /></el-icon> {{ $t('common.search') }}</el-button>
        <el-button type="primary" @click="showAddDialog = true"><el-icon><Plus /></el-icon> {{ $t('route.createRoute') }}</el-button>
      </div>
    </div>
    <div class="page-card">
      <el-table :data="filteredRoutes" class="data-table">
      <el-table-column prop="route_code" :label="$t('route.code')" width="120" />
      <el-table-column prop="route_name" :label="$t('route.name')" min-width="200" />
      <el-table-column prop="description" :label="$t('route.description')" min-width="250" />
      <el-table-column prop="version" :label="$t('route.version')" width="80" />
      <el-table-column prop="is_active" :label="$t('route.status')" width="100">
        <template #default="scope">
          <el-tag :type="scope.row.is_active ? 'success' : 'danger'" effect="dark" size="small" round>
            {{ scope.row.is_active ? $t('route.enabled') : $t('route.disabled') }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="$t('common.operation')" width="200" fixed="right">
        <template #default="scope">
          <el-button size="small" @click="editRoute(scope.row)">{{ $t('route.edit') }}</el-button>
          <el-button size="small" :type="scope.row.is_active ? 'danger' : 'success'" plain @click="toggleActive(scope.row)">
            {{ scope.row.is_active ? $t('route.toggle') : $t('route.toggleBack') }}
          </el-button>
        </template>
      </el-table-column>
      </el-table>
    </div>
  </AppLayout>
  <el-dialog v-model="showAddDialog" :title="isEditing ? $t('route.editRoute') : $t('route.newRoute')" width="500px">
    <el-form :model="routeForm" :label-width="$t('common.enabled').includes('Enabled') ? '120px' : '100px'">
      <el-form-item :label="$t('route.routeCodeLabel')"><el-input v-model="routeForm.route_code" :disabled="isEditing" /></el-form-item>
      <el-form-item :label="$t('route.routeNameLabel')"><el-input v-model="routeForm.route_name" /></el-form-item>
      <el-form-item :label="$t('route.descLabel')"><el-input v-model="routeForm.description" type="textarea" :rows="3" /></el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="showAddDialog = false">{{ $t('common.cancel') }}</el-button>
      <el-button type="primary" @click="saveRoute">{{ $t('common.save') }}</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
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
const searchText = ref('')
const showAddDialog = ref(false)
const isEditing = ref(false)
const editingId = ref(null)
const routeForm = ref({ route_code: '', route_name: '', description: '' })

const navigate = (path) => { router.push(path) }

const filteredRoutes = computed(() => {
  const s = searchText.value.toLowerCase()
  if (!s) return routes.value
  return routes.value.filter(r =>
    r.route_code?.toLowerCase().includes(s) || r.route_name?.toLowerCase().includes(s)
  )
})

const searchRoutes = () => {
}

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
.page-toolbar { display: flex; gap: 12px; margin-bottom: 16px; align-items: center; justify-content: space-between; }
.toolbar-right { display: flex; gap: 8px; }
.page-card { background: var(--bg-card); border-radius: var(--radius-md); box-shadow: var(--shadow-sm); overflow: hidden; }
.data-table { width: 100%; }
</style>
