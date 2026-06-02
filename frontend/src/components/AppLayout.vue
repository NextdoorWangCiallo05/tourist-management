<template>
  <div class="page">
    <el-container class="main-container">
      <AppSidebar :activeMenu="activeMenu" />
      <el-container class="main-content">
        <el-header class="top-header">
          <div class="header-left">
            <el-icon class="header-icon" v-if="headerIcon"><component :is="headerIcon" /></el-icon>
            <span class="breadcrumb">{{ breadcrumb }}</span>
          </div>
          <div class="header-right">
            <el-tag type="info" effect="plain" class="date-tag">
              <el-icon style="margin-right:4px"><Calendar /></el-icon>
              {{ currentDate }}
            </el-tag>
          </div>
        </el-header>
        <el-main class="content-area">
          <slot />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { Calendar } from '@element-plus/icons-vue'
import AppSidebar from './AppSidebar.vue'

defineProps({
  activeMenu: { type: String, default: 'dashboard' },
  breadcrumb: { type: String, default: '' },
  headerIcon: { type: [String, Object], default: null }
})

const currentDate = new Date().toLocaleDateString('zh-CN', {
  year: 'numeric', month: '2-digit', day: '2-digit', weekday: 'long'
})
</script>

<style scoped>
.page { min-height: 100vh; display: flex; }
.main-container { width: 100%; height: 100vh; }
.main-content { flex: 1; display: flex; flex-direction: column; background: #f1f5f9; }
.top-header {
  background: white; padding: 0 28px; display: flex; justify-content: space-between;
  align-items: center; border-bottom: 1px solid #e2e8f0; height: 60px;
}
.header-left { display: flex; align-items: center; gap: 8px; }
.header-icon { font-size: 18px; color: #3b82f6; }
.breadcrumb { font-size: 15px; color: #1e293b; font-weight: 600; }
.header-right { display: flex; align-items: center; gap: 12px; }
.date-tag { font-size: 13px; padding: 4px 12px; border-radius: 20px; }
.content-area { flex: 1; padding: 24px 28px; overflow-y: auto; }

@media (max-width: 768px) {
  .page .main-container .sidebar { display: none; }
  .top-header { padding: 0 16px; height: 50px; }
  .content-area { padding: 16px; }
  .breadcrumb { font-size: 13px; }
}
</style>
