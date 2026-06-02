import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import request from '../utils/request'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const displayName = ref(localStorage.getItem('displayName') || '操作员')
  const role = ref(localStorage.getItem('role') || 'operator')

  const isLoggedIn = computed(() => !!token.value)
  const userInitial = computed(() => displayName.value.charAt(0))
  const roleName = computed(() => role.value === 'admin' ? '管理员' : '操作员')

  function setUser(t, dn, r) {
    token.value = t
    displayName.value = dn
    role.value = r
    localStorage.setItem('token', t)
    localStorage.setItem('displayName', dn)
    localStorage.setItem('role', r)
  }

  function logout() {
    token.value = ''
    displayName.value = '操作员'
    role.value = 'operator'
    localStorage.removeItem('token')
    localStorage.removeItem('displayName')
    localStorage.removeItem('role')
  }

  return { token, displayName, role, isLoggedIn, userInitial, roleName, setUser, logout }
})
