<template>
  <AppLayout activeMenu="tour-group-mgmt" :breadcrumb="$t('tourGroup.title')" :headerIcon="Suitcase">
    <div class="page-toolbar">
      <el-input v-model="searchText" :placeholder="$t('tourGroup.searchPlaceholder')" clearable style="width:300px" @keyup.enter="searchGroups" />
      <div class="toolbar-right">
        <el-button @click="searchGroups"><el-icon><Search /></el-icon> {{ $t('common.search') }}</el-button>
        <el-button type="primary" @click="showAddDialog = true"><el-icon><Plus /></el-icon> {{ $t('tourGroup.createGroup') }}</el-button>
      </div>
    </div>
    <div class="page-card">
      <el-table :data="filteredGroups" class="data-table">
        <el-table-column prop="group_code" :label="$t('tourGroup.code')" width="130" />
        <el-table-column prop="route_code" :label="$t('tourGroup.routeCode')" width="100" />
        <el-table-column prop="route_name" :label="$t('tourGroup.routeName')" min-width="180" />
        <el-table-column prop="departure_date" :label="$t('tourGroup.departureDate')" width="120" />
        <el-table-column prop="deadline_date" :label="$t('tourGroup.deadlineDate')" width="120" />
        <el-table-column prop="max_capacity" :label="$t('tourGroup.maxCapacity')" width="100" />
        <el-table-column prop="adult_price" :label="$t('tourGroup.adultPrice')" width="100">
          <template #default="scope">¥{{ scope.row.adult_price }}</template>
        </el-table-column>
        <el-table-column prop="child_price" :label="$t('tourGroup.childPrice')" width="100">
          <template #default="scope">¥{{ scope.row.child_price }}</template>
        </el-table-column>
        <el-table-column prop="is_public" :label="$t('tourGroup.isPublic')" width="80">
          <template #default="scope">
            <el-tag :type="scope.row.is_public ? 'success' : 'info'" effect="dark" size="small" round>
              {{ scope.row.is_public ? $t('tourGroup.yes') : $t('tourGroup.no') }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="$t('common.operation')" width="220" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="editGroup(scope.row)">{{ $t('tourGroup.edit') }}</el-button>
            <el-button size="small" type="warning" plain @click="editPrices(scope.row)">{{ $t('tourGroup.price') }}</el-button>
            <el-button size="small" :type="scope.row.is_public ? 'success' : 'info'" plain @click="togglePublic(scope.row)">
              {{ scope.row.is_public ? $t('tourGroup.yes') : $t('tourGroup.no') }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </AppLayout>
  <el-dialog v-model="showAddDialog" :title="isEditing ? $t('tourGroup.editGroup') : $t('tourGroup.newGroup')" width="550px">
    <el-form :model="groupForm" :label-width="$t('common.enabled').includes('Enabled') ? '140px' : '110px'">
      <el-form-item :label="$t('tourGroup.groupCodeLabel')"><el-input v-model="groupForm.group_code" /></el-form-item>
      <el-form-item :label="$t('tourGroup.routeLabel')">
        <el-select v-model="groupForm.route_id" :placeholder="$t('common.select')" style="width:100%">
          <el-option v-for="r in routes" :key="r.id" :label="`${r.route_code} - ${r.route_name}`" :value="r.id" />
        </el-select>
      </el-form-item>
      <el-form-item :label="$t('tourGroup.departureDate')"><el-date-picker v-model="groupForm.departure_date" type="date" style="width:100%" value-format="YYYY-MM-DD" /></el-form-item>
      <el-form-item :label="$t('tourGroup.deadlineDate')"><el-date-picker v-model="groupForm.deadline_date" type="date" style="width:100%" value-format="YYYY-MM-DD" /></el-form-item>
      <el-form-item :label="$t('tourGroup.capacityLabel')"><el-input-number v-model="groupForm.max_capacity" :min="1" style="width:100%" /></el-form-item>
      <el-form-item :label="$t('tourGroup.adultPriceLabel')"><el-input-number v-model="groupForm.adult_price" :min="0" :precision="2" style="width:100%" /></el-form-item>
      <el-form-item :label="$t('tourGroup.childPriceLabel')"><el-input-number v-model="groupForm.child_price" :min="0" :precision="2" style="width:100%" /></el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="showAddDialog = false">{{ $t('common.cancel') }}</el-button>
      <el-button type="primary" @click="saveGroup">{{ $t('common.save') }}</el-button>
    </template>
  </el-dialog>
  <el-dialog v-model="showPriceDialog" :title="$t('tourGroup.priceTitle')" width="400px">
    <el-form :model="priceForm" :label-width="$t('common.enabled').includes('Enabled') ? '120px' : '100px'">
      <el-form-item :label="$t('tourGroup.adultPriceLabel')"><el-input-number v-model="priceForm.adult_price" :min="0" :precision="2" style="width:100%" /></el-form-item>
      <el-form-item :label="$t('tourGroup.childPriceLabel')"><el-input-number v-model="priceForm.child_price" :min="0" :precision="2" style="width:100%" /></el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="showPriceDialog = false">{{ $t('common.cancel') }}</el-button>
      <el-button type="primary" @click="savePrices">{{ $t('common.save') }}</el-button>
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
.page-toolbar { display: flex; gap: 12px; margin-bottom: 16px; align-items: center; justify-content: space-between; }
.toolbar-right { display: flex; gap: 8px; }
.page-card { background: var(--bg-card); border-radius: var(--radius-md); box-shadow: var(--shadow-sm); overflow: hidden; }
.data-table { width: 100%; }
.data-table :deep(.el-table__header th) { background: #f8fafc; color: #475569; font-weight: 600; }
</style>