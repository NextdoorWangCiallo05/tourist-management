<template>
  <AppLayout activeMenu="dashboard" :breadcrumb="$t('dashboard.title')" :headerIcon="Monitor">
    <div class="welcome-section">
      <div class="welcome-text">
        <h2>{{ $t('dashboard.welcome', { greeting: greeting, name: displayName }) }}</h2>
        <p>{{ $t('common.todayIs') }} {{ todayStr }}，{{ $t('common.systemNormal') }}</p>
      </div>
      <div class="welcome-stats-mini">
        <div class="mini-stat" v-for="s in miniStats" :key="s.label">
          <span class="mini-value">{{ s.value }}</span>
          <span class="mini-label">{{ s.label }}</span>
        </div>
      </div>
    </div>

    <div class="stats-grid">
      <div class="stat-card" v-for="stat in stats" :key="stat.label">
        <div class="stat-body">
          <span class="stat-value">{{ stat.value }}</span>
          <span class="stat-label">{{ stat.label }}</span>
        </div>
        <div class="stat-icon" :style="{ background: stat.bg, color: stat.color }">
          <el-icon :size="20"><component :is="stat.icon" /></el-icon>
        </div>
      </div>
    </div>

    <div class="charts-grid">
      <div class="chart-card">
        <div class="chart-title">{{ $t('dashboard.chartStatus') }}</div>
        <div class="chart-body"><v-chart :option="chartStatus" style="height:260px" /></div>
      </div>
      <div class="chart-card">
        <div class="chart-title">{{ $t('dashboard.chartTrend') }}</div>
        <div class="chart-body"><v-chart :option="chartTrend" style="height:260px" /></div>
      </div>
    </div>

    <div class="bottom-grid">
      <div class="bottom-card">
        <div class="card-title">{{ $t('dashboard.quickActions') }}</div>
        <div class="quick-grid">
          <button class="quick-btn" @click="navigate('/applications/create')">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2" stroke-linecap="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
            <span>{{ $t('dashboard.newApp') }}</span>
          </button>
          <button class="quick-btn" @click="navigate('/tour-groups')">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
            <span>{{ $t('dashboard.searchGroups') }}</span>
          </button>
          <button class="quick-btn" @click="navigate('/applications')">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
            <span>{{ $t('dashboard.appList') }}</span>
          </button>
          <button class="quick-btn" @click="navigate('/audit-logs')">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
            <span>{{ $t('dashboard.auditLogs') }}</span>
          </button>
        </div>
      </div>
      <div class="bottom-card">
        <div class="card-title">{{ $t('dashboard.reminders') }}</div>
        <div class="reminder-list">
          <div class="reminder-item" v-for="(item, idx) in reminders" :key="idx">
            <span class="reminder-dot" :style="{ background: dotColors[item.type] || '#94a3b8' }"></span>
            <span class="reminder-text">{{ item.text }}</span>
          </div>
          <div v-if="reminders.length === 0" class="reminder-empty">{{ $t('dashboard.noReminders') }}</div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import request from '../utils/request'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart, LineChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, LegendComponent, GridComponent } from 'echarts/components'
import { useI18n } from 'vue-i18n'
import {
  Monitor, Document, User, Wallet, Odometer, Calendar
} from '@element-plus/icons-vue'
import AppLayout from '../components/AppLayout.vue'

use([CanvasRenderer, PieChart, LineChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent])

const { t } = useI18n()
const router = useRouter()
const userStore = useUserStore()
const displayName = computed(() => userStore.displayName)
const greeting = computed(() => {
  const h = new Date().getHours()
  return h < 12 ? t('common.morning') : h < 18 ? t('common.afternoon') : t('common.evening')
})
const todayStr = new Date().toLocaleDateString('zh-CN', { month: 'long', day: 'numeric', weekday: 'long' })

const navigate = (path) => router.push(path)

const overview = ref({ total_applications: 0, total_groups: 0, total_participants: 0 })
const chartStatus = ref({})
const chartTrend = ref({})
const reminders = ref([])

const dotColors = { warning: '#f59e0b', info: '#3b82f6', success: '#22c55e', danger: '#ef4444' }

const stats = computed(() => [
  { value: overview.value.total_applications, label: t('dashboard.totalApps'), icon: Document, bg: 'rgba(79,110,247,0.1)', color: '#4f6ef7' },
  { value: overview.value.total_participants, label: t('dashboard.totalParticipants'), icon: User, bg: 'rgba(16,185,129,0.1)', color: '#10b981' },
  { value: `¥${Number(overview.value.today_payments || 0).toFixed(0)}`, label: t('dashboard.todayPayments'), icon: Wallet, bg: 'rgba(245,158,11,0.1)', color: '#f59e0b' },
  { value: overview.value.total_groups, label: t('dashboard.totalGroups'), icon: Odometer, bg: 'rgba(139,92,246,0.1)', color: '#8b5cf6' },
])

const miniStats = computed(() => [
  { value: overview.value.total_applications, label: t('dashboard.totalApps') },
  { value: overview.value.total_participants, label: t('dashboard.totalParticipants') },
  { value: overview.value.total_groups, label: t('dashboard.totalGroups') },
])

const loadStats = async () => {
  try {
    const data = await request.get('/stats')
    overview.value = data
    const sd = data.status_distribution || []
    const dt = data.daily_trend || []
    chartStatus.value = {
      tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
      legend: { bottom: 0, data: ['处理中', '已完成', '已取消'], textStyle: { fontSize: 12, color: '#5b677d' } },
      series: [{
        type: 'pie', radius: ['40%', '62%'], center: ['50%', '45%'],
        avoidLabelOverlap: false, itemStyle: { borderRadius: 4, borderColor: '#fff', borderWidth: 2 },
        label: { show: true, formatter: '{b}\n{c}', fontSize: 11, color: '#5b677d' },
        data: sd.map(d => ({ name: d.name === 'pending' ? '处理中' : d.name === 'completed' ? '已完成' : '已取消', value: d.value })),
        color: ['#f59e0b', '#10b981', '#ef4444']
      }]
    }
    chartTrend.value = {
      tooltip: { trigger: 'axis' },
      grid: { left: 40, right: 16, bottom: 24, top: 12 },
      xAxis: { type: 'category', data: dt.map(d => d.date.slice(5)), axisLabel: { fontSize: 11 }, axisLine: { show: false }, axisTick: { show: false } },
      yAxis: { type: 'value', minInterval: 1, splitLine: { lineStyle: { color: '#f0f0f0' } }, axisLabel: { fontSize: 11 } },
      series: [{
        type: 'line', smooth: true, data: dt.map(d => d.count),
        areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(79,110,247,0.2)' }, { offset: 1, color: 'rgba(79,110,247,0)' }] } },
        lineStyle: { color: '#4f6ef7', width: 2.5 },
        itemStyle: { color: '#4f6ef7' },
        symbol: 'circle', symbolSize: 6
      }]
    }
    const pending = sd.find(d => d.name === 'pending')
    const items = []
    if (pending?.value > 0) items.push({ type: 'warning', text: t('dashboard.pendingApps', { count: pending.value }) })
    if (data.total_groups > 0) items.push({ type: 'info', text: t('dashboard.groupsActive', { count: data.total_groups }) })
    if (items.length === 0) items.push({ type: 'success', text: t('dashboard.allGood') })
    reminders.value = items
  } catch (e) { console.error(e) }
}

onMounted(() => { loadStats() })
</script>

<style scoped>
.welcome-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}
.welcome-text h2 {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 4px;
}
.welcome-text p {
  font-size: 14px;
  color: var(--text-muted);
  margin: 0;
}
.welcome-stats-mini {
  display: flex;
  gap: 20px;
}
.mini-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}
.mini-value {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
}
.mini-label {
  font-size: 12px;
  color: var(--text-muted);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}
.stat-card {
  background: var(--bg-card);
  border-radius: var(--radius-md);
  padding: 20px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: var(--shadow-sm);
}
.stat-body {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
}
.stat-label {
  font-size: 13px;
  color: var(--text-muted);
}
.stat-icon {
  width: 42px;
  height: 42px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.charts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 24px;
}
.chart-card {
  background: var(--bg-card);
  border-radius: var(--radius-md);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}
.chart-title {
  padding: 16px 20px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  border-bottom: 1px solid var(--border);
}
.chart-body { padding: 12px; }

.bottom-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
.bottom-card {
  background: var(--bg-card);
  border-radius: var(--radius-md);
  padding: 20px 24px;
  box-shadow: var(--shadow-sm);
}
.card-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
}
.quick-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}
.quick-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: transparent;
  cursor: pointer;
  font-size: 13px;
  color: var(--text-secondary);
  transition: all 0.15s ease;
}
.quick-btn:hover {
  border-color: var(--accent);
  background: var(--accent-soft);
  color: var(--accent);
}
.quick-btn svg { flex-shrink: 0; }

.reminder-list { display: flex; flex-direction: column; gap: 10px; }
.reminder-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: var(--radius-sm);
  background: var(--bg);
}
.reminder-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}
.reminder-text { font-size: 13.5px; color: var(--text-secondary); }
.reminder-empty { font-size: 13.5px; color: var(--text-muted); padding: 10px 0; }

@media (max-width: 768px) {
  .stats-grid, .charts-grid, .bottom-grid { grid-template-columns: 1fr; }
  .welcome-section { flex-direction: column; align-items: flex-start; gap: 16px; }
  .quick-grid { grid-template-columns: 1fr; }
}
</style>
