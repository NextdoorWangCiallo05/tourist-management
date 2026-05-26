import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Dashboard from '../views/Dashboard.vue'
import TourGroupList from '../views/TourGroupList.vue'
import ApplicationList from '../views/ApplicationList.vue'
import ApplicationDetail from '../views/ApplicationDetail.vue'
import CreateApplication from '../views/CreateApplication.vue'
import RouteManagement from '../views/RouteManagement.vue'
import TourGroupManagement from '../views/TourGroupManagement.vue'
import ConfirmationPrint from '../views/ConfirmationPrint.vue'
import DailyExport from '../views/DailyExport.vue'
import AuditLogs from '../views/AuditLogs.vue'

const routes = [
  { path: '/', name: 'Login', component: Login },
  { path: '/dashboard', name: 'Dashboard', component: Dashboard },
  { path: '/tour-groups', name: 'TourGroupList', component: TourGroupList },
  { path: '/applications', name: 'ApplicationList', component: ApplicationList },
  { path: '/applications/detail/:appNo', name: 'ApplicationDetail', component: ApplicationDetail },
  { path: '/applications/create', name: 'CreateApplication', component: CreateApplication },
  { path: '/routes', name: 'RouteManagement', component: RouteManagement },
  { path: '/tour-group-management', name: 'TourGroupManagement', component: TourGroupManagement },
  { path: '/confirmations', name: 'ConfirmationPrint', component: ConfirmationPrint },
  { path: '/daily-export', name: 'DailyExport', component: DailyExport },
  { path: '/audit-logs', name: 'AuditLogs', component: AuditLogs }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.path !== '/' && !token) {
    next('/')
  } else {
    next()
  }
})

export default router