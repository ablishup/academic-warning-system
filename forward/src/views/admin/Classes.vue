<template>
  <div class="classes-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <h1>班级管理</h1>
        <p>管理班级信息，分配学生和辅导员</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="openAddDialog">
          <el-icon><Plus /></el-icon>
          新增班级
        </el-button>
      </div>
    </div>

    <!-- 筛选栏 -->
    <el-card class="filter-card" shadow="hover">
      <el-form :model="filterForm" inline>
        <el-form-item label="年级">
          <el-select v-model="filterForm.grade" placeholder="全部年级" clearable style="width: 150px">
            <el-option label="2021级" value="2021" />
            <el-option label="2022级" value="2022" />
            <el-option label="2023级" value="2023" />
            <el-option label="2024级" value="2024" />
          </el-select>
        </el-form-item>
        <el-form-item label="专业">
          <el-select v-model="filterForm.major" placeholder="全部专业" clearable style="width: 180px">
            <el-option label="计算机科学与技术" value="计算机科学与技术" />
            <el-option label="软件工程" value="软件工程" />
            <el-option label="网络工程" value="网络工程" />
            <el-option label="信息安全" value="信息安全" />
          </el-select>
        </el-form-item>
        <el-form-item label="搜索">
          <el-input
            v-model="filterForm.search"
            placeholder="班级名称"
            clearable
            style="width: 200px"
          />
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

    <!-- 班级列表 -->
    <el-card class="classes-card" shadow="hover">
      <el-table :data="classes" v-loading="loading" stripe>
        <el-table-column type="index" width="50" />
        <el-table-column label="班级" min-width="180">
          <template #default="{ row }">
            <div class="class-info">
              <div class="class-name">{{ row.name }}</div>
              <div class="class-meta">{{ row.grade }}级 · {{ row.major }}</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="counselor_name" label="辅导员" width="120" />
        <el-table-column prop="student_count" label="学生数" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ row.student_count }}人</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="warning_count" label="预警人数" width="100">
          <template #default="{ row }">
            <span :class="{ 'warning-text': row.warning_count > 0 }">
              {{ row.warning_count }}人
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="120">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="editClass(row)">
              编辑
            </el-button>
            <el-button type="success" link size="small" @click="manageStudents(row)">
              学生管理
            </el-button>
            <el-button type="warning" link size="small" @click="assignCounselor(row)">
              分配辅导员
            </el-button>
            <el-button type="danger" link size="small" @click="deleteClass(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 新增/编辑班级弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑班级' : '新增班级'"
      width="500px"
    >
      <el-form :model="classForm" label-width="100px" :rules="classRules" ref="classFormRef">
        <el-form-item label="班级名称" prop="name">
          <el-input v-model="classForm.name" placeholder="如：计算机2101" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="年级" prop="grade">
              <el-select v-model="classForm.grade" placeholder="选择年级" style="width: 100%">
                <el-option label="2021级" value="2021" />
                <el-option label="2022级" value="2022" />
                <el-option label="2023级" value="2023" />
                <el-option label="2024级" value="2024" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="专业" prop="major">
              <el-select v-model="classForm.major" placeholder="选择专业" style="width: 100%">
                <el-option label="计算机科学与技术" value="计算机科学与技术" />
                <el-option label="软件工程" value="软件工程" />
                <el-option label="网络工程" value="网络工程" />
                <el-option label="信息安全" value="信息安全" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="辅导员">
          <el-select v-model="classForm.counselor_id" placeholder="选择辅导员" style="width: 100%" clearable>
            <el-option
              v-for="counselor in counselorOptions"
              :key="counselor.id"
              :label="counselor.name"
              :value="counselor.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="班级描述">
          <el-input
            v-model="classForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入班级描述（可选）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitClass" :loading="submitting">确认</el-button>
      </template>
    </el-dialog>

    <!-- 学生管理弹窗 -->
    <el-dialog v-model="studentDialogVisible" title="班级学生管理" width="800px">
      <div v-if="currentClass" class="student-manage">
        <div class="manage-header">
          <h4>{{ currentClass.name }} - 学生列表 ({{ currentClassStudents.length }}人)</h4>
          <el-button type="primary" size="small" @click="showAddStudentDialog">
            <el-icon><Plus /></el-icon>
            添加学生
          </el-button>
        </div>
        <el-table :data="currentClassStudents" height="400" v-loading="studentLoading">
          <el-table-column type="index" width="50" />
          <el-table-column label="学生" min-width="150">
            <template #default="{ row }">
              <div class="student-info">
                <el-avatar :size="32" :style="{ background: getAvatarColor(row.name) }">
                  {{ row.name?.charAt(0) }}
                </el-avatar>
                <div class="student-meta">
                  <div class="student-name">{{ row.name }}</div>
                  <div class="student-no">{{ row.student_no }}</div>
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="gender" label="性别" width="80">
            <template #default="{ row }">
              {{ row.gender === 'male' ? '男' : '女' }}
            </template>
          </el-table-column>
          <el-table-column prop="phone" label="手机号" width="120" />
          <el-table-column prop="warning_count" label="预警" width="80">
            <template #default="{ row }">
              <el-tag v-if="row.warning_count > 0" type="danger" size="small">{{ row.warning_count }}</el-tag>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100" fixed="right">
            <template #default="{ row }">
              <el-button type="danger" link size="small" @click="removeStudentFromClass(row)">移除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>

    <!-- 添加学生弹窗 -->
    <el-dialog v-model="addStudentDialogVisible" title="添加学生到班级" width="500px" append-to-body>
      <el-select-v2
        v-model="selectedStudents"
        :options="availableStudentOptions"
        placeholder="选择要添加的学生"
        multiple
        filterable
        clearable
        style="width: 100%"
      />
      <template #footer>
        <el-button @click="addStudentDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmAddStudents" :loading="addingStudents">
          添加 ({{ selectedStudents.length }})
        </el-button>
      </template>
    </el-dialog>

    <!-- 分配辅导员弹窗 -->
    <el-dialog v-model="counselorDialogVisible" title="分配辅导员" width="400px">
      <el-form label-width="100px">
        <el-form-item label="当前辅导员">
          <span v-if="currentClass?.counselor_name">{{ currentClass.counselor_name }}</span>
          <el-tag v-else type="info" size="small">未分配</el-tag>
        </el-form-item>
        <el-form-item label="新辅导员">
          <el-select v-model="selectedCounselor" placeholder="选择辅导员" style="width: 100%">
            <el-option
              v-for="counselor in counselorOptions"
              :key="counselor.id"
              :label="counselor.name"
              :value="counselor.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="counselorDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmAssignCounselor" :loading="assigning">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Plus, Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const submitting = ref(false)
const studentLoading = ref(false)
const addingStudents = ref(false)
const assigning = ref(false)
const dialogVisible = ref(false)
const studentDialogVisible = ref(false)
const addStudentDialogVisible = ref(false)
const counselorDialogVisible = ref(false)
const isEdit = ref(false)
const classFormRef = ref(null)
const currentClass = ref(null)
const currentClassStudents = ref([])
const selectedStudents = ref([])
const selectedCounselor = ref(null)

// 筛选表单
const filterForm = reactive({
  grade: '',
  major: '',
  search: ''
})

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

// 班级列表
const classes = ref([])

// 辅导员选项
const counselorOptions = ref([
  { id: 1, name: '李老师' },
  { id: 2, name: '王老师' },
  { id: 3, name: '张老师' },
  { id: 4, name: '赵老师' }
])

// 可用学生选项
const availableStudentOptions = ref([
  { value: 10, label: '孙八 (2021010)' },
  { value: 11, label: '周九 (2021011)' },
  { value: 12, label: '吴十 (2021012)' },
  { value: 13, label: '郑十一 (2021013)' },
  { value: 14, label: '陈十二 (2021014)' }
])

// 班级表单
const classForm = reactive({
  name: '',
  grade: '',
  major: '',
  counselor_id: null,
  description: ''
})

const classRules = {
  name: [{ required: true, message: '请输入班级名称', trigger: 'blur' }],
  grade: [{ required: true, message: '请选择年级', trigger: 'change' }],
  major: [{ required: true, message: '请选择专业', trigger: 'change' }]
}

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 500))
    classes.value = [
      { id: 1, name: '计算机2101', grade: '2021', major: '计算机科学与技术', counselor_name: '李老师', counselor_id: 1, student_count: 45, warning_count: 3, created_at: '2021-09-01' },
      { id: 2, name: '计算机2102', grade: '2021', major: '计算机科学与技术', counselor_name: '李老师', counselor_id: 1, student_count: 42, warning_count: 1, created_at: '2021-09-01' },
      { id: 3, name: '软件工程2101', grade: '2021', major: '软件工程', counselor_name: '王老师', counselor_id: 2, student_count: 48, warning_count: 5, created_at: '2021-09-01' },
      { id: 4, name: '软件工程2102', grade: '2021', major: '软件工程', counselor_name: '王老师', counselor_id: 2, student_count: 44, warning_count: 2, created_at: '2021-09-01' },
      { id: 5, name: '网络工程2101', grade: '2021', major: '网络工程', counselor_name: '张老师', counselor_id: 3, student_count: 40, warning_count: 0, created_at: '2021-09-01' },
      { id: 6, name: '计算机2201', grade: '2022', major: '计算机科学与技术', counselor_name: '赵老师', counselor_id: 4, student_count: 46, warning_count: 2, created_at: '2022-09-01' }
    ]
    pagination.total = classes.value.length
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 筛选
const handleFilter = () => {
  pagination.page = 1
  loadData()
}

const resetFilter = () => {
  filterForm.grade = ''
  filterForm.major = ''
  filterForm.search = ''
  pagination.page = 1
  loadData()
}

// 分页
const handleSizeChange = (val) => {
  pagination.pageSize = val
  loadData()
}

const handleCurrentChange = (val) => {
  pagination.page = val
  loadData()
}

// 打开新增弹窗
const openAddDialog = () => {
  isEdit.value = false
  classForm.name = ''
  classForm.grade = ''
  classForm.major = ''
  classForm.counselor_id = null
  classForm.description = ''
  dialogVisible.value = true
}

// 编辑班级
const editClass = (row) => {
  isEdit.value = true
  currentClass.value = row
  classForm.name = row.name
  classForm.grade = row.grade
  classForm.major = row.major
  classForm.counselor_id = row.counselor_id
  classForm.description = row.description || ''
  dialogVisible.value = true
}

// 提交班级
const submitClass = async () => {
  const valid = await classFormRef.value?.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 500))
    ElMessage.success(isEdit.value ? '班级更新成功' : '班级创建成功')
    dialogVisible.value = false
    loadData()
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败')
  } finally {
    submitting.value = false
  }
}

// 管理学生
const manageStudents = async (row) => {
  currentClass.value = row
  studentDialogVisible.value = true
  studentLoading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 500))
    currentClassStudents.value = [
      { id: 1, student_no: '2021001', name: '张三', gender: 'male', phone: '13800138001', warning_count: 1 },
      { id: 2, student_no: '2021002', name: '李四', gender: 'female', phone: '13800138002', warning_count: 0 },
      { id: 3, student_no: '2021003', name: '王五', gender: 'male', phone: '13800138003', warning_count: 2 },
      { id: 4, student_no: '2021004', name: '赵六', gender: 'female', phone: '13800138004', warning_count: 0 },
      { id: 5, student_no: '2021005', name: '钱七', gender: 'male', phone: '13800138005', warning_count: 0 }
    ]
  } finally {
    studentLoading.value = false
  }
}

// 显示添加学生弹窗
const showAddStudentDialog = () => {
  selectedStudents.value = []
  addStudentDialogVisible.value = true
}

// 确认添加学生
const confirmAddStudents = async () => {
  if (selectedStudents.value.length === 0) {
    ElMessage.warning('请选择要添加的学生')
    return
  }
  addingStudents.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 500))
    ElMessage.success(`成功添加 ${selectedStudents.value.length} 名学生`)
    addStudentDialogVisible.value = false
    // 刷新学生列表
    manageStudents(currentClass.value)
  } catch (error) {
    console.error('添加失败:', error)
    ElMessage.error('添加失败')
  } finally {
    addingStudents.value = false
  }
}

// 从班级移除学生
const removeStudentFromClass = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要将 ${row.name} 从班级中移除吗？`, '确认', { type: 'warning' })
    await new Promise(resolve => setTimeout(resolve, 300))
    currentClassStudents.value = currentClassStudents.value.filter(s => s.id !== row.id)
    ElMessage.success('已移除')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('移除失败:', error)
    }
  }
}

// 分配辅导员
const assignCounselor = (row) => {
  currentClass.value = row
  selectedCounselor.value = row.counselor_id
  counselorDialogVisible.value = true
}

// 确认分配辅导员
const confirmAssignCounselor = async () => {
  if (!selectedCounselor.value) {
    ElMessage.warning('请选择辅导员')
    return
  }
  assigning.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 500))
    ElMessage.success('辅导员分配成功')
    counselorDialogVisible.value = false
    loadData()
  } catch (error) {
    console.error('分配失败:', error)
    ElMessage.error('分配失败')
  } finally {
    assigning.value = false
  }
}

// 删除班级
const deleteClass = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除班级 "${row.name}" 吗？`, '确认删除', { type: 'warning' })
    await new Promise(resolve => setTimeout(resolve, 500))
    ElMessage.success('班级已删除')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 工具函数
const getAvatarColor = (name) => {
  const colors = ['#667eea', '#f093fb', '#4facfe', '#43e97b', '#fa709a', '#30cfd0']
  let hash = 0
  for (let i = 0; i < name?.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash)
  return colors[Math.abs(hash) % colors.length]
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.classes-page {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.header-left h1 {
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 8px;
}

.header-left p {
  color: #6b7280;
}

.filter-card {
  margin-bottom: 24px;
  border-radius: 12px;
}

.classes-card {
  border-radius: 12px;
}

.class-info .class-name {
  font-weight: 500;
  color: #1f2937;
}

.class-info .class-meta {
  font-size: 12px;
  color: #6b7280;
  margin-top: 4px;
}

.warning-text {
  color: #ef4444;
  font-weight: 500;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

.student-manage .manage-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.student-manage h4 {
  margin: 0;
  color: #374151;
}

.student-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.student-meta .student-name {
  font-weight: 500;
  color: #1f2937;
}

.student-meta .student-no {
  font-size: 12px;
  color: #6b7280;
}
</style>
