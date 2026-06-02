<template>
  <el-aside width="240px" class="sidebar">
    <div class="sidebar-header">
      <div class="logo-wrapper">
        <svg class="logo-icon" viewBox="0 0 64 64" fill="none">
          <circle cx="32" cy="32" r="30" fill="url(#logoGradient)"/>
          <path d="M32 18 L32 46 M20 28 L44 28 M18 36 L46 36" stroke="white" stroke-width="3" stroke-linecap="round"/>
          <circle cx="32" cy="32" r="8" fill="white" opacity="0.3"/>
          <defs>
            <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#3b82f6"/>
              <stop offset="100%" stop-color="#1e40af"/>
            </linearGradient>
          </defs>
        </svg>
        <div class="logo-text">
          <h1 class="logo-title">智游云管</h1>
          <p class="logo-subtitle">旅游业务管理系统</p>
        </div>
      </div>
    </div>
    <el-menu :default-active="activeMenu" class="sidebar-menu">
      <el-menu-item index="dashboard" @click="navigate('/dashboard')">
        <el-icon><Monitor /></el-icon><span>首页概览</span>
      </el-menu-item>
      <el-menu-item index="create-app" @click="navigate('/applications/create')">
        <el-icon><Plus /></el-icon><span>新建申请</span>
      </el-menu-item>
      <el-menu-item index="applications" @click="navigate('/applications')">
        <el-icon><Document /></el-icon><span>申请管理</span>
      </el-menu-item>
      <el-menu-item index="tour-groups" @click="navigate('/tour-groups')">
        <el-icon><Search /></el-icon><span>旅游团查询</span>
      </el-menu-item>
      <el-menu-item index="tour-group-mgmt" @click="navigate('/tour-group-management')">
        <el-icon><Suitcase /></el-icon><span>旅游团管理</span>
      </el-menu-item>
      <el-menu-item index="routes" @click="navigate('/routes')">
        <el-icon><MapLocation /></el-icon><span>路线管理</span>
      </el-menu-item>
      <el-menu-item index="confirmations" @click="navigate('/confirmations')">
        <el-icon><Printer /></el-icon><span>确认书打印</span>
      </el-menu-item>
      <el-menu-item index="export" @click="navigate('/daily-export')">
        <el-icon><Download /></el-icon><span>财务导出</span>
      </el-menu-item>
    </el-menu>
    <div class="sidebar-footer">
      <div class="user-info">
        <div class="user-avatar"><span class="avatar-text">{{ userInitial }}</span></div>
        <div class="user-detail">
          <span class="user-name">{{ displayName }}</span>
          <span class="user-role">{{ roleName }}</span>
        </div>
      </div>
      <el-button @click="handleLogout" class="logout-btn">
        <el-icon><SwitchButton /></el-icon> 退出登录
      </el-button>
    </div>
  </el-aside>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '../stores/user'
import {
  Monitor, Plus, Document, Search, Suitcase, MapLocation,
  Printer, Download, SwitchButton
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const props = defineProps({
  activeMenu: { type: String, default: 'dashboard' }
})

const navigate = (path) => { router.push(path) }
const handleLogout = () => { userStore.logout(); router.push('/') }

const displayName = computed(() => userStore.displayName)
const userInitial = computed(() => userStore.userInitial)
const roleName = computed(() => userStore.roleName)
</script>

<style scoped>
.sidebar {
  background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
  color: white; display: flex; flex-direction: column;
  border-right: 1px solid rgba(255,255,255,0.05);
}
.sidebar-header { padding: 20px; border-bottom: 1px solid rgba(255,255,255,0.06); }
.logo-wrapper { display: flex; align-items: center; gap: 12px; }
.logo-icon { width: 44px; height: 44px; }
.logo-text { display: flex; flex-direction: column; }
.logo-title { font-size: 18px; font-weight: 700; margin: 0; color: white; letter-spacing: 1px; }
.logo-subtitle { font-size: 10px; margin: 2px 0 0; color: rgba(255,255,255,0.5); }
.sidebar-menu { flex: 1; border-right: none; background: transparent; padding: 8px 0; }
.sidebar-menu .el-menu-item {
  color: rgba(255,255,255,0.65); height: 46px; line-height: 46px;
  margin: 2px 12px; border-radius: 10px; font-size: 14px;
}
.sidebar-menu .el-menu-item:hover { background: rgba(59,130,246,0.12); color: rgba(255,255,255,0.9); }
.sidebar-menu .el-menu-item.is-active {
  background: linear-gradient(135deg, rgba(59,130,246,0.2), rgba(30,64,175,0.2));
  color: #93c5fd; font-weight: 500;
}
.sidebar-menu .el-menu-item .el-icon { margin-right: 10px; font-size: 18px; }
.sidebar-footer { padding: 16px; border-top: 1px solid rgba(255,255,255,0.06); }
.user-info { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
.user-avatar {
  width: 38px; height: 38px; border-radius: 10px;
  background: linear-gradient(135deg, #3b82f6, #1e40af);
  display: flex; align-items: center; justify-content: center;
}
.avatar-text { color: white; font-weight: 600; font-size: 15px; }
.user-detail { display: flex; flex-direction: column; }
.user-name { font-size: 14px; font-weight: 600; color: white; }
.user-role { font-size: 11px; color: rgba(255,255,255,0.45); }
.logout-btn {
  width: 100%; height: 36px; border-radius: 8px; background: transparent;
  border: 1px solid rgba(255,255,255,0.1); color: rgba(255,255,255,0.6); font-size: 13px;
}
.logout-btn:hover { background: rgba(239,68,68,0.12); color: #fca5a5; border-color: rgba(239,68,68,0.25); }
</style>
