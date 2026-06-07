<template>
  <AppLayout activeMenu="tour-groups" :breadcrumb="$t('tourGroup.query')" :headerIcon="Search">
    <div class="page-toolbar">
      <el-input v-model="searchText" :placeholder="$t('common.search') + '...'" clearable style="width:300px" @keyup.enter="searchGroups" />
      <div class="toolbar-right">
        <el-button @click="searchGroups"><el-icon><Search /></el-icon> {{ $t('common.search') }}</el-button>
      </div>
    </div>
    <div class="tour-group-grid">
      <div v-for="group in filteredGroups" :key="group.id" class="tour-card">
        <div class="card-header">
          <div class="card-header-left">
            <el-tag size="small" :type="canApply(group) ? 'success' : 'danger'" effect="dark" round>
              {{ canApply(group) ? $t('common.yes') : $t('common.no') }}
            </el-tag>
            <span class="group-code">{{ group.group_code }}</span>
          </div>
          <el-tag size="small" effect="plain" type="info">{{ group.route_code }}</el-tag>
        </div>
        <div class="card-body">
          <h3 class="route-name">{{ group.route_name }}</h3>
          <div class="info-rows">
            <div class="info-row"><el-icon><Calendar /></el-icon><span>{{ $t('tourGroup.departureDate') }}：{{ group.departure_date }}</span></div>
            <div class="info-row"><el-icon><Timer /></el-icon><span>{{ $t('tourGroup.deadlineDate') }}：{{ group.deadline_date }}</span></div>
            <div class="info-row"><el-icon><UserFilled /></el-icon><span>{{ $t('tourGroup.remaining') }}：<strong>{{ getRemainingCapacity(group) }} / {{ group.max_capacity }}</strong> {{ $t('common.person') }}</span></div>
          </div>
          <div class="price-row">
            <div class="price-item"><span class="price-label">{{ $t('common.adult') }}</span><span class="price-value">¥{{ group.adult_price }}</span></div>
            <div class="price-divider"></div>
            <div class="price-item"><span class="price-label">{{ $t('common.child') }}</span><span class="price-value">¥{{ group.child_price }}</span></div>
          </div>
        </div>
        <div class="card-footer">
          <el-button @click="checkAvailability(group)" :icon="InfoFilled">{{ $t('common.detail') }}</el-button>
          <el-button type="primary" @click="createApplication(group.id)" :disabled="!canApply(group)">{{ $t('tourGroup.bookNow') }}</el-button>
        </div>
      </div>
    </div>
    <div v-if="filteredGroups.length === 0" class="empty-state">
      <el-empty :description="$t('common.noData')" />
    </div>
  </AppLayout>
  <el-dialog v-model="showAvailability" :title="$t('common.detail')" width="420px">
    <div class="availability-result">
      <div :class="['result-icon', availabilityResult?.available ? 'success' : 'error']">
        <el-icon v-if="availabilityResult?.available" :size="32"><CircleCheck /></el-icon>
        <el-icon v-else :size="32"><CircleClose /></el-icon>
      </div>
      <p :class="['result-text', availabilityResult?.available ? 'success' : 'error']">{{ availabilityResult?.reason }}</p>
      <div v-if="availabilityResult?.available" class="apply-info">
        <div class="apply-info-row"><span>旅游团代码</span><span>{{ currentGroupForCheck?.group_code }}</span></div>
        <div class="apply-info-row"><span>路线名称</span><span>{{ currentGroupForCheck?.route_name }}</span></div>
        <el-button type="primary" class="apply-btn" @click="proceedToApply">立即申请</el-button>
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import request from '../utils/request'
import {
  Monitor, Plus, Document, Search, Suitcase, MapLocation,
  Printer, Download, SwitchButton, Calendar, Timer, UserFilled,
  InfoFilled, CircleCheck, CircleClose
} from '@element-plus/icons-vue'
import AppLayout from '../components/AppLayout.vue'

const router = useRouter()
const groups = ref([])
const searchText = ref('')
const showAvailability = ref(false)
const availabilityResult = ref(null)
const currentGroupForCheck = ref(null)

const filteredGroups = computed(() => {
  if (!searchText.value) return groups.value
  const q = searchText.value
  return groups.value.filter(g => g.route_name?.includes(q) || g.group_code?.includes(q))
})

const navigate = (path) => { router.push(path) }

const loadGroups = async () => {
  try {
    const res = await request.get('/tour_groups')
    groups.value = res
  } catch (error) {
    console.error('Failed to load tour groups:', error)
  }
}

const searchGroups = () => {}

const getRemainingCapacity = (group) => group.remaining_capacity !== undefined ? group.remaining_capacity : group.max_capacity

const canApply = (group) => {
  const today = new Date()
  const deadline = new Date(group.deadline_date)
  return today <= deadline && getRemainingCapacity(group) > 0
}

const checkAvailability = async (group) => {
  currentGroupForCheck.value = group
  try {
    const res = await request.get(`/tour_groups/${group.id}/check_availability`)
    availabilityResult.value = res
    showAvailability.value = true
  } catch (error) {
    console.error('Failed to check availability:', error)
  }
}

const createApplication = (groupId) => {
  router.push({ path: '/applications/create', query: { groupId } })
}

const proceedToApply = () => {
  showAvailability.value = false
  if (currentGroupForCheck.value) {
    createApplication(currentGroupForCheck.value.id)
  }
}

onMounted(() => { loadGroups() })
</script>

<style scoped>
.page-toolbar { display: flex; gap: 12px; margin-bottom: 16px; align-items: center; justify-content: space-between; }
.toolbar-right { display: flex; gap: 8px; }
.tour-group-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 16px; }
.tour-card {
  background: var(--bg-card); border-radius: var(--radius-md); overflow: hidden;
  box-shadow: var(--shadow-sm); transition: all 0.2s ease;
}
.tour-card:hover { box-shadow: var(--shadow-md); }
.card-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 16px 20px; background: #f8fafc; border-bottom: 1px solid #e2e8f0;
}
.card-header-left { display: flex; align-items: center; gap: 10px; }
.group-code { font-size: 13px; font-weight: 600; color: #3b82f6; }
.card-body { padding: 20px; }
.route-name { font-size: 17px; font-weight: 600; color: #0f172a; margin: 0 0 14px; }
.info-rows { display: flex; flex-direction: column; gap: 8px; }
.info-row { display: flex; align-items: center; gap: 6px; font-size: 13px; color: #64748b; }
.info-row .el-icon { font-size: 14px; }
.info-row strong { color: #3b82f6; }
.price-row {
  display: flex; align-items: center; gap: 16px; margin-top: 16px;
  padding-top: 14px; border-top: 1px dashed #e2e8f0;
}
.price-item { display: flex; flex-direction: column; gap: 2px; }
.price-label { font-size: 12px; color: #94a3b8; }
.price-value { font-size: 18px; font-weight: 700; color: #0f172a; }
.price-divider { width: 1px; height: 32px; background: #e2e8f0; }
.card-footer {
  display: flex; gap: 10px; padding: 14px 20px; background: #f8fafc;
  border-top: 1px solid #e2e8f0;
}
.card-footer .el-button { flex: 1; }
.empty-state { padding: 60px 0; }
.availability-result { text-align: center; padding: 20px; }
.result-icon {
  width: 64px; height: 64px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto 16px;
}
.result-icon.success { background: rgba(34,197,94,0.1); color: #22c55e; }
.result-icon.error { background: rgba(239,68,68,0.1); color: #ef4444; }
.result-text { font-size: 15px; font-weight: 500; margin: 0 0 20px; }
.result-text.success { color: #22c55e; }
.result-text.error { color: #ef4444; }
.apply-info { background: #f8fafc; border-radius: 10px; padding: 16px; }
.apply-info-row { display: flex; justify-content: space-between; padding: 6px 0; font-size: 14px; color: #475569; }
.apply-btn { width: 100%; margin-top: 16px; }

@media (max-width: 768px) {
  .tour-group-grid { grid-template-columns: 1fr; }
  .search-box { max-width: 100%; flex-direction: column; }
}
</style>
