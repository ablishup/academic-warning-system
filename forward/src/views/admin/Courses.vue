<template>
  <div class="admin-page">
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
          <el-input v-model="filterForm.search" placeholder="课程名称/课程代码" clearable style="width: 250px" />
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
    <el-card class="list-card" shadow="hover">
      <el-table :data="filteredCourses" v-loading="loading" stripe>
        <el-table-column type="index" width="50" />
        <el-table-column label="课程" min-width="200">
          <template #default="{ row }">
            <div class="course-info">
              <div class="info-name">{{ row.name }}</div>
              <div class="info-meta">{{ row.code }}</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="任课教师" width="120">
          <template #default="{ row }">
            {{ getTeacherName(row.teacher_id) }}
          </template>
        </el-table-column>
        <el-table-column prop="semester" label="学期" width="120" />
        <el-table-column prop="credit" label="学分" width="80" />
        <el-table-column prop="student_count" label="学生数" width="80" />
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small">{{ getStatusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="editCourse(row)">编辑</el-button>
            <el-button type="success" link size="small" @click="manageStudents(row)">学生管理</el-button>
            <el-button type="danger" link size="small" @click="deleteCourse(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增/编辑课程弹窗 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑课程' : '新增课程'" width="600px">
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
            <el-option v-for="t in teacherOptions" :key="t.id" :label="t.name" :value="t.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="学期" prop="semester">
          <el-select v-model="courseForm.semester" placeholder="选择学期" style="width: 100%">
            <el-option label="2024-2025-1" value="2024-2025-1" />
            <el-option label="2024-2025-2" value="2024-2025-2" />
          </el-select>
        </el-form-item>
        <el-form-item label="课程描述">
          <el-input v-model="courseForm.description" type="textarea" :rows="3" placeholder="请输入课程描述" />
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
        <div class="manage-header">
          <h4>{{ currentCourse.name }} - 已选学生 ({{ currentCourseStudents.length }})</h4>
        </div>
        <el-table :data="currentCourseStudents" height="250" size="small">
          <el-table-column prop="student_no" label="学号" width="100" />
          <el-table-column prop="name" label="姓名" />
          <el-table-column label="操作" width="80">
            <template #default="{ row }">
              <el-button type="danger" link size="small" @click="removeStudent(row)">移除</el-button>
            </template>
          </el-table-column>
        </el-table>
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
import { ref, reactive, onMounted, computed } from 'vue'
import { Plus, Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getAdminCourses, createCourse, updateCourse, deleteCourse as apiDeleteCourse,
  getTeacherOptions, getCourseStudents, addStudentsToCourse,
  removeStudentFromCourse, getStudentOptions
} from '@/api/admin'
import { getStatusTagType, getStatusLabel } from './common'

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const studentDialogVisible = ref(false)
const isEdit = ref(false)
const courseFormRef = ref(null)
const currentCourse = ref(null)
const currentCourseStudents = ref([])
const selectedStudents = ref([])

const filterForm = reactive({ semester: '', status: '', search: '' })
const courses = ref([])
const teacherOptions = ref([])

const courseForm = reactive({
  name: '', code: '', credit: 3, hours: 48, teacher_id: null,
  semester: '', description: '', status: 'active'
})

const courseRules = {
  name: [{ required: true, message: '请输入课程名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入课程代码', trigger: 'blur' }],
  credit: [{ required: true, message: '请输入学分', trigger: 'change' }],
  teacher_id: [{ required: true, message: '请选择任课教师', trigger: 'change' }],
  semester: [{ required: true, message: '请选择学期', trigger: 'change' }]
}

// 前端筛选（后端目前不支持筛选参数）
const filteredCourses = computed(() => {
  let list = courses.value
  if (filterForm.semester) {
    list = list.filter(c => c.semester === filterForm.semester)
  }
  if (filterForm.status) {
    list = list.filter(c => c.status === filterForm.status)
  }
  if (filterForm.search) {
    const kw = filterForm.search.toLowerCase()
    list = list.filter(c =>
      (c.name && c.name.toLowerCase().includes(kw)) ||
      (c.code && c.code.toLowerCase().includes(kw))
    )
  }
  return list
})

const loadData = async () => {
  loading.value = true
  try {
    const res = await getAdminCourses()
    if (res.code === 200) {
      courses.value = res.data || []
    }
  } catch (error) {
    console.error('加载课程失败:', error)
    ElMessage.error('加载课程失败')
  } finally {
    loading.value = false
  }
}

const loadTeachers = async () => {
  try {
    const res = await getTeacherOptions()
    if (res.code === 200) {
      const list = res.data?.results || res.data || []
      teacherOptions.value = list.map(u => ({
        id: u.id,
        name: u.last_name + u.first_name || u.username
      }))
    }
  } catch (error) {
    console.error('加载教师列表失败:', error)
  }
}

const getTeacherName = (teacherId) => {
  const t = teacherOptions.value.find(opt => opt.id === teacherId)
  return t?.name || '-'
}

const handleFilter = () => {}
const resetFilter = () => {
  filterForm.semester = ''
  filterForm.status = ''
  filterForm.search = ''
}

const openAddDialog = () => {
  isEdit.value = false
  Object.assign(courseForm, { name: '', code: '', credit: 3, hours: 48, teacher_id: null, semester: '', description: '', status: 'active' })
  dialogVisible.value = true
}

const editCourse = (row) => {
  isEdit.value = true
  currentCourse.value = row
  Object.assign(courseForm, {
    name: row.name, code: row.code, credit: row.credit, hours: row.hours,
    teacher_id: row.teacher_id, semester: row.semester, description: row.description, status: row.status
  })
  dialogVisible.value = true
}

const submitCourse = async () => {
  const valid = await courseFormRef.value?.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    if (isEdit.value) {
      await updateCourse(currentCourse.value.id, courseForm)
      ElMessage.success('课程更新成功')
    } else {
      await createCourse(courseForm)
      ElMessage.success('课程创建成功')
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

const deleteCourse = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除课程 "${row.name}" 吗？`, '确认删除', { type: 'warning' })
    await apiDeleteCourse(row.id)
    ElMessage.success('课程已删除')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error(error.message || '删除失败')
    }
  }
}

const manageStudents = async (row) => {
  currentCourse.value = row
  currentCourseStudents.value = []
  selectedStudents.value = []
  studentDialogVisible.value = true
  try {
    const res = await getCourseStudents(row.id)
    if (res.code === 200) {
      currentCourseStudents.value = res.data || []
    }
  } catch (error) {
    console.error('加载课程学生失败:', error)
    ElMessage.error('加载课程学生失败')
  }
}

const removeStudent = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要将 ${row.name} 从课程中移除吗？`, '确认', { type: 'warning' })
    await removeStudentFromCourse(currentCourse.value.id, row.id)
    ElMessage.success('已移除')
    manageStudents(currentCourse.value)
  } catch (error) {
    if (error !== 'cancel') {
      console.error('移除失败:', error)
      ElMessage.error('移除失败')
    }
  }
}

const addStudents = async () => {
  if (selectedStudents.value.length === 0) {
    ElMessage.warning('请选择要添加的学生')
    return
  }
  try {
    await addStudentsToCourse(currentCourse.value.id, selectedStudents.value)
    ElMessage.success(`成功添加 ${selectedStudents.value.length} 名学生`)
    selectedStudents.value = []
    manageStudents(currentCourse.value)
  } catch (error) {
    console.error('添加失败:', error)
    ElMessage.error('添加失败')
  }
}

const loadStudentOptions = async () => {
  try {
    const res = await getStudentOptions()
    if (res.code === 200) {
      const list = res.data || []
      studentOptions.value = list.map(s => ({
        value: s.id,
        label: `${s.student_no} - ${s.name}`
      }))
    }
  } catch (error) {
    console.error('加载学生列表失败:', error)
  }
}

onMounted(() => {
  loadData()
  loadTeachers()
  loadStudentOptions()
})
</script>

<style scoped>
@import './common.css';

.course-info {
  display: flex;
  flex-direction: column;
}

.student-manage h4 {
  margin: 0 0 12px 0;
  color: #374151;
  font-size: 14px;
}

.manage-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.add-students {
  margin-top: 8px;
}
</style>
