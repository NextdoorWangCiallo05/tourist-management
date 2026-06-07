<template>
  <div class="page">
    <el-container class="main-container">
      <AppSidebar :activeMenu="activeMenu" />
      <el-container class="main-content">
        <el-header class="top-header">
          <div class="header-left">
            <div class="breadcrumb">
              <span class="breadcrumb-icon" v-if="headerIcon"><component :is="headerIcon" /></span>
              <span>{{ breadcrumb }}</span>
            </div>
          </div>
          <div class="header-right">
            <div class="header-date">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>
              </svg>
              {{ currentDate }}
            </div>
          </div>
        </el-header>
        <el-main class="content-area">
          <slot />
        </el-main>
        <AiChat />
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import AppSidebar from './AppSidebar.vue'
import AiChat from './AiChat.vue'

defineProps({
  activeMenu: { type: String, default: 'dashboard' },
  breadcrumb: { type: String, default: '' },
  headerIcon: { type: [String, Object], default: null }
})

const { locale } = useI18n()
const currentDate = computed(() => {
  const opts = locale.value === 'en'
    ? { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }
    : { year: 'numeric', month: '2-digit', day: '2-digit', weekday: 'long' }
  return new Date().toLocaleDateString(locale.value === 'en' ? 'en-US' : 'zh-CN', opts)
})
</script>

<style scoped>
.page { min-height: 100vh; display: flex; }
.main-container { width: 100%; height: 100vh; }
.main-content { flex: 1; display: flex; flex-direction: column; background: var(--bg); }
.top-header {
  background: var(--bg-card);
  padding: 0 28px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--border);
  height: 56px;
}
.header-left { display: flex; align-items: center; }
.breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  color: var(--text-primary);
  font-weight: 600;
}
.breadcrumb-icon { color: var(--accent); font-size: 16px; display: flex; }
.header-right { display: flex; align-items: center; }
.header-date {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--text-muted);
  padding: 6px 14px;
  background: var(--bg);
  border-radius: var(--radius-sm);
}
.header-date svg { opacity: 0.6; flex-shrink: 0; }
.content-area { flex: 1; padding: 24px 28px; overflow-y: auto; }

@media (max-width: 768px) {
  .page .main-container .sidebar { display: none; }
  .top-header { padding: 0 16px; height: 50px; }
  .content-area { padding: 16px; }
}
</style>
