<template>
  <div class="courses-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <h1>课程管理</h1>
        <p>管理系统课程，分配任课教师</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="openAddDialog">
          <el-icon><Plus /></el-icon>
          新增课程
        </el-button>
      </div>
    </div>

    <!-- 筛选栏 -->
    <el-card class="filter-card" shadow="hover">
      <el-form :model="filterForm" inline>
        <el-form-item label="学期">
          <el-select v-model="filterForm.semester" placeholder="全部学期" clearable style="width: 150px">
            <el-option label="2024-2025-1" value="2024-2025-1" />
            <el-option label="2024-2025-2" value="2024-2025-2" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="全部状态" clearable style="width: 150px">
            <el-option label="进行中" value="active" />
            <el-option label="已结束" value="ended" />
            <el-option label="未开始" value="pending" />
          </el-select>
        </el-form-item>
        <el-form-item label="搜索">
          <el-input
            v-model="filterForm.search"
            placeholder="课程名称/课程代码"
            clearable
            style="width: 250px"
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

    <!-- 课程列表 -->
    <el-card class="courses-card" shadow="hover">
      <el-table :data="courses" v-loading="loading" stripe>
        <el-table-column type="index" width="50" />
        <el-table-column label="课程" min-width="200">
          <template #default="{ row }">
            <div class="course-info">
              <div class="course-name">{{ row.name }}</div>
              <div class="course-code">{{ row.code }}</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="teacher_name" label="任课教师" width="120" />
        <el-table-column prop="semester" label="学期" width="120" />
        <el-table-column prop="credit" label="学分" width="80" />
        <el-table-column prop="student_count" label="学生数" width="80" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="editCourse(row)">
              编辑
            </el-button>
            <el-button type="success" link size="small" @click="manageStudents(row)">
              学生管理
            </el-button>
            <el-button type="danger" link size="small" @click="deleteCourse(row)">
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

    <!-- 新增/编辑课程弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑课程' : '新增课程'"
      width="600px"
    >
      <el-form :model="courseForm" label-width="100px" :rules="courseRules" ref="courseFormRef">
        <el-form-item label="课程名称" prop="name">
          <el-input v-model="courseForm.name" placeholder="请输入课程名称" />
        </el-form-item>
        <el-form-item label="课程代码" prop="code">
          <el-input v-model="courseForm.code" placeholder="请输入课程代码" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="学分" prop="credit">
              <el-input-number v-model="courseForm.credit" :min="0.5" :max="10" :step="0.5" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="学时" prop="hours">
              <el-input-number v-model="courseForm.hours" :min="8" :max="160" :step="8" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="任课教师" prop="teacher_id">
          <el-select v-model="courseForm.teacher_id" placeholder="选择任课教师" style="width: 100%" filterable>
            <el-option
              v-for="teacher in teacherOptions"
              :key="teacher.id"
              :label="teacher.name"
              :value="teacher.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="学期" prop="semester">
          <el-select v-model="courseForm.semester" placeholder="选择学期" style="width: 100%">
            <el-option label="2024-2025-1" value="2024-2025-1" />
            <el-option label="2024-2025-2" value="2024-2025-2" />
          </el-select>
        </el-form-item>
        <el-form-item label="课程描述">
          <el-input
            v-model="courseForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入课程描述"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="courseForm.status">
            <el-radio label="active">进行中</el-radio>
            <el-radio label="pending">未开始</el-radio>
            <el-radio label="ended">已结束</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitCourse" :loading="submitting">确认</el-button>
      </template>
    </el-dialog>

    <!-- 学生管理弹窗 -->
    <el-dialog v-model="studentDialogVisible" title="课程学生管理" width="700px">
      <div v-if="currentCourse" class="student-manage">
        <div class="current-students">
          <h4>已选学生 ({{ currentCourseStudents.length }})</h4>
          <el-table :data="currentCourseStudents" height="250" size="small">
            <el-table-column prop="student_no" label="学号" width="100" />
            <el-table-column prop="name" label="姓名" />
            <el-table-column label="操作" width="80">
              <template #default="{ row }">
                <el-button type="danger" link size="small" @click="removeStudent(row)">移除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
        <el-divider />
        <div class="add-students">
          <h4>添加学生</h4>
          <el-select-v2
            v-model="selectedStudents"
            :options="studentOptions"
            placeholder="选择要添加的学生"
            multiple
            filterable
            clearable
            style="width: 100%"
          />
          <el-button type="primary" @click="addStudents" style="margin-top: 12px">
            添加选中学生
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Plus, Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const studentDialogVisible = ref(false)
const isEdit = ref(false)
const courseFormRef = ref(null)
const currentCourse = ref(null)
const currentCourseStudents = ref([])
const selectedStudents = ref([])

// 筛选表单
const filterForm = reactive({
  semester: '',
  status: '',
  search: ''
})

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

// 课程列表
const courses = ref([])

// 教师选项
const teacherOptions = ref([
  { id: 1, name: '张教授' },
  { id: 2, name: '李教授' },
  { id: 3, name: '王教授' },
  { id: 4, name: '赵教授' }
])

// 学生选项
const studentOptions = ref([
  { value: 1, label: '张三 (2021001)' },
  { value: 2, label: '李四 (2021002)' },
  { value: 3, label: '王五 (2021003)' },
  { value: 4, label: '赵六 (2021004)' },
  { value: 5, label: '钱七 (2021005)' }
])

// 课程表单
const courseForm = reactive({
  name: '',
  code: '',
  credit: 3,
  hours: 48,
  teacher_id: null,
  semester: '',
  description: '',
  status: 'active'
})

const courseRules = {
  name: [{ required: true, message: '请输入课程名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入课程代码', trigger: 'blur' }],
  credit: [{ required: true, message: '请输入学分', trigger: 'change' }],
  teacher_id: [{ required: true, message: '请选择任课教师', trigger: 'change' }],
  semester: [{ required: true, message: '请选择学期', trigger: 'change' }]
}

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 500))
    courses.value = [
      { id: 1, name: '数据结构', code: 'CS201', credit: 4, hours: 64, teacher_name: '张教授', teacher_id: 1, semester: '2024-2025-1', student_count: 156, status: 'active', description: '计算机专业核心课程' },
      { id: 2, name: '算法设计', code: 'CS202', credit: 4, hours: 64, teacher_name: '李教授', teacher_id: 2, semester: '2024-2025-1', student_count: 142, status: 'active', description: '算法分析与设计' },
      { id: 3, name: '操作系统', code: 'CS301', credit: 4, hours: 64, teacher_name: '王教授', teacher_id: 3, semester: '2024-2025-1', student_count: 138, status: 'active', description: '操作系统原理' },
      { id: 4, name: '计算机网络', code: 'CS302', credit: 3, hours: 48, teacher_name: '赵教授', teacher_id: 4, semester: '2024-2025-2', student_count: 125, status: 'pending', description: '网络原理与应用' },
      { id: 5, name: '数据库原理', code: 'CS303', credit: 3, hours: 48, teacher_name: '张教授', teacher_id: 1, semester: '2024-2025-2', student_count: 118, status: 'pending', description: '数据库系统概论' },
      { id: 6, name: '编译原理', code: 'CS401', credit: 3, hours: 48, teacher_name: '李教授', teacher_id: 2, semester: '2024-2025-1', student_count: 98, status: 'ended', description: '编译器构造' }
    ]
    pagination.total = courses.value.length
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
  filterForm.semester = ''
  filterForm.status = ''
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
  courseForm.name = ''
  courseForm.code = ''
  courseForm.credit = 3
  courseForm.hours = 48
  courseForm.teacher_id = null
  courseForm.semester = ''
  courseForm.description = ''
  courseForm.status = 'active'
  dialogVisible.value = true
}

// 编辑课程
const editCourse = (row) => {
  isEdit.value = true
  currentCourse.value = row
  courseForm.name = row.name
  courseForm.code = row.code
  courseForm.credit = row.credit
  courseForm.hours = row.hours
  courseForm.teacher_id = row.teacher_id
  courseForm.semester = row.semester
  courseForm.description = row.description
  courseForm.status = row.status
  dialogVisible.value = true
}

// 提交课程
const submitCourse = async () => {
  const valid = await courseFormRef.value?.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 500))
    ElMessage.success(isEdit.value ? '课程更新成功' : '课程创建成功')
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
const manageStudents = (row) => {
  currentCourse.value = row
  currentCourseStudents.value = [
    { id: 1, student_no: '2021001', name: '张三' },
    { id: 2, student_no: '2021002', name: '李四' },
    { id: 3, student_no: '2021003', name: '王五' }
  ]
  selectedStudents.value = []
  studentDialogVisible.value = true
}

// 移除学生
const removeStudent = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要将 ${row.name} 从课程中移除吗？`, '确认', { type: 'warning' })
    await new Promise(resolve => setTimeout(resolve, 300))
    currentCourseStudents.value = currentCourseStudents.value.filter(s => s.id !== row.id)
    ElMessage.success('已移除')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('移除失败:', error)
    }
  }
}

// 添加学生
const addStudents = async () => {
  if (selectedStudents.value.length === 0) {
    ElMessage.warning('请选择要添加的学生')
    return
  }
  try {
    await new Promise(resolve => setTimeout(resolve, 500))
    ElMessage.success(`成功添加 ${selectedStudents.value.length} 名学生`)
    selectedStudents.value = []
  } catch (error) {
    console.error('添加失败:', error)
    ElMessage.error('添加失败')
  }
}

// 删除课程
const deleteCourse = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除课程 "${row.name}" 吗？`, '确认删除', { type: 'warning' })
    await new Promise(resolve => setTimeout(resolve, 500))
    ElMessage.success('课程已删除')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 工具函数
const getStatusTagType = (status) => {
  const types = { active: 'success', pending: 'info', ended: '' }
  return types[status] || ''
}

const getStatusLabel = (status) => {
  const labels = { active: '进行中', pending: '未开始', ended: '已结束' }
  return labels[status] || status
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.courses-page {
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

.courses-card {
  border-radius: 12px;
}

.course-info .course-name {
  font-weight: 500;
  color: #1f2937;
}

.course-info .course-code {
  font-size: 12px;
  color: #6b7280;
  margin-top: 4px;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

.student-manage h4 {
  margin-bottom: 12px;
  color: #374151;
}
</style>
