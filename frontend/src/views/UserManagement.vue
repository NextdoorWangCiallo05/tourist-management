<template>
  <AppLayout activeMenu="user-management" breadcrumb="用户管理" :headerIcon="User">
    <div class="page-toolbar">
      <span class="page-description">管理系统用户账户，仅超级管理员可操作</span>
      <div class="toolbar-right">
        <el-button type="primary" @click="createUser"><el-icon><Plus /></el-icon> 新建用户</el-button>
      </div>
    </div>
    <div class="page-card">
      <el-table :data="users" class="data-table">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="username" label="用户名" width="140" />
        <el-table-column prop="display_name" label="显示名称" width="140" />
        <el-table-column prop="role" label="角色" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.role === 'admin' ? 'danger' : 'info'" size="small" effect="plain">
              {{ scope.row.role === 'admin' ? '管理员' : '操作员' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button size="small" :type="scope.row.role === 'admin' ? 'warning' : 'success'" plain @click="toggleRole(scope.row)">
              设为{{ scope.row.role === 'admin' ? '操作员' : '管理员' }}
            </el-button>
            <el-button size="small" type="danger" plain @click="deleteUser(scope.row)" :disabled="scope.row.username === currentUser">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </AppLayout>

  <el-dialog v-model="showCreateDialog" :title="$t('userMgmt.newUser')" width="450px">
    <el-form :model="createForm" label-width="80px">
      <el-form-item :label="$t('userMgmt.username')"><el-input v-model="createForm.username" placeholder="2-20位字母数字或中文" /></el-form-item>
      <el-form-item :label="$t('userMgmt.displayName')"><el-input v-model="createForm.display_name" /></el-form-item>
      <el-form-item label="邮箱"><el-input v-model="createForm.email" placeholder="email@example.com" /></el-form-item>
      <el-form-item label="手机号"><el-input v-model="createForm.phone" placeholder="手机号（选填）" /></el-form-item>
      <el-form-item :label="$t('login.password')"><el-input v-model="createForm.password" type="password" show-password placeholder="不少于6位" /></el-form-item>
      <el-form-item :label="$t('userMgmt.role')">
        <el-select v-model="createForm.role" style="width:100%">
          <el-option :label="$t('userMgmt.operator')" value="operator" />
          <el-option :label="$t('userMgmt.admin')" value="admin" />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="showCreateDialog = false">取消</el-button>
      <el-button type="primary" @click="saveUser">创建</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '../utils/request'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Monitor, Plus, Document, Search, Suitcase, MapLocation, User, List } from '@element-plus/icons-vue'
import AppLayout from '../components/AppLayout.vue'

const users = ref([])
const currentUser = ref(localStorage.getItem('displayName') || '')
const showCreateDialog = ref(false)
const createForm = ref({ username: '', display_name: '', email: '', phone: '', password: '', role: 'operator' })

const loadUsers = async () => {
  try {
    const res = await request.get('/users')
    users.value = res
  } catch (e) { console.error(e) }
}

const createUser = () => {
  createForm.value = { username: '', display_name: '', email: '', phone: '', password: '', role: 'operator' }
  showCreateDialog.value = true
}

const saveUser = async () => {
  try {
    await request.post('/register', createForm.value)
    showCreateDialog.value = false
    ElMessage.success('用户创建成功')
    loadUsers()
  } catch (e) { ElMessage.error('创建失败') }
}

const toggleRole = async (u) => {
  const newRole = u.role === 'admin' ? 'operator' : 'admin'
  const roleText = newRole === 'admin' ? '管理员' : '操作员'
  try {
    await ElMessageBox.confirm(
      `确认将 <b>${u.display_name}</b>（${u.username}）的角色改为 <b>${roleText}</b>？<br><br>
      <span style="color:#f59e0b">⚠️ 修改后其权限将立即变更</span>`,
      '修改角色',
      { confirmButtonText: '确认修改', cancelButtonText: '取消', type: 'warning', dangerouslyUseHTMLString: true }
    )
    await request.put(`/users/${u.id}/role`, { role: newRole })
    ElMessage.success(`已将 ${u.display_name} 设为${roleText}`)
    loadUsers()
  } catch (e) { if (e !== 'cancel') ElMessage.error('操作失败') }
}

const deleteUser = async (u) => {
  try {
    await ElMessageBox.confirm(
      `确认删除用户 <b>${u.display_name}</b>（${u.username}）？<br><br>
      <span style="color:#ef4444">⚠️ 此操作不可撤销，该用户将无法再登录系统</span>`,
      '确认删除',
      { confirmButtonText: '确认删除', cancelButtonText: '取消', type: 'error', dangerouslyUseHTMLString: true }
    )
    await request.delete(`/users/${u.id}`)
    ElMessage.success(`已删除用户 ${u.display_name}`)
    loadUsers()
  } catch (e) { if (e !== 'cancel') ElMessage.error('删除失败') }
}

onMounted(() => { loadUsers() })
</script>

<style scoped>
.page-description { font-size: 13px; color: var(--text-muted); }
.page-toolbar { display: flex; gap: 12px; margin-bottom: 16px; align-items: center; justify-content: space-between; }
.toolbar-right { display: flex; gap: 8px; }
.page-card { background: var(--bg-card); border-radius: var(--radius-md); box-shadow: var(--shadow-sm); overflow: hidden; }
</style>
