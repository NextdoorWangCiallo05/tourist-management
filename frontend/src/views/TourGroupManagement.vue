<template>
  <AppLayout activeMenu="tour-group-mgmt" breadcrumb="旅游团管理" :headerIcon="Suitcase">
    <div class="toolbar">
      <el-input v-model="searchText" placeholder="搜索旅游团名称或代码" clearable style="width:300px" @keyup.enter="searchGroups" />
      <el-button type="primary" @click="searchGroups"><el-icon><Search /></el-icon> 搜索</el-button>
      <el-button type="success" @click="showAddDialog = true"><el-icon><Plus /></el-icon> 新增旅游团</el-button>
    </div>
    <el-table :data="filteredGroups" class="data-table">
      <el-table-column prop="group_code" label="旅游团代码" width="130" />
      <el-table-column prop="route_code" label="路线代码" width="100" />
      <el-table-column prop="route_name" label="路线名称" min-width="180" />
      <el-table-column prop="departure_date" label="出发日期" width="120" />
      <el-table-column prop="deadline_date" label="报名截止" width="120" />
      <el-table-column prop="max_capacity" label="最大容量" width="100" />
      <el-table-column prop="adult_price" label="成人价" width="100">
        <template #default="scope">¥{{ scope.row.adult_price }}</template>
      </el-table-column>
      <el-table-column prop="child_price" label="儿童价" width="100">
        <template #default="scope">¥{{ scope.row.child_price }}</template>
      </el-table-column>
      <el-table-column prop="is_public" label="公开" width="80">
        <template #default="scope">
          <el-tag :type="scope.row.is_public ? 'success' : 'info'" effect="dark" size="small" round>
            {{ scope.row.is_public ? '是' : '否' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="scope">
          <el-button size="small" @click="editGroup(scope.row)">编辑</el-button>
          <el-button size="small" type="warning" plain @click="editPrices(scope.row)">价格</el-button>
          <el-button size="small" :type="scope.row.is_public ? 'success' : 'info'" plain @click="togglePublic(scope.row)">
            {{ scope.row.is_public ? '公开' : '不公开' }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </AppLayout>
  <el-dialog v-model="showAddDialog" :title="isEditing ? '编辑旅游团' : '新增旅游团'" width="550px">
    <el-form :model="groupForm" label-width="110px">
      <el-form-item label="旅游团代码"><el-input v-model="groupForm.group_code" /></el-form-item>
      <el-form-item label="路线">
        <el-select v-model="groupForm.route_id" placeholder="请选择路线" style="width:100%">
          <el-option v-for="r in routes" :key="r.id" :label="`${r.route_code} - ${r.route_name}`" :value="r.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="出发日期"><el-date-picker v-model="groupForm.departure_date" type="date" style="width:100%" value-format="YYYY-MM-DD" /></el-form-item>
      <el-form-item label="报名截止日期"><el-date-picker v-model="groupForm.deadline_date" type="date" style="width:100%" value-format="YYYY-MM-DD" /></el-form-item>
      <el-form-item label="最大容量"><el-input-number v-model="groupForm.max_capacity" :min="1" style="width:100%" /></el-form-item>
      <el-form-item label="成人价格"><el-input-number v-model="groupForm.adult_price" :min="0" :precision="2" style="width:100%" /></el-form-item>
      <el-form-item label="儿童价格"><el-input-number v-model="groupForm.child_price" :min="0" :precision="2" style="width:100%" /></el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="showAddDialog = false">取消</el-button>
      <el-button type="primary" @click="saveGroup">保存</el-button>
    </template>
  </el-dialog>
  <el-dialog v-model="showPriceDialog" title="编辑价格" width="400px">
    <el-form :model="priceForm" label-width="100px">
      <el-form-item label="成人价格"><el-input-number v-model="priceForm.adult_price" :min="0" :precision="2" style="width:100%" /></el-form-item>
      <el-form-item label="儿童价格"><el-input-number v-model="priceForm.child_price" :min="0" :precision="2" style="width:100%" /></el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="showPriceDialog = false">取消</el-button>
      <el-button type="primary" @click="savePrices">保存</el-button>
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
const groups = ref([])
const routes = ref([])
const searchText = ref('')
const showAddDialog = ref(false)
const isEditing = ref(false)
const editingId = ref(null)
const showPriceDialog = ref(false)
const priceGroupId = ref(null)
const groupForm = ref({
  group_code: '', route_id: null, departure_date: '', deadline_date: '',
  max_capacity: 20, adult_price: 0, child_price: 0
})
const priceForm = ref({ adult_price: 0, child_price: 0 })

const filteredGroups = computed(() => {
  if (!searchText.value) return groups.value
  const q = searchText.value
  return groups.value.filter(g => g.route_name?.includes(q) || g.group_code?.includes(q))
})

const navigate = (path) => { router.push(path) }

const loadGroups = async () => {
  try {
    const res = await request.get('/tour_groups/all')
    groups.value = res
  } catch (error) {
    console.error('Failed to load groups:', error)
  }
}

const loadRoutes = async () => {
  try {
    const res = await request.get('/routes')
    routes.value = res
  } catch (error) {
    console.error('Failed to load routes:', error)
  }
}

const searchGroups = () => {}

const editGroup = (group) => {
  isEditing.value = true
  editingId.value = group.id
  groupForm.value = {
    group_code: group.group_code,
    route_id: group.route_id,
    departure_date: group.departure_date,
    deadline_date: group.deadline_date,
    max_capacity: group.max_capacity,
    adult_price: group.adult_price,
    child_price: group.child_price
  }
  showAddDialog.value = true
}

const saveGroup = async () => {
  try {
    if (isEditing.value) {
      const updateData = {
        route_id: groupForm.value.route_id,
        departure_date: groupForm.value.departure_date,
        deadline_date: groupForm.value.deadline_date,
        max_capacity: groupForm.value.max_capacity,
        adult_price: groupForm.value.adult_price,
        child_price: groupForm.value.child_price
      }
      await request.put(`/tour_groups/${editingId.value}`, updateData)
    } else {
      await request.post('/tour_groups', groupForm.value)
    }
    showAddDialog.value = false
    isEditing.value = false
    editingId.value = null
    groupForm.value = { group_code: '', route_id: null, departure_date: '', deadline_date: '', max_capacity: 20, adult_price: 0, child_price: 0 }
    loadGroups()
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const editPrices = (group) => {
  priceGroupId.value = group.id
  priceForm.value = { adult_price: group.adult_price, child_price: group.child_price }
  showPriceDialog.value = true
}

const savePrices = async () => {
  try {
    await request.put(`/tour_groups/${priceGroupId.value}/price`, priceForm.value)
    showPriceDialog.value = false
    loadGroups()
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const togglePublic = async (group) => {
  try {
    if (group.is_public) {
      await request.post(`/tour_groups/${group.id}/unpublish`)
    } else {
      await request.post(`/tour_groups/${group.id}/publish`)
    }
    loadGroups()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

onMounted(() => { loadGroups(); loadRoutes() })
</script>

<style scoped>
.toolbar { display: flex; gap: 12px; margin-bottom: 20px; align-items: center; }
.data-table { width: 100%; }
.data-table :deep(.el-table__header th) { background: #f8fafc; color: #475569; font-weight: 600; }
</style>