<template>
  <AppLayout activeMenu="dashboard" breadcrumb="首页概览" :headerIcon="Odometer">
    <div class="welcome-banner">
      <div class="welcome-text">
        <h2>{{ greeting }}，{{ displayName }} 👋</h2>
        <p>欢迎回来，以下是系统总览</p>
      </div>
      <div class="welcome-stats">
        <div class="welcome-stat-item">
          <span class="welcome-stat-value">{{ overview.total_applications }}</span>
          <span class="welcome-stat-label">总申请</span>
        </div>
        <div class="welcome-stat-divider"></div>
        <div class="welcome-stat-item">
          <span class="welcome-stat-value">{{ overview.total_participants }}</span>
          <span class="welcome-stat-label">总参加者</span>
        </div>
        <div class="welcome-stat-divider"></div>
        <div class="welcome-stat-item">
          <span class="welcome-stat-value">{{ overview.total_groups }}</span>
          <span class="welcome-stat-label">总旅游团</span>
        </div>
        <div class="welcome-stat-divider"></div>
        <div class="welcome-stat-item">
          <span class="welcome-stat-value">¥{{ overview.today_payments }}</span>
          <span class="welcome-stat-label">总收款</span>
        </div>
      </div>
    </div>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon-wrap blue"><el-icon><Document /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ overview.total_applications }}</span>
          <span class="stat-label">申请总数</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon-wrap green"><el-icon><User /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ overview.total_participants }}</span>
          <span class="stat-label">参加者总数</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon-wrap purple"><el-icon><Wallet /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">¥{{ overview.today_payments }}</span>
          <span class="stat-label">总收款金额</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon-wrap orange"><el-icon><Suitcase /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ overview.total_groups }}</span>
          <span class="stat-label">旅游团总数</span>
        </div>
      </div>
    </div>

    <div class="charts-grid">
      <div class="chart-card">
        <div class="chart-header"><el-icon><DataAnalysis /></el-icon><h3>申请状态分布</h3></div>
        <div class="chart-body"><v-chart :option="chartStatus" style="height:280px" /></div>
       </div>
       <div class="chart-card">
         <div class="chart-header"><el-icon><TrendCharts /></el-icon><h3>近7日申请趋势</h3></div>
         <div class="chart-body"><v-chart :option="chartTrend" style="height:280px" /></div>
      </div>
    </div>

    <div class="content-grid">
      <div class="quick-section">
        <div class="section-header"><el-icon><Lightning /></el-icon><h3>快捷操作</h3></div>
        <div class="quick-actions">
          <button class="action-btn primary" @click="navigate('/applications/create')"><el-icon><CirclePlus /></el-icon><span>新建申请</span></button>
          <button class="action-btn" @click="navigate('/tour-groups')"><el-icon><Search /></el-icon><span>查询旅游团</span></button>
          <button class="action-btn" @click="navigate('/applications')"><el-icon><List /></el-icon><span>申请列表</span></button>
          <button class="action-btn" @click="navigate('/audit-logs')"><el-icon><List /></el-icon><span>操作日志</span></button>
        </div>
      </div>
      <div class="info-section">
        <div class="section-header"><el-icon><Bell /></el-icon><h3>待办提醒</h3></div>
        <div class="info-list">
          <div class="info-item" v-for="(item, idx) in reminders" :key="idx">
            <el-tag size="small" :type="item.type" effect="dark" round>{{ item.tag }}</el-tag>
            <span class="info-text">{{ item.text }}</span>
          </div>
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
import {
  Monitor, Plus, Document, Search, Suitcase, MapLocation,
  Printer, Download, SwitchButton, Odometer, Calendar,
  User, Wallet, Lightning, CirclePlus,
  List, Bell, DataAnalysis, TrendCharts
} from '@element-plus/icons-vue'
import AppLayout from '../components/AppLayout.vue'

use([CanvasRenderer, PieChart, LineChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent])

const router = useRouter()
const userStore = useUserStore()

const displayName = computed(() => userStore.displayName)
const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return '上午好'
  if (hour < 18) return '下午好'
  return '晚上好'
})

const overview = ref({
  total_applications: 0, total_groups: 0, total_routes: 0,
  total_participants: 0, today_applications: 0, today_payments: '0.00'
})
const chartStatus = ref({})
const chartTrend = ref({})
const reminders = ref([{ type: 'info', tag: '通知', text: '加载中...' }])

const navigate = (path) => { router.push(path) }

const loadStats = async () => {
  try {
    const data = await request.get('/stats')
    overview.value = data
    const sd = data.status_distribution || []
    const dt = data.daily_trend || []
    chartStatus.value = {
      tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
      legend: { bottom: 0, data: ['处理中', '已完成', '已取消'] },
      series: [{
        type: 'pie', radius: ['35%', '60%'], center: ['50%', '45%'],
        avoidLabelOverlap: false, itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
        label: { show: true, formatter: '{b}\n{c}', fontSize: 12 },
        data: sd.map(d => ({
          name: d.name === 'pending' ? '处理中' : d.name === 'completed' ? '已完成' : '已取消',
          value: d.value
        })),
        color: ['#f59e0b', '#22c55e', '#ef4444']
      }]
    }
    chartTrend.value = {
      tooltip: { trigger: 'axis' },
      grid: { left: 40, right: 20, bottom: 30, top: 20 },
      xAxis: { type: 'category', data: dt.map(d => d.date.slice(5)), axisLabel: { fontSize: 11 } },
      yAxis: { type: 'value', minInterval: 1 },
      series: [{
        type: 'line', smooth: true, data: dt.map(d => d.count),
        areaStyle: { color: 'rgba(59,130,246,0.15)' },
        lineStyle: { color: '#3b82f6', width: 3 },
        itemStyle: { color: '#3b82f6' },
        symbol: 'circle', symbolSize: 8
      }]
    }
    const items = []
    const pending = sd.find(d => d.name === 'pending')
    if (pending && pending.value > 0) items.push({ type: 'warning', tag: '待办', text: `${pending.value}笔申请处理中` })
    if (data.total_groups > 0) items.push({ type: 'info', tag: '进行中', text: `${data.total_groups}个旅游团` })
    if (items.length === 0) items.push({ type: 'success', tag: '完成', text: '系统运行正常' })
    reminders.value = items
  } catch (error) {
    console.error('Failed to load stats:', error)
  }
}

onMounted(() => { loadStats() })
</script>

<style scoped>
.welcome-banner {
  background: linear-gradient(135deg, #1e40af 0%, #3b82f6 50%, #60a5fa 100%);
  border-radius: 16px;
  padding: 28px 32px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  color: white;
  position: relative;
  overflow: hidden;
}
.welcome-banner::before {
  content: ''; position: absolute; top: -50%; right: -10%;
  width: 300px; height: 300px; background: rgba(255,255,255,0.05); border-radius: 50%;
}
.welcome-banner::after {
  content: ''; position: absolute; bottom: -30%; right: 20%;
  width: 200px; height: 200px; background: rgba(255,255,255,0.03); border-radius: 50%;
}
.welcome-text { position: relative; z-index: 1; }
.welcome-text h2 { font-size: 22px; font-weight: 700; margin: 0 0 6px; }
.welcome-text p { font-size: 14px; margin: 0; opacity: 0.8; }
.welcome-stats { display: flex; align-items: center; gap: 24px; position: relative; z-index: 1; }
.welcome-stat-item { display: flex; flex-direction: column; align-items: center; }
.welcome-stat-value { font-size: 28px; font-weight: 700; line-height: 1.2; }
.welcome-stat-label { font-size: 12px; opacity: 0.75; margin-top: 2px; }
.welcome-stat-divider { width: 1px; height: 40px; background: rgba(255,255,255,0.2); }
.stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 24px; }
.stat-card {
  background: white; border-radius: 14px; padding: 22px 24px;
  display: flex; align-items: center; gap: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.04);
  transition: all 0.25s ease;
}
.stat-card:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(0,0,0,0.08); }
.stat-icon-wrap {
  width: 48px; height: 48px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.stat-icon-wrap .el-icon { font-size: 22px; }
.stat-icon-wrap.blue { background: linear-gradient(135deg, rgba(59,130,246,0.12), rgba(30,64,175,0.12)); color: #3b82f6; }
.stat-icon-wrap.green { background: linear-gradient(135deg, rgba(34,197,94,0.12), rgba(22,163,74,0.12)); color: #22c55e; }
.stat-icon-wrap.purple { background: linear-gradient(135deg, rgba(168,85,247,0.12), rgba(126,34,206,0.12)); color: #a855f7; }
.stat-icon-wrap.orange { background: linear-gradient(135deg, rgba(249,115,22,0.12), rgba(234,88,12,0.12)); color: #f97316; }
.stat-info { flex: 1; display: flex; flex-direction: column; }
.stat-info .stat-value { font-size: 26px; font-weight: 700; color: #0f172a; line-height: 1.2; }
.stat-info .stat-label { font-size: 13px; color: #94a3b8; margin-top: 2px; }
.charts-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 24px; }
.chart-card { background: white; border-radius: 14px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }
.chart-header {
  display: flex; align-items: center; gap: 8px; padding: 14px 20px;
  background: #f8fafc; border-bottom: 1px solid #e2e8f0; font-weight: 600; color: #0f172a; font-size: 15px;
}
.chart-header .el-icon { color: #3b82f6; font-size: 18px; }
.chart-header h3 { margin: 0; font-size: 15px; }
.chart-body { padding: 16px; }
.content-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.quick-section, .info-section { background: white; border-radius: 14px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }
.section-header { display: flex; align-items: center; gap: 8px; margin-bottom: 20px; }
.section-icon { font-size: 18px; color: #3b82f6; }
.section-header h3 { font-size: 16px; font-weight: 600; color: #0f172a; margin: 0; }
.quick-actions { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
.action-btn {
  display: flex; align-items: center; gap: 10px; padding: 16px 20px;
  border: 1px solid #e2e8f0; border-radius: 12px; background: white;
  cursor: pointer; transition: all 0.2s ease; font-size: 14px; color: #475569;
}
.action-btn:hover { border-color: #3b82f6; background: rgba(59,130,246,0.03); transform: translateY(-1px); }
.action-btn .el-icon { font-size: 20px; color: #64748b; }
.action-btn.primary { background: linear-gradient(135deg, #3b82f6, #1e40af); border: none; color: white; }
.action-btn.primary .el-icon { color: white; }
.action-btn.primary:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(59,130,246,0.3); }
.info-list { display: flex; flex-direction: column; gap: 12px; }
.info-item {
  display: flex; align-items: center; gap: 12px;
  padding: 10px 12px; border-radius: 10px; background: #f8fafc; transition: all 0.2s ease;
}
.info-item:hover { background: #f1f5f9; }
.info-text { font-size: 14px; color: #334155; }

@media (max-width: 768px) {
  .stats-grid, .charts-grid, .content-grid { grid-template-columns: 1fr; }
  .welcome-banner { flex-direction: column; gap: 16px; text-align: center; }
  .welcome-stats { gap: 16px; }
  .quick-actions { grid-template-columns: 1fr; }
}
</style>