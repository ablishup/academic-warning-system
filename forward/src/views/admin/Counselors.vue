<template>
  <div class="admin-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <h1>辅导员管理</h1>
        <p>管理辅导员信息及班级分配</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="openAddDialog">
          <el-icon><Plus /></el-icon>
          新增辅导员
        </el-button>
        <BatchImportButtons module="counselor" />
      </div>
    </div>

    <!-- 筛选栏 -->
    <el-card class="filter-card" shadow="hover">
      <el-form :model="filterForm" inline>
        <el-form-item label="院系">
          <el-select v-model="filterForm.department" placeholder="全部院系" clearable style="width: 180px">
            <el-option v-for="dept in departments" :key="dept" :label="dept" :value="dept" />
          </el-select>
        </el-form-item>
        <el-form-item label="搜索">
          <el-input v-model="filterForm.search" placeholder="姓名/工号" clearable style="width: 200px" />
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

    <!-- 辅导员列表 -->
    <el-card class="list-card" shadow="hover" v-loading="loading">
      <el-table :data="counselors" stripe>
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column label="辅导员" min-width="150">
          <template #default="{ row }">
            <div class="counselor-info">
              <div class="info-name">{{ row.name || row.username }}</div>
              <div class="info-meta">{{ row.username }}</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="employee_no" label="工号" width="120" />
        <el-table-column prop="department" label="所属院系" min-width="150" show-overflow-tooltip />
        <el-table-column prop="phone" label="联系电话" width="130" />
        <el-table-column label="管理班级" width="100">
          <template #default="{ row }">
            <el-tag type="primary" size="small">{{ row.classCount || 0 }} 个</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="260" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewDetail(row)">
              <el-icon><View /></el-icon>详情
            </el-button>
            <el-button type="warning" link size="small" @click="openEditDialog(row)">
              <el-icon><Edit /></el-icon>编辑
            </el-button>
            <el-button type="success" link size="small" @click="manageClasses(row)">
              <el-icon><School /></el-icon>分配班级
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 辅导员详情弹窗 -->
    <el-dialog v-model="detailDialogVisible" title="辅导员详情" width="600px">
      <div v-if="selectedCounselor" class="counselor-detail">
        <div class="detail-header">
          <div class="detail-info">
            <h3>{{ selectedCounselor.name || selectedCounselor.username }}</h3>
            <p>工号：{{ selectedCounselor.employee_no }}</p>
          </div>
        </div>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="用户名">{{ selectedCounselor.username }}</el-descriptions-item>
          <el-descriptions-item label="工号">{{ selectedCounselor.employee_no }}</el-descriptions-item>
          <el-descriptions-item label="院系">{{ selectedCounselor.department || '-' }}</el-descriptions-item>
          <el-descriptions-item label="电话">{{ selectedCounselor.phone || '-' }}</el-descriptions-item>
          <el-descriptions-item label="邮箱">{{ selectedCounselor.email || '-' }}</el-descriptions-item>
          <el-descriptions-item label="办公地点">{{ selectedCounselor.office || '-' }}</el-descriptions-item>
        </el-descriptions>
        <div class="detail-section">
          <h4>管理的班级</h4>
          <div v-if="counselorClasses.length === 0" class="empty-text">暂无管理的班级</div>
          <el-tag v-for="cls in counselorClasses" :key="cls.id" type="primary" size="small" class="class-tag">
            {{ cls.name }} ({{ cls.student_count }}人)
          </el-tag>
        </div>
      </div>
    </el-dialog>

    <!-- 班级分配弹窗 -->
    <el-dialog v-model="assignDialogVisible" title="分配班级" width="700px">
      <div v-if="selectedCounselor" class="assign-dialog">
        <div class="dialog-header">
          <span class="counselor-name">{{ selectedCounselor.name || selectedCounselor.username }}</span>
          <span class="counselor-no">工号：{{ selectedCounselor.employee_no }}</span>
        </div>
        <el-divider />
        <!-- 已分配班级 -->
        <div class="section">
          <div class="section-title">
            <span>已分配班级</span>
            <el-tag type="info" size="small">{{ counselorClasses.length }} 个</el-tag>
          </div>
          <el-table :data="counselorClasses" size="small" v-loading="classesLoading">
            <el-table-column prop="name" label="班级名称" min-width="150" />
            <el-table-column prop="grade" label="年级" width="100" />
            <el-table-column prop="student_count" label="学生数" width="100" />
            <el-table-column label="操作" width="100" fixed="right">
              <template #default="{ row }">
                <el-button type="danger" link size="small" @click="removeClass(row)">移除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
        <el-divider />
        <!-- 可分配班级 -->
        <div class="section">
          <div class="section-title">
            <span>可分配班级</span>
            <el-tag type="success" size="small">{{ availableClasses.length }} 个</el-tag>
          </div>
          <el-table :data="availableClasses" size="small" v-loading="availableLoading" @selection-change="handleSelectionChange">
            <el-table-column type="selection" width="55" />
            <el-table-column prop="name" label="班级名称" min-width="150" />
            <el-table-column prop="grade" label="年级" width="100" />
            <el-table-column prop="student_count" label="学生数" width="100" />
          </el-table>
        </div>
      </div>
      <template #footer>
        <el-button @click="assignDialogVisible = false">关闭</el-button>
        <el-button type="primary" :disabled="selectedClasses.length === 0" @click="confirmAssign">
          分配选中班级 ({{ selectedClasses.length }})
        </el-button>
      </template>
    </el-dialog>

    <!-- 编辑辅导员弹窗 -->
    <el-dialog v-model="editDialogVisible" title="编辑辅导员" width="600px">
      <el-form :model="editForm" :rules="editRules" ref="editFormRef" label-width="100px">
        <el-form-item label="姓名" prop="name">
          <el-input v-model="editForm.name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="工号" prop="employee_no">
          <el-input v-model="editForm.employee_no" placeholder="请输入工号" />
        </el-form-item>
        <el-form-item label="院系">
          <el-select v-model="editForm.department" placeholder="请选择院系" clearable style="width: 100%">
            <el-option v-for="dept in departments" :key="dept" :label="dept" :value="dept" />
          </el-select>
        </el-form-item>
        <el-form-item label="电话">
          <el-input v-model="editForm.phone" placeholder="请输入电话" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="editForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="办公室">
          <el-input v-model="editForm.office" placeholder="请输入办公室" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="editSubmitting" @click="submitEdit">保存</el-button>
      </template>
    </el-dialog>

    <!-- 新增辅导员弹窗 -->
    <el-dialog v-model="addDialogVisible" title="新增辅导员" width="600px">
      <el-form :model="addForm" :rules="addRules" ref="addFormRef" label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="addForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="addForm.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <el-form-item label="姓名">
          <el-row :gutter="10">
            <el-col :span="12"><el-input v-model="addForm.last_name" placeholder="姓" /></el-col>
            <el-col :span="12"><el-input v-model="addForm.first_name" placeholder="名" /></el-col>
          </el-row>
        </el-form-item>
        <el-form-item label="工号">
          <el-input v-model="addForm.student_no" placeholder="请输入工号" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="addForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="电话">
          <el-input v-model="addForm.phone" placeholder="请输入电话" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="addForm.is_active" active-text="启用" inactive-text="禁用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="addSubmitting" @click="submitAdd">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Search, View, School, Edit, Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import BatchImportButtons from '@/components/BatchImportButtons.vue'
import {
  getCounselorList, getCounselorDetail, getCounselorClasses,
  getAvailableClasses, assignClassesToCounselor, removeClassFromCounselor,
  getDepartmentList, updateCounselor, createUser
} from '@/api/admin'

const loading = ref(false)
const classesLoading = ref(false)
const availableLoading = ref(false)
const detailDialogVisible = ref(false)
const assignDialogVisible = ref(false)
const editDialogVisible = ref(false)
const editSubmitting = ref(false)
const addDialogVisible = ref(false)
const addSubmitting = ref(false)
const selectedCounselor = ref(null)
const counselorClasses = ref([])
const availableClasses = ref([])
const selectedClasses = ref([])
const editForm = reactive({ name: '', employee_no: '', department: '', phone: '', email: '', office: '' })
const editFormRef = ref(null)
const editRules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  employee_no: [{ required: true, message: '请输入工号', trigger: 'blur' }]
}
const addForm = reactive({
  username: '', password: '', first_name: '', last_name: '',
  student_no: '', role: 'counselor', email: '', phone: '', is_active: true
})
const addFormRef = ref(null)
const addRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur', min: 6 }]
}

const filterForm = reactive({ department: '', search: '' })
const pagination = reactive({ page: 1, pageSize: 10, total: 0 })
const counselors = ref([])
const departments = ref([])

const loadData = async () => {
  loading.value = true
  try {
    const params = { page: pagination.page, page_size: pagination.pageSize, ...filterForm }
    const res = await getCounselorList(params)
    if (res.code === 200) {
      counselors.value = res.data?.results || res.data || []
      pagination.total = res.data?.count || counselors.value.length
      // 加载每个辅导员的班级数量
      for (const counselor of counselors.value) {
        try {
          const classRes = await getCounselorClasses(counselor.id)
          if (classRes.code === 200) {
            counselor.classCount = classRes.data?.length || 0
          }
        } catch (error) {
          counselor.classCount = 0
        }
      }
    }
  } catch (error) {
    console.error('加载辅导员列表失败:', error)
    ElMessage.error('加载辅导员列表失败')
  } finally {
    loading.value = false
  }
}

const handleFilter = () => { pagination.page = 1; loadData() }
const resetFilter = () => { filterForm.department = ''; filterForm.search = ''; pagination.page = 1; loadData() }

const loadDepartments = async () => {
  try {
    const res = await getDepartmentList()
    if (res.code === 200) {
      departments.value = res.data || []
    }
  } catch (error) {
    console.error('加载院系列表失败:', error)
  }
}
const handleSizeChange = (val) => { pagination.pageSize = val; loadData() }
const handlePageChange = (val) => { pagination.page = val; loadData() }

const viewDetail = async (row) => {
  selectedCounselor.value = row
  detailDialogVisible.value = true
  counselorClasses.value = []
  try {
    const res = await getCounselorClasses(row.id)
    if (res.code === 200) counselorClasses.value = res.data || []
  } catch (error) {
    console.error('加载班级失败:', error)
  }
}

const manageClasses = async (row) => {
  selectedCounselor.value = row
  selectedClasses.value = []
  assignDialogVisible.value = true
  classesLoading.value = true
  availableLoading.value = true
  try {
    const [classesRes, availableRes] = await Promise.all([
      getCounselorClasses(row.id),
      getAvailableClasses()
    ])
    if (classesRes.code === 200) counselorClasses.value = classesRes.data || []
    if (availableRes.code === 200) availableClasses.value = availableRes.data || []
  } catch (error) {
    console.error('加载班级数据失败:', error)
    ElMessage.error('加载班级数据失败')
  } finally {
    classesLoading.value = false
    availableLoading.value = false
  }
}

const openEditDialog = (row) => {
  selectedCounselor.value = row
  Object.assign(editForm, {
    name: row.name || '',
    employee_no: row.employee_no || '',
    department: row.department || '',
    phone: row.phone || '',
    email: row.email || '',
    office: row.office || ''
  })
  editDialogVisible.value = true
}

const openAddDialog = () => {
  Object.assign(addForm, {
    username: '', password: '', first_name: '', last_name: '',
    student_no: '', role: 'counselor', email: '', phone: '', is_active: true
  })
  addDialogVisible.value = true
}

const submitAdd = async () => {
  const valid = await addFormRef.value?.validate().catch(() => false)
  if (!valid) return
  addSubmitting.value = true
  try {
    await createUser(addForm)
    ElMessage.success('辅导员创建成功')
    addDialogVisible.value = false
    loadData()
  } catch (error) {
    console.error('创建失败:', error)
    ElMessage.error(error.message || '创建失败')
  } finally {
    addSubmitting.value = false
  }
}

const submitEdit = async () => {
  const valid = await editFormRef.value?.validate().catch(() => false)
  if (!valid) return
  editSubmitting.value = true
  try {
    await updateCounselor(selectedCounselor.value.id, editForm)
    ElMessage.success('辅导员信息更新成功')
    editDialogVisible.value = false
    loadData()
  } catch (error) {
    console.error('更新失败:', error)
    ElMessage.error(error.message || '更新失败')
  } finally {
    editSubmitting.value = false
  }
}

const handleSelectionChange = (selection) => { selectedClasses.value = selection }

const confirmAssign = async () => {
  if (selectedClasses.value.length === 0) return
  try {
    const classIds = selectedClasses.value.map(item => item.id)
    const res = await assignClassesToCounselor(selectedCounselor.value.id, classIds)
    if (res.code === 200) {
      ElMessage.success('班级分配成功')
      manageClasses(selectedCounselor.value)
      loadData()
    }
  } catch (error) {
    console.error('分配失败:', error)
    ElMessage.error('分配失败')
  }
}

const removeClass = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要将 "${row.name}" 从该辅导员管理的班级中移除吗？`, '确认移除', { type: 'warning' })
    const res = await removeClassFromCounselor(selectedCounselor.value.id, row.id)
    if (res.code === 200) {
      ElMessage.success('移除成功')
      manageClasses(selectedCounselor.value)
      loadData()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('移除失败:', error)
      ElMessage.error('移除失败')
    }
  }
}

onMounted(() => {
  loadData()
  loadDepartments()
})
</script>

<style scoped>
@import './common.css';

.counselor-info {
  display: flex;
  flex-direction: column;
}

.counselor-detail {
  padding: 8px 0;
}

.detail-header {
  margin-bottom: 16px;
}

.detail-header h3 {
  margin: 0 0 4px 0;
  font-size: 18px;
}

.detail-header p {
  margin: 0;
  color: #6b7280;
  font-size: 14px;
}

.detail-section {
  margin-top: 20px;
}

.detail-section h4 {
  margin: 0 0 12px 0;
  font-size: 15px;
  color: #374151;
}

.empty-text {
  color: #9ca3af;
  font-size: 14px;
}

.class-tag {
  margin: 4px;
}

.dialog-header {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.counselor-name {
  font-weight: 600;
  font-size: 16px;
}

.counselor-no {
  color: #6b7280;
  font-size: 13px;
}

.section {
  margin: 12px 0;
}

.section-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  font-weight: 500;
}
</style>
