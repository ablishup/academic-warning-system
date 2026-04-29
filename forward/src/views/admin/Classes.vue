<template>
  <div class="admin-page">
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
        <BatchImportButtons module="class" />
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
          <el-select v-model="filterForm.major_id" placeholder="全部专业" clearable style="width: 180px">
            <el-option v-for="m in majorOptions" :key="m.id" :label="m.name" :value="m.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="搜索">
          <el-input v-model="filterForm.search" placeholder="班级名称" clearable style="width: 200px" />
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
    <el-card class="list-card" shadow="hover">
      <el-table :data="filteredClasses" v-loading="loading" stripe>
        <el-table-column type="index" width="50" />
        <el-table-column label="班级" min-width="180">
          <template #default="{ row }">
            <div class="class-info">
              <div class="info-name">{{ row.name }}</div>
              <div class="info-meta">{{ row.grade }}级 · {{ row.major }}</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="辅导员" width="120">
          <template #default="{ row }">
            {{ row.counselor_name || '未分配' }}
          </template>
        </el-table-column>
        <el-table-column label="学生数" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ row.student_count }}人</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="预警人数" width="100">
          <template #default="{ row }">
            <span :class="{ 'warning-text': row.warning_count > 0 }">{{ row.warning_count }}人</span>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="120">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="260" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="editClass(row)">编辑</el-button>
            <el-button type="success" link size="small" @click="manageStudents(row)">学生管理</el-button>
            <el-button type="warning" link size="small" @click="assignCounselor(row)">分配辅导员</el-button>
            <el-button type="danger" link size="small" @click="deleteClass(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增/编辑班级弹窗 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑班级' : '新增班级'" width="500px">
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
            <el-form-item label="专业" prop="major_id">
              <el-select v-model="classForm.major_id" placeholder="选择专业" style="width: 100%">
                <el-option v-for="m in majorOptions" :key="m.id" :label="m.name" :value="m.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="辅导员">
          <el-select v-model="classForm.counselor_id" placeholder="选择辅导员" style="width: 100%" clearable>
            <el-option v-for="c in counselorOptions" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="班级描述">
          <el-input v-model="classForm.description" type="textarea" :rows="3" placeholder="请输入班级描述（可选）" />
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
        <el-table :data="currentClassStudents" height="400" v-loading="studentLoading" size="small">
          <el-table-column type="index" width="50" />
          <el-table-column label="学生" min-width="150">
            <template #default="{ row }">
              <div class="student-info">
                <div class="student-meta">
                  <div class="info-name">{{ row.name }}</div>
                  <div class="info-meta">{{ row.student_no }}</div>
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="性别" width="80">
            <template #default="{ row }">
              {{ row.gender === 'male' || row.gender === 1 ? '男' : (row.gender === 'female' || row.gender === 2 ? '女' : '-') }}
            </template>
          </el-table-column>
          <el-table-column prop="phone" label="手机号" width="120" />
          <el-table-column label="预警" width="80">
            <template #default="{ row }">
              <el-tag v-if="row.warning_count > 0" type="danger" size="small">{{ row.warning_count }}</el-tag>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100" fixed="right">
            <template #default="{ row }">
              <el-button type="danger" link size="small" @click="handleRemoveStudent(row)">移除</el-button>
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
            <el-option v-for="c in counselorOptions" :key="c.id" :label="c.name" :value="c.id" />
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
import { ref, reactive, onMounted, computed } from 'vue'
import BatchImportButtons from '@/components/BatchImportButtons.vue'
import { Plus, Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getAdminClasses, createClass, updateClass, deleteClass as apiDeleteClass,
  getCounselorOptions, getMajorList, getClassStudents, addStudentsToClass,
  removeStudentFromClass as apiRemoveStudentFromClass, getStudentOptions
} from '@/api/admin'
import { formatDate } from './common'

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

const filterForm = reactive({ grade: '', major_id: null, search: '' })
const classes = ref([])
const counselorOptions = ref([])
const majorOptions = ref([])
const availableStudentOptions = ref([])

const classForm = reactive({
  name: '', grade: '', major_id: null, counselor_id: null, description: ''
})

const classRules = {
  name: [{ required: true, message: '请输入班级名称', trigger: 'blur' }],
  grade: [{ required: true, message: '请选择年级', trigger: 'change' }],
  major_id: [{ required: true, message: '请选择专业', trigger: 'change' }]
}

// 前端筛选
const filteredClasses = computed(() => {
  let list = classes.value
  if (filterForm.grade) {
    list = list.filter(c => c.grade === filterForm.grade)
  }
  if (filterForm.major_id) {
    list = list.filter(c => c.major_id === filterForm.major_id)
  }
  if (filterForm.search) {
    const kw = filterForm.search.toLowerCase()
    list = list.filter(c => c.name && c.name.toLowerCase().includes(kw))
  }
  return list
})

const loadData = async () => {
  loading.value = true
  try {
    const res = await getAdminClasses()
    if (res.code === 200) {
      classes.value = res.data || []
    }
  } catch (error) {
    console.error('加载班级失败:', error)
    ElMessage.error('加载班级失败')
  } finally {
    loading.value = false
  }
}

const loadCounselors = async () => {
  try {
    const res = await getCounselorOptions()
    if (res.code === 200) {
      const list = res.data?.results || res.data || []
      counselorOptions.value = list.map(u => ({
        id: u.id,
        name: (u.last_name + u.first_name) || u.username
      }))
    }
  } catch (error) {
    console.error('加载辅导员列表失败:', error)
  }
}

const loadMajors = async () => {
  try {
    const res = await getMajorList()
    if (res.code === 200) {
      majorOptions.value = res.data || []
    }
  } catch (error) {
    console.error('加载专业列表失败:', error)
  }
}

const handleFilter = () => {}
const resetFilter = () => {
  filterForm.grade = ''
  filterForm.major_id = null
  filterForm.search = ''
}

const openAddDialog = () => {
  isEdit.value = false
  Object.assign(classForm, { name: '', grade: '', major_id: null, counselor_id: null, description: '' })
  dialogVisible.value = true
}

const editClass = (row) => {
  isEdit.value = true
  currentClass.value = row
  Object.assign(classForm, {
    name: row.name, grade: row.grade, major_id: row.major_id,
    counselor_id: row.counselor_id, description: row.description || ''
  })
  dialogVisible.value = true
}

const submitClass = async () => {
  const valid = await classFormRef.value?.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    if (isEdit.value) {
      await updateClass(currentClass.value.id, classForm)
      ElMessage.success('班级更新成功')
    } else {
      await createClass(classForm)
      ElMessage.success('班级创建成功')
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

const manageStudents = async (row) => {
  currentClass.value = row
  studentDialogVisible.value = true
  studentLoading.value = true
  try {
    const res = await getClassStudents(row.id)
    if (res.code === 200) {
      currentClassStudents.value = res.data || []
    }
  } catch (error) {
    console.error('加载班级学生失败:', error)
    ElMessage.error('加载班级学生失败')
  } finally {
    studentLoading.value = false
  }
}

const showAddStudentDialog = async () => {
  selectedStudents.value = []
  addStudentDialogVisible.value = true
  try {
    const res = await getStudentOptions({ unassigned: 'true' })
    if (res.code === 200) {
      const list = res.data || []
      availableStudentOptions.value = list.map(s => ({
        value: s.id,
        label: `${s.student_no} - ${s.name}`
      }))
    }
  } catch (error) {
    console.error('加载可选学生失败:', error)
  }
}

const confirmAddStudents = async () => {
  if (selectedStudents.value.length === 0) {
    ElMessage.warning('请选择要添加的学生')
    return
  }
  addingStudents.value = true
  try {
    await addStudentsToClass(currentClass.value.id, selectedStudents.value)
    ElMessage.success(`成功添加 ${selectedStudents.value.length} 名学生`)
    addStudentDialogVisible.value = false
    manageStudents(currentClass.value)
  } catch (error) {
    console.error('添加失败:', error)
    ElMessage.error('添加失败')
  } finally {
    addingStudents.value = false
  }
}

const handleRemoveStudent = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要将 ${row.name} 从班级中移除吗？`, '确认', { type: 'warning' })
    await apiRemoveStudentFromClass(currentClass.value.id, row.id)
    ElMessage.success('已移除')
    manageStudents(currentClass.value)
  } catch (error) {
    if (error !== 'cancel') {
      console.error('移除失败:', error)
      ElMessage.error('移除失败')
    }
  }
}

const assignCounselor = (row) => {
  currentClass.value = row
  selectedCounselor.value = row.counselor_id
  counselorDialogVisible.value = true
}

const confirmAssignCounselor = async () => {
  if (!selectedCounselor.value) {
    ElMessage.warning('请选择辅导员')
    return
  }
  assigning.value = true
  try {
    await updateClass(currentClass.value.id, { counselor_id: selectedCounselor.value })
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

const deleteClass = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除班级 "${row.name}" 吗？`, '确认删除', { type: 'warning' })
    await apiDeleteClass(row.id)
    ElMessage.success('班级已删除')
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
  loadCounselors()
  loadMajors()
})
</script>

<style scoped>
@import './common.css';

.class-info {
  display: flex;
  flex-direction: column;
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

.student-meta {
  display: flex;
  flex-direction: column;
}
</style>
