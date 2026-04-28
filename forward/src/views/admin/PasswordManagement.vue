<template>
  <div class="admin-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <h1>密码管理</h1>
        <p>管理系统所有账号的密码，支持直接重置</p>
      </div>
    </div>

    <!-- 筛选栏 -->
    <el-card class="filter-card" shadow="hover">
      <el-form :model="filterForm" inline>
        <el-form-item label="角色">
          <el-select v-model="filterForm.role" placeholder="全部角色" clearable style="width: 150px">
            <el-option label="学生" value="student" />
            <el-option label="教师" value="teacher" />
            <el-option label="辅导员" value="counselor" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filterForm.is_active" placeholder="全部状态" clearable style="width: 150px">
            <el-option label="启用" :value="true" />
            <el-option label="禁用" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item label="搜索">
          <el-input v-model="filterForm.search" placeholder="用户名/姓名/学号" clearable style="width: 250px" />
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

    <!-- 用户列表 -->
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
        <el-table-column prop="student_no" label="学号/工号" width="120" />
        <el-table-column label="角色" width="90">
          <template #default="{ row }">
            <el-tag :type="getRoleTagType(row.role)" size="small">{{ getRoleLabel(row.role) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="注册时间" width="120">
          <template #default="{ row }">
            {{ formatDate(row.date_joined) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button type="warning" link size="small" @click="resetPassword(row)">重置密码</el-button>
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

    <!-- 重置密码弹窗 -->
    <el-dialog v-model="resetDialogVisible" title="重置密码" width="400px">
      <p style="margin-bottom: 16px; color: #606266;">
        正在为 <strong>{{ currentUser?.username }}</strong> 重置密码
      </p>
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
import { Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getUserList, resetUserPassword } from '@/api/admin'
import { formatDate, getRoleTagType, getRoleLabel } from './common'

const loading = ref(false)
const resetting = ref(false)
const resetDialogVisible = ref(false)
const resetFormRef = ref(null)
const currentUser = ref(null)

const filterForm = reactive({ role: '', is_active: undefined, search: '' })
const pagination = reactive({ page: 1, pageSize: 10, total: 0 })
const users = ref([])

const resetForm = reactive({ password: '', confirmPassword: '' })
const resetRules = {
  password: [{ required: true, message: '请输入新密码', trigger: 'blur', min: 6 }],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== resetForm.password) callback(new Error('两次输入的密码不一致'))
        else callback()
      },
      trigger: 'blur'
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
  filterForm.role = ''; filterForm.is_active = undefined; filterForm.search = ''
  pagination.page = 1; loadData()
}
const handleSizeChange = (val) => { pagination.pageSize = val; loadData() }
const handleCurrentChange = (val) => { pagination.page = val; loadData() }

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

onMounted(() => { loadData() })
</script>

<style scoped>
@import './common.css';

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-meta .info-name {
  font-weight: 500;
  color: #303133;
}

.user-meta .info-meta {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}
</style>
