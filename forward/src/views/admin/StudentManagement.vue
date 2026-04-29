<template>
  <div class="admin-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <h1>学生管理</h1>
        <p>管理学生学籍信息</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="openAddDialog">
          <el-icon><Plus /></el-icon>
          新增学生
        </el-button>
        <BatchImportButtons module="student" />
      </div>
    </div>

    <!-- 筛选栏 -->
    <el-card class="filter-card" shadow="hover">
      <el-form :model="filterForm" inline>
        <el-form-item label="搜索">
          <el-input v-model="filterForm.keyword" placeholder="学号/姓名" clearable style="width: 250px" />
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

    <!-- 学生列表 -->
    <el-card class="list-card" shadow="hover">
      <el-table :data="students" v-loading="loading" stripe>
        <el-table-column type="index" width="50" />
        <el-table-column prop="student_no" label="学号" width="120" />
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column label="性别" width="80">
          <template #default="{ row }">
            {{ row.gender === 1 ? '男' : (row.gender === 2 ? '女' : '未知') }}
          </template>
        </el-table-column>
        <el-table-column prop="class_name" label="班级" width="150" show-overflow-tooltip />
        <el-table-column prop="phone" label="手机号" width="120" />
        <el-table-column prop="email" label="邮箱" min-width="180" show-overflow-tooltip />
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="editStudent(row)">编辑</el-button>
            <el-button type="warning" link size="small" @click="createAccount(row)">生成账号</el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row)">删除</el-button>
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
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑学生' : '新增学生'" width="600px">
      <el-form :model="studentForm" label-width="100px" :rules="studentRules" ref="studentFormRef">
        <el-form-item label="学号" prop="student_no">
          <el-input v-model="studentForm.student_no" placeholder="请输入学号" />
        </el-form-item>
        <el-form-item label="姓名" prop="name">
          <el-input v-model="studentForm.name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="性别">
          <el-select v-model="studentForm.gender" placeholder="选择性别" style="width: 100%">
            <el-option label="男" :value="1" />
            <el-option label="女" :value="2" />
            <el-option label="未知" :value="0" />
          </el-select>
        </el-form-item>
        <el-form-item label="班级">
          <el-select v-model="studentForm.class_id" placeholder="选择班级" style="width: 100%" filterable clearable>
            <el-option v-for="c in classOptions" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="studentForm.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="studentForm.email" placeholder="请输入邮箱" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitStudent" :loading="submitting">确认</el-button>
      </template>
    </el-dialog>

    <!-- 生成账号弹窗 -->
    <el-dialog v-model="accountDialogVisible" title="生成登录账号" width="400px">
      <p style="margin-bottom: 16px; color: #606266;">
        正在为 <strong>{{ currentStudent?.name }}</strong> ({{ currentStudent?.student_no }}) 生成账号
      </p>
      <el-form :model="accountForm" label-width="100px">
        <el-form-item label="密码">
          <el-input v-model="accountForm.password" placeholder="默认：学号+123" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="accountDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitCreateAccount" :loading="creatingAccount">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import BatchImportButtons from '@/components/BatchImportButtons.vue'
import { Plus, Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getStudentList, createStudent, updateStudent, deleteStudent, createStudentAccount, getAdminClasses
} from '@/api/admin'

const loading = ref(false)
const submitting = ref(false)
const creatingAccount = ref(false)
const dialogVisible = ref(false)
const accountDialogVisible = ref(false)
const isEdit = ref(false)
const studentFormRef = ref(null)
const currentStudent = ref(null)

const filterForm = reactive({ keyword: '' })
const pagination = reactive({ page: 1, pageSize: 10, total: 0 })
const students = ref([])
const classOptions = ref([])

const studentForm = reactive({
  student_no: '', name: '', gender: 1, class_id: null, phone: '', email: ''
})

const studentRules = {
  student_no: [{ required: true, message: '请输入学号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }]
}

const accountForm = reactive({ password: '' })

const loadData = async () => {
  loading.value = true
  try {
    const params = { page: pagination.page, page_size: pagination.pageSize, keyword: filterForm.keyword }
    const res = await getStudentList(params)
    if (res.code === 200) {
      students.value = res.data?.results || []
      pagination.total = res.data?.count || 0
    }
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const loadClasses = async () => {
  try {
    const res = await getAdminClasses()
    if (res.code === 200) {
      classOptions.value = res.data || []
    }
  } catch (error) {
    console.error('加载班级列表失败:', error)
  }
}

const handleFilter = () => { pagination.page = 1; loadData() }
const resetFilter = () => {
  filterForm.keyword = ''
  pagination.page = 1; loadData()
}
const handleSizeChange = (val) => { pagination.pageSize = val; loadData() }
const handleCurrentChange = (val) => { pagination.page = val; loadData() }

const openAddDialog = () => {
  isEdit.value = false
  Object.assign(studentForm, { student_no: '', name: '', gender: 1, class_id: null, phone: '', email: '' })
  dialogVisible.value = true
}

const editStudent = (row) => {
  isEdit.value = true
  currentStudent.value = row
  Object.assign(studentForm, {
    student_no: row.student_no, name: row.name, gender: row.gender || 1,
    class_id: row.class_id, phone: row.phone || '', email: row.email || ''
  })
  dialogVisible.value = true
}

const submitStudent = async () => {
  const valid = await studentFormRef.value?.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    if (isEdit.value) {
      await updateStudent(currentStudent.value.id, studentForm)
      ElMessage.success('学生更新成功')
    } else {
      await createStudent(studentForm)
      ElMessage.success('学生创建成功')
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

const createAccount = (row) => {
  currentStudent.value = row
  accountForm.password = ''
  accountDialogVisible.value = true
}

const submitCreateAccount = async () => {
  if (!currentStudent.value) return
  creatingAccount.value = true
  try {
    const res = await createStudentAccount(currentStudent.value.id, accountForm.password || undefined)
    if (res.code === 200) {
      ElMessage.success(`账号创建成功，用户名：${res.data?.username}，密码：${res.data?.password}`)
      accountDialogVisible.value = false
    }
  } catch (error) {
    console.error('创建账号失败:', error)
    ElMessage.error(error.message || '创建账号失败')
  } finally {
    creatingAccount.value = false
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除学生 "${row.name}" 吗？`, '确认删除', { type: 'warning' })
    await deleteStudent(row.id)
    ElMessage.success('学生已删除')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error(error.message || '删除失败')
    }
  }
}

onMounted(() => {
  loadData()
  loadClasses()
})
</script>

<style scoped>
@import './common.css';

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}
</style>
