<template>
  <div class="counselors-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <h1>辅导员管理</h1>
        <p>管理辅导员信息及班级分配</p>
      </div>
    </div>

    <!-- 筛选栏 -->
    <el-card class="filter-card" shadow="never">
      <el-form :model="filterForm" inline>
        <el-form-item label="院系">
          <el-select v-model="filterForm.department" placeholder="全部院系" clearable style="width: 180px">
            <el-option v-for="dept in departments" :key="dept" :label="dept" :value="dept" />
          </el-select>
        </el-form-item>
        <el-form-item label="搜索">
          <el-input
            v-model="filterForm.search"
            placeholder="姓名/工号"
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

    <!-- 辅导员列表 -->
    <el-card class="counselors-card" shadow="never" v-loading="loading">
      <el-table :data="counselors" stripe>
        <el-table-column label="辅导员" min-width="150">
          <template #default="{ row }">
            <div class="counselor-info">
              <el-avatar :size="40" :style="{ background: getAvatarColor(row.user?.first_name || row.user?.username) }">
                {{ (row.user?.first_name || row.user?.username || '?').charAt(0) }}
              </el-avatar>
              <div class="info-text">
                <div class="name">{{ row.user?.first_name || row.user?.username }}</div>
                <div class="username">{{ row.user?.username }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="employee_no" label="工号" width="120" />
        <el-table-column prop="department" label="所属院系" min-width="150" />
        <el-table-column prop="phone" label="联系电话" width="130" />
        <el-table-column label="管理班级" width="100">
          <template #default="{ row }">
            <el-tag type="primary" size="small">
              {{ row.classCount || 0 }} 个
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewDetail(row)">
              <el-icon><View /></el-icon>
              详情
            </el-button>
            <el-button type="success" link size="small" @click="manageClasses(row)">
              <el-icon><School /></el-icon>
              分配班级
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
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
          <el-avatar :size="64" :style="{ background: getAvatarColor(selectedCounselor.user?.first_name) }">
            {{ (selectedCounselor.user?.first_name || selectedCounselor.user?.username || '?').charAt(0) }}
          </el-avatar>
          <div class="detail-info">
            <h3>{{ selectedCounselor.user?.first_name || selectedCounselor.user?.username }}</h3>
            <p>工号：{{ selectedCounselor.employee_no }}</p>
          </div>
        </div>

        <el-descriptions :column="2" border class="detail-descriptions">
          <el-descriptions-item label="用户名">{{ selectedCounselor.user?.username }}</el-descriptions-item>
          <el-descriptions-item label="工号">{{ selectedCounselor.employee_no }}</el-descriptions-item>
          <el-descriptions-item label="院系">{{ selectedCounselor.department || '-' }}</el-descriptions-item>
          <el-descriptions-item label="电话">{{ selectedCounselor.phone || '-' }}</el-descriptions-item>
          <el-descriptions-item label="邮箱">{{ selectedCounselor.user?.email || '-' }}</el-descriptions-item>
          <el-descriptions-item label="办公地点">{{ selectedCounselor.office || '-' }}</el-descriptions-item>
        </el-descriptions>

        <div class="detail-section">
          <h4>管理的班级</h4>
          <div v-if="counselorClasses.length === 0" class="empty-text">暂无管理的班级</div>
          <el-tag
            v-for="cls in counselorClasses"
            :key="cls.id"
            type="primary"
            size="small"
            class="class-tag"
          >
            {{ cls.name }} ({{ cls.student_count }}人)
          </el-tag>
        </div>
      </div>
    </el-dialog>

    <!-- 班级分配弹窗 -->
    <el-dialog v-model="assignDialogVisible" title="分配班级" width="700px">
      <div v-if="selectedCounselor" class="assign-dialog">
        <div class="dialog-header">
          <span class="counselor-name">{{ selectedCounselor.user?.first_name || selectedCounselor.user?.username }}</span>
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
                <el-button type="danger" link size="small" @click="removeClass(row)">
                  移除
                </el-button>
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
          <el-table
            :data="availableClasses"
            size="small"
            v-loading="availableLoading"
            @selection-change="handleSelectionChange"
          >
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
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Search, View, School } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getCounselorList,
  getCounselorDetail,
  getCounselorClasses,
  getAvailableClasses,
  assignClassesToCounselor,
  removeClassFromCounselor
} from '@/api/admin'

// 状态
const loading = ref(false)
const classesLoading = ref(false)
const availableLoading = ref(false)
const detailDialogVisible = ref(false)
const assignDialogVisible = ref(false)
const selectedCounselor = ref(null)
const counselorClasses = ref([])
const availableClasses = ref([])
const selectedClasses = ref([])

// 筛选表单
const filterForm = reactive({
  department: '',
  search: ''
})

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

// 数据
const counselors = ref([])
const departments = ref(['计算机学院', '软件学院', '信息工程学院', '电子工程学院'])

// 加载辅导员列表
const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      ...filterForm
    }
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

// 筛选
const handleFilter = () => {
  pagination.page = 1
  loadData()
}

const resetFilter = () => {
  filterForm.department = ''
  filterForm.search = ''
  pagination.page = 1
  loadData()
}

// 分页
const handleSizeChange = (val) => {
  pagination.pageSize = val
  loadData()
}

const handlePageChange = (val) => {
  pagination.page = val
  loadData()
}

// 查看详情
const viewDetail = async (row) => {
  selectedCounselor.value = row
  detailDialogVisible.value = true

  // 加载班级列表
  try {
    const res = await getCounselorClasses(row.id)
    if (res.code === 200) {
      counselorClasses.value = res.data || []
    }
  } catch (error) {
    counselorClasses.value = []
  }
}

// 管理班级
const manageClasses = async (row) => {
  selectedCounselor.value = row
  selectedClasses.value = []
  assignDialogVisible.value = true

  // 加载已分配班级
  classesLoading.value = true
  try {
    const res = await getCounselorClasses(row.id)
    if (res.code === 200) {
      counselorClasses.value = res.data || []
    }
  } catch (error) {
    counselorClasses.value = []
  } finally {
    classesLoading.value = false
  }

  // 加载可分配班级
  availableLoading.value = true
  try {
    const res = await getAvailableClasses()
    if (res.code === 200) {
      availableClasses.value = res.data || []
    }
  } catch (error) {
    availableClasses.value = []
  } finally {
    availableLoading.value = false
  }
}

// 移除班级
const removeClass = async (cls) => {
  try {
    await ElMessageBox.confirm(
      `确定要移除班级 "${cls.name}" 吗？`,
      '确认移除',
      { type: 'warning' }
    )

    const res = await removeClassFromCounselor(selectedCounselor.value.id, cls.id)
    if (res.code === 200) {
      ElMessage.success('移除成功')
      // 刷新列表
      counselorClasses.value = counselorClasses.value.filter(c => c.id !== cls.id)
      // 添加到可分配列表
      availableClasses.value.push(cls)
      // 更新计数
      selectedCounselor.value.classCount = counselorClasses.value.length
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('移除失败')
    }
  }
}

// 选择班级
const handleSelectionChange = (selection) => {
  selectedClasses.value = selection
}

// 确认分配
const confirmAssign = async () => {
  if (selectedClasses.value.length === 0) return

  try {
    const classIds = selectedClasses.value.map(c => c.id)
    const res = await assignClassesToCounselor(selectedCounselor.value.id, classIds)
    if (res.code === 200) {
      ElMessage.success(`成功分配 ${res.data?.assigned_count || 0} 个班级`)
      // 刷新列表
      const newClasses = await getCounselorClasses(selectedCounselor.value.id)
      if (newClasses.code === 200) {
        counselorClasses.value = newClasses.data || []
      }
      // 从可分配列表中移除
      const assignedIds = selectedClasses.value.map(c => c.id)
      availableClasses.value = availableClasses.value.filter(c => !assignedIds.includes(c.id))
      // 清空选择
      selectedClasses.value = []
      // 更新计数
      selectedCounselor.value.classCount = counselorClasses.value.length
    }
  } catch (error) {
    ElMessage.error('分配失败')
  }
}

// 工具函数
const getAvatarColor = (name) => {
  const colors = ['#667eea', '#f093fb', '#4facfe', '#43e97b', '#fa709a', '#30cfd0']
  let hash = 0
  for (let i = 0; i < (name?.length || 0); i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash)
  }
  return colors[Math.abs(hash) % colors.length]
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.counselors-page {
  max-width: 1200px;
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
  font-size: 14px;
}

.filter-card {
  margin-bottom: 20px;
  border-radius: 12px;
}

.counselors-card {
  border-radius: 12px;
}

.counselor-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.info-text .name {
  font-weight: 600;
  color: #1f2937;
}

.info-text .username {
  font-size: 12px;
  color: #6b7280;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e5e7eb;
}

/* 详情弹窗 */
.counselor-detail {
  padding: 0 10px;
}

.detail-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.detail-info h3 {
  margin: 0 0 8px 0;
  font-size: 20px;
  color: #1f2937;
}

.detail-info p {
  margin: 0;
  color: #6b7280;
  font-size: 14px;
}

.detail-descriptions {
  margin: 20px 0;
}

.detail-section {
  margin-top: 20px;
}

.detail-section h4 {
  margin-bottom: 12px;
  color: #374151;
}

.empty-text {
  color: #9ca3af;
  font-size: 14px;
}

.class-tag {
  margin: 4px;
}

/* 分配弹窗 */
.assign-dialog {
  max-height: 60vh;
  overflow-y: auto;
}

.dialog-header {
  display: flex;
  align-items: center;
  gap: 16px;
}

.counselor-name {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.counselor-no {
  color: #6b7280;
  font-size: 14px;
}

.section {
  margin: 20px 0;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-weight: 600;
  color: #374151;
}
</style>
