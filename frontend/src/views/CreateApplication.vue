<template>
  <AppLayout activeMenu="create-app" :breadcrumb="$t('application.create')" :headerIcon="Plus">
    <div class="form-card">
      <div class="form-card-header"><el-icon><InfoFilled /></el-icon> {{ $t('application.selectGroup') }}</div>
      <div class="form-card-body">
        <el-form :model="form" label-width="100px">
          <el-form-item :label="$t('application.group')">
            <el-select v-model="form.group_id" :placeholder="$t('common.select')" style="width:100%" @change="onGroupChange">
              <el-option v-for="g in groups" :key="g.id" :label="`${g.group_code} - ${g.route_name}`" :value="g.id" />
            </el-select>
          </el-form-item>
          <el-form-item :label="$t('application.responsiblePerson')">
            <el-input v-model="form.responsible_name" :placeholder="$t('common.placeholder')" />
          </el-form-item>
          <el-form-item :label="$t('application.responsiblePhone')">
            <el-input v-model="form.responsible_phone" :placeholder="$t('common.placeholder')" />
          </el-form-item>
        </el-form>
      </div>
    </div>
    <div v-if="selectedGroup" class="form-card">
      <div class="form-card-header"><el-icon><UserFilled /></el-icon> {{ $t('application.participantInfo') }}</div>
      <div class="form-card-body">
        <div class="participant-inputs">
          <div class="participant-row">
            <el-input v-model="newParticipant.name" :placeholder="$t('common.name')" style="width:140px" />
            <el-select v-model="newParticipant.id_type" style="width:120px">
              <el-option label="身份证" value="身份证" />
              <el-option label="护照" value="护照" />
            </el-select>
            <el-input v-model="newParticipant.id_number" :placeholder="$t('application.idNumberCol')" style="width:200px" />
            <el-input v-model="newParticipant.phone" :placeholder="$t('common.phone')" style="width:140px" />
            <el-radio-group v-model="newParticipant.is_adult">
              <el-radio :label="true">{{ $t('common.adult') }}</el-radio>
              <el-radio :label="false">{{ $t('common.child') }}</el-radio>
            </el-radio-group>
            <el-button type="primary" @click="addParticipant"><el-icon><Plus /></el-icon> {{ $t('common.add') }}</el-button>
          </div>
        </div>
        <el-table :data="participants" class="data-table" style="margin-top:12px">
          <el-table-column prop="name" :label="$t('application.nameCol')" width="120" />
          <el-table-column prop="id_type" :label="$t('application.idTypeCol')" width="100" />
          <el-table-column prop="id_number" :label="$t('application.idNumberCol')" width="200" />
          <el-table-column prop="phone" :label="$t('application.phoneCol')" width="140" />
          <el-table-column prop="is_adult" :label="$t('application.typeCol')" width="80">
            <template #default="scope">
              <el-tag :type="scope.row.is_adult ? 'primary' : 'success'" size="small" effect="plain">
                {{ scope.row.is_adult ? $t('common.adult') : $t('common.child') }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column :label="$t('application.actionCol')" width="80">
            <template #default="scope">
              <el-button size="small" type="danger" plain @click="removeParticipant(scope.$index)">{{ $t('common.delete') }}</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
    <div v-if="selectedGroup" class="form-card">
      <div class="form-card-header"><el-icon><Money /></el-icon> {{ $t('application.feeEstimate') }}</div>
      <div class="form-card-body">
        <div class="fee-grid">
          <div class="fee-item">
            <span class="fee-label">{{ $t('application.adultUnitPrice') }}</span>
            <span class="fee-value">¥{{ selectedGroup.adult_price }}</span>
          </div>
          <div class="fee-item">
            <span class="fee-label">{{ $t('application.childUnitPrice') }}</span>
            <span class="fee-value">¥{{ selectedGroup.child_price }}</span>
          </div>
          <div class="fee-item">
            <span class="fee-label">{{ $t('application.adultCount') }}</span>
            <span class="fee-value">{{ adultCount }} {{ $t('common.person') }}</span>
          </div>
          <div class="fee-item">
            <span class="fee-label">{{ $t('application.childCount') }}</span>
            <span class="fee-value">{{ childCount }} {{ $t('common.person') }}</span>
          </div>
          <div class="fee-item total">
            <span class="fee-label">{{ $t('application.estTotal') }}</span>
            <span class="fee-value highlight">¥{{ estimatedTotal }}</span>
          </div>
          <div class="fee-item">
            <span class="fee-label">{{ $t('application.estDeposit') }}</span>
            <span class="fee-value deposit">¥{{ estimatedDeposit }}</span>
          </div>
        </div>
      </div>
    </div>
    <div class="form-actions">
      <el-button size="large" @click="navigate('/applications')"><el-icon><Back /></el-icon> {{ $t('common.back') }}</el-button>
      <el-button type="primary" size="large" :disabled="!canSubmit" @click="submitApplication">
        <el-icon><CircleCheck /></el-icon> {{ $t('application.submitApp') }}
      </el-button>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import request from '../utils/request'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Monitor, Plus, Document, Search, Suitcase, MapLocation,
  Printer, Download, SwitchButton, Calendar, InfoFilled,
  UserFilled, Money, Back, CircleCheck
} from '@element-plus/icons-vue'
import AppLayout from '../components/AppLayout.vue'

const router = useRouter()
const route = useRoute()
const groups = ref([])
const selectedGroup = ref(null)
const participants = ref([])
const newParticipant = ref({ name: '', id_type: '身份证', id_number: '', phone: '', is_adult: true })
const form = ref({ group_id: null, responsible_name: '', responsible_phone: '' })

const currentDate = new Date().toLocaleDateString('zh-CN', {
  year: 'numeric', month: '2-digit', day: '2-digit', weekday: 'long'
})

const adultCount = computed(() => participants.value.filter(p => p.is_adult).length)
const childCount = computed(() => participants.value.filter(p => !p.is_adult).length)
const estimatedTotal = computed(() => {
  if (!selectedGroup.value) return '0.00'
  return (adultCount.value * selectedGroup.value.adult_price + childCount.value * selectedGroup.value.child_price).toFixed(2)
})
const estimatedDeposit = computed(() => {
  if (!selectedGroup.value) return '0.00'
  const total = adultCount.value * selectedGroup.value.adult_price + childCount.value * selectedGroup.value.child_price
  const rate = selectedGroup.value.deposit_rate !== undefined ? selectedGroup.value.deposit_rate : 0.2
  return (total * rate).toFixed(2)
})
const canSubmit = computed(() => form.value.group_id && form.value.responsible_name && participants.value.length > 0)

const navigate = (path) => { router.push(path) }

const loadGroups = async () => {
  try {
    const res = await request.get('/tour_groups')
    groups.value = res
    if (route.query.groupId) {
      form.value.group_id = parseInt(route.query.groupId)
      onGroupChange(form.value.group_id)
    }
  } catch (error) {
    console.error('Failed to load groups:', error)
  }
}

const onGroupChange = (groupId) => {
  selectedGroup.value = groups.value.find(g => g.id === groupId) || null
}

const addParticipant = () => {
  if (!newParticipant.value.name || !newParticipant.value.id_number) {
    ElMessage.warning('请填写参加者姓名和证件号码')
    return
  }
  participants.value.push({ ...newParticipant.value })
  newParticipant.value = { name: '', id_type: '身份证', id_number: '', phone: '', is_adult: true }
}

const removeParticipant = (index) => {
  participants.value.splice(index, 1)
}

const submitApplication = async () => {
  try {
    const adultCount = participants.value.filter(p => p.is_adult).length
    const childCount = participants.value.filter(p => !p.is_adult).length
    const payload = {
      group_id: form.value.group_id,
      responsible_name: form.value.responsible_name,
      phone_number: form.value.responsible_phone,
      adult_count: adultCount,
      child_count: childCount
    }
    const res = await request.post('/applications', payload)
    const appNo = res.application_no
    const participantPayload = {
      participants: participants.value.map(p => ({
        name: p.name,
        id_number: p.id_number,
        phone_number: p.phone,
        is_adult: p.is_adult
      }))
    }
    await request.post(`/applications/${appNo}/participants`, participantPayload)
    ElMessage.success(`申请创建成功！申请编号: ${appNo}`)
    router.push(`/applications/detail/${appNo}`)
  } catch (error) {
    ElMessage.error('创建申请失败')
  }
}

onMounted(() => { loadGroups() })
</script>

<style scoped>
.form-card {
  background: white; border-radius: 14px; overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04); margin-bottom: 20px;
}
.form-card-header {
  display: flex; align-items: center; gap: 8px;
  padding: 16px 20px; background: #f8fafc; border-bottom: 1px solid #e2e8f0;
  font-weight: 600; color: #0f172a; font-size: 15px;
}
.form-card-header .el-icon { color: #3b82f6; }
.form-card-body { padding: 20px; }

.participant-row { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
.data-table { width: 100%; }
.data-table :deep(.el-table__header th) { background: #f8fafc; color: #475569; font-weight: 600; }

.fee-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.fee-item {
  display: flex; flex-direction: column; gap: 4px;
  padding: 16px; background: #f8fafc; border-radius: 10px;
}
.fee-label { font-size: 13px; color: #64748b; }
.fee-value { font-size: 20px; font-weight: 700; color: #0f172a; }
.fee-value.highlight { color: #3b82f6; font-size: 24px; }
.fee-value.deposit { color: #f59e0b; }
.fee-item.total { background: linear-gradient(135deg, #eff6ff, #dbeafe); }

.form-actions {
  display: flex; gap: 12px; justify-content: center;
  padding: 20px; background: white; border-radius: 14px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
</style>