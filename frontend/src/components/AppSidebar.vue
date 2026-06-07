<template>
  <el-aside width="240px" class="sidebar">
    <div class="sidebar-inner">
      <div class="sidebar-header">
        <div class="logo">
          <div class="logo-mark">
            <svg width="22" height="22" viewBox="0 0 32 32" fill="none">
              <rect x="2" y="2" width="28" height="28" rx="8" fill="var(--accent)"/>
              <path d="M10 16L14 20L22 12" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <span class="logo-text">{{ $t('app.name') }}</span>
        </div>
      </div>
      <div class="sidebar-nav">
        <div class="nav-label">{{ $t('nav.dashboard').includes('Dashboard') ? 'Navigation' : '导航菜单' }}</div>
        <div class="nav-items">
          <div v-for="item in navItems" :key="item.key"
            class="nav-item"
            :class="{ active: activeMenu === item.key }"
            @click="navigate(item.path)">
            <el-icon class="nav-icon"><component :is="item.icon" /></el-icon>
            <span class="nav-label-text">{{ navLabel[item.key].value }}</span>
          </div>
        </div>
      </div>
      <div class="sidebar-footer">
        <div class="user-card">
          <div class="user-avatar">{{ userInitial }}</div>
          <div class="user-info">
            <span class="user-name">{{ displayName }}</span>
            <span class="user-role">{{ roleName }}</span>
          </div>
          <button class="logout-btn" @click="handleLogout" :title="logoutTooltip">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
              <polyline points="16 17 21 12 16 7"/>
              <line x1="21" y1="12" x2="9" y2="12"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  </el-aside>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { useI18n } from 'vue-i18n'
import {
  Monitor, Plus, Document, Search, Suitcase,
  MapLocation, Printer, Download, User, Setting
} from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()
const { t } = useI18n()

defineProps({ activeMenu: { type: String, default: 'dashboard' } })

const navigate = (path) => router.push(path)
const handleLogout = () => { userStore.logout(); router.push('/') }

const displayName = computed(() => userStore.displayName)
const userInitial = computed(() => userStore.userInitial)
const roleName = computed(() => userStore.roleName)

const navLabel = {
  dashboard: computed(() => t('nav.dashboard')),
  'create-app': computed(() => t('nav.createApp')),
  applications: computed(() => t('nav.applications')),
  'tour-groups': computed(() => t('nav.tourGroups')),
  'tour-group-mgmt': computed(() => t('nav.tourGroupMgmt')),
  routes: computed(() => t('nav.routes')),
  confirmations: computed(() => t('nav.confirmations')),
  export: computed(() => t('nav.export')),
  'user-management': computed(() => t('nav.userMgmt')),
  settings: computed(() => t('nav.settings')),
}

const logoutTooltip = computed(() => t('nav.dashboard').includes('Dashboard') ? 'Logout' : '退出登录')

const navItems = [
  { key: 'dashboard', path: '/dashboard', icon: Monitor },
  { key: 'create-app', path: '/applications/create', icon: Plus },
  { key: 'applications', path: '/applications', icon: Document },
  { key: 'tour-groups', path: '/tour-groups', icon: Search },
  { key: 'tour-group-mgmt', path: '/tour-group-management', icon: Suitcase },
  { key: 'routes', path: '/routes', icon: MapLocation },
  { key: 'confirmations', path: '/confirmations', icon: Printer },
  { key: 'export', path: '/daily-export', icon: Download },
  { key: 'user-management', path: '/user-management', icon: User },
  { key: 'settings', path: '/settings', icon: Setting },
]
</script>

<style scoped>
.sidebar {
  background: var(--bg-sidebar);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
}
.sidebar-inner {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 0;
}

.sidebar-header {
  padding: 20px 20px 16px;
  border-bottom: 1px solid var(--border);
}
.logo {
  display: flex;
  align-items: center;
  gap: 10px;
}
.logo-mark {
  display: flex;
  align-items: center;
  justify-content: center;
}
.logo-text {
  font-size: 17px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: 0.5px;
}

.sidebar-nav {
  flex: 1;
  padding: 16px 10px;
  overflow-y: auto;
}
.nav-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.8px;
  padding: 0 10px;
  margin-bottom: 8px;
}
.nav-items {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.15s ease;
  color: var(--text-secondary);
  font-size: 14px;
}
.nav-item:hover {
  background: var(--accent-soft);
  color: var(--text-primary);
}
.nav-item.active {
  background: var(--accent-light);
  color: var(--accent);
  font-weight: 500;
}
.nav-icon { font-size: 18px; }
.nav-label-text { font-size: 13.5px; }

.sidebar-footer {
  padding: 12px 12px 16px;
  border-top: 1px solid var(--border);
}
.user-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: var(--radius-sm);
  background: var(--bg);
}
.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: var(--accent);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
  flex-shrink: 0;
}
.user-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}
.user-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}
.user-role {
  font-size: 11px;
  color: var(--text-muted);
}
.logout-btn {
  width: 30px;
  height: 30px;
  border-radius: 8px;
  border: none;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;
  flex-shrink: 0;
}
.logout-btn:hover {
  background: rgba(239, 68, 68, 0.08);
  color: #ef4444;
}
</style>
