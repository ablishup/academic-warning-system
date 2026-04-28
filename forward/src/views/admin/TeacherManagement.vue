<template>
  <div class="admin-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <h1>教师管理</h1>
        <p>管理教师账号信息</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="openAddDialog">
          <el-icon><Plus /></el-icon>
          新增教师
        </el-button>
      </div>
    </div>

    <!-- 筛选栏 -->
    <el-card class="filter-card" shadow="hover">
      <el-form :model="filterForm" inline>
        <el-form-item label="状态">
          <el-select v-model="filterForm.is_active" placeholder="全部状态" clearable style="width: 150px">
            <el-option label="启用" :value="true" />
            <el-option label="禁用" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item label="搜索">
          <el-input v-model="filterForm.search" placeholder="用户名/姓名/工号" clearable style="width: 250px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleFilter">
            <el-icon><Search /></el-icon>
            筛选
          </el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 教师列表 -->
    <el-card class="list-card" shadow="hover">
      <el-table :data="users" v-loading="loading" stripe>
        <el-table-column type="index" width="50" />
        <el-table-column label="用户" min-width="180">
          <template #default="{ row }">
            <div class="user-info">
              <div class="user-meta">
                <div class="info-name">{{ row.username }}</div>
                <div class="info-meta" v-if="row.first_name || row.last_name">
                  {{ row.last_name }}{{ row.first_name }}
                </div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="student_no" label="工号" width="120" />
        <el-table-column prop="email" label="邮箱" min-width="180" show-overflow-tooltip />
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-switch v-model="row.is_active" @change="(val) => toggleUserStatus(row, val)" />
          </template>
        </el-table-column>
        <el-table-column label="注册时间" width="120">
          <template #default="{ row }">
            {{ formatDate(row.date_joined) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="editUser(row)">编辑</el-button>
            <el-button type="warning" link size="small" @click="resetPassword(row)">重置密码</el-button>
            <el-button type="danger" link size="small" @click="handleDeleteUser(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑教师' : '新增教师'" width="600px">
      <el-form :model="userForm" label-width="100px" :rules="userRules" ref="userFormRef">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" :disabled="isEdit" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="!isEdit">
          <el-input v-model="userForm.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <el-form-item label="姓名">
          <el-row :gutter="10">
            <el-col :span="12"><el-input v-model="userForm.last_name" placeholder="姓" /></el-col>
            <el-col :span="12"><el-input v-model="userForm.first_name" placeholder="名" /></el-col>
          </el-row>
        </el-form-item>
        <el-form-item label="工号">
          <el-input v-model="userForm.student_no" placeholder="请输入工号" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="userForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="userForm.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="userForm.is_active" active-text="启用" inactive-text="禁用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitUser" :loading="submitting">确认</el-button>
      </template>
    </el-dialog>

    <!-- 重置密码弹窗 -->
    <el-dialog v-model="resetDialogVisible" title="重置密码" width="400px">
      <el-form :model="resetForm" label-width="100px" :rules="resetRules" ref="resetFormRef">
        <el-form-item label="新密码" prop="password">
          <el-input v-model="resetForm.password" type="password" placeholder="请输入新密码" show-password />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="resetForm.confirmPassword" type="password" placeholder="请再次输入新密码" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="resetDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitResetPassword" :loading="resetting">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Plus, Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getUserList, createUser, updateUser, deleteUser as apiDeleteUser,
  resetUserPassword, toggleUserStatus as apiToggleUserStatus
} from '@/api/admin'
import { formatDate } from './common'

const loading = ref(false)
const submitting = ref(false)
const resetting = ref(false)
const dialogVisible = ref(false)
const resetDialogVisible = ref(false)
const isEdit = ref(false)
const userFormRef = ref(null)
const resetFormRef = ref(null)
const currentUser = ref(null)

const filterForm = reactive({ role: 'teacher', is_active: undefined, search: '' })
const pagination = reactive({ page: 1, pageSize: 10, total: 0 })
const users = ref([])

const userForm = reactive({
  username: '', password: '', first_name: '', last_name: '', student_no: '',
  role: 'teacher', email: '', phone: '', is_active: true
})

const userRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur', min: 6 }]
}

const resetForm = reactive({ password: '', confirmPassword: '' })
const resetRules = {
  password: [{ required: true, message: '请输入新密码', trigger: 'blur', min: 6 }],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== resetForm.password) callback(new Error('两次输入的密码不一致'))
        else callback()
      }, trigger: 'blur'
    }
  ]
}

const loadData = async () => {
  loading.value = true
  try {
    const params = { page: pagination.page, page_size: pagination.pageSize, ...filterForm }
    const res = await getUserList(params)
    if (res.code === 200) {
      users.value = res.data?.results || []
      pagination.total = res.data?.count || 0
    }
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const handleFilter = () => { pagination.page = 1; loadData() }
const resetFilter = () => {
  filterForm.is_active = undefined; filterForm.search = ''
  pagination.page = 1; loadData()
}
const handleSizeChange = (val) => { pagination.pageSize = val; loadData() }
const handleCurrentChange = (val) => { pagination.page = val; loadData() }

const openAddDialog = () => {
  isEdit.value = false
  Object.assign(userForm, { username: '', password: '', first_name: '', last_name: '', student_no: '', role: 'teacher', email: '', phone: '', is_active: true })
  dialogVisible.value = true
}

const editUser = (row) => {
  isEdit.value = true
  currentUser.value = row
  Object.assign(userForm, {
    username: row.username, first_name: row.first_name, last_name: row.last_name,
    student_no: row.student_no, role: 'teacher', email: row.email, phone: row.phone, is_active: row.is_active
  })
  dialogVisible.value = true
}

const submitUser = async () => {
  const valid = await userFormRef.value?.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    if (isEdit.value) {
      await updateUser(currentUser.value.id, userForm)
      ElMessage.success('教师更新成功')
    } else {
      await createUser(userForm)
      ElMessage.success('教师创建成功')
    }
    dialogVisible.value = false
    loadData()
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error(error.message || '保存失败')
  } finally {
    submitting.value = false
  }
}

const toggleUserStatus = async (row, val) => {
  try {
    await apiToggleUserStatus(row.id, val)
    ElMessage.success(val ? '教师已启用' : '教师已禁用')
  } catch (error) {
    console.error('更新状态失败:', error)
    ElMessage.error('更新状态失败')
    row.is_active = !val
  }
}

const resetPassword = (row) => {
  currentUser.value = row
  resetForm.password = ''; resetForm.confirmPassword = ''
  resetDialogVisible.value = true
}

const submitResetPassword = async () => {
  const valid = await resetFormRef.value?.validate().catch(() => false)
  if (!valid) return
  resetting.value = true
  try {
    await resetUserPassword(currentUser.value.id, resetForm.password)
    ElMessage.success('密码重置成功')
    resetDialogVisible.value = false
  } catch (error) {
    console.error('重置密码失败:', error)
    ElMessage.error(error.message || '重置密码失败')
  } finally {
    resetting.value = false
  }
}

const handleDeleteUser = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除教师 "${row.username}" 吗？`, '确认删除', { type: 'warning' })
    await apiDeleteUser(row.id)
    ElMessage.success('教师已删除')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error(error.message || '删除失败')
    }
  }
}

onMounted(() => { loadData() })
</script>

<style scoped>
@import './common.css';

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}
</style>
