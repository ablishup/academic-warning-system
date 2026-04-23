<template>
  <div class="course-students-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <el-button link @click="goBack">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <h1>{{ courseName }} - 学生列表</h1>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="showUploadDialog = true">
          <el-icon><Upload /></el-icon>
          导入数据
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon blue">
            <el-icon><User /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalStudents }}</div>
            <div class="stat-label">学生总数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon green">
            <el-icon><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.normalStudents }}</div>
            <div class="stat-label">正常学生</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon orange">
            <el-icon><Warning /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.warningStudents }}</div>
            <div class="stat-label">预警学生</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon red">
            <el-icon><CircleClose /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.criticalStudents }}</div>
            <div class="stat-label">高危学生</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 学生列表 -->
    <el-card class="students-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="card-title">
            <el-icon><List /></el-icon>
            学生名单
          </span>
          <div class="header-actions">
            <el-select
              v-model="selectedClass"
              placeholder="全部班级"
              clearable
              style="width: 180px"
              @change="handleClassChange"
            >
              <el-option
                v-for="cls in classOptions"
                :key="cls.id"
                :label="`${cls.name} (${cls.student_count}人)`"
                :value="cls.id"
              />
            </el-select>
            <el-input
              v-model="searchQuery"
              placeholder="搜索学生姓名或学号"
              style="width: 250px"
              clearable
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-button type="primary" @click="refreshData" :loading="loading">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>

      <el-table
        :data="filteredStudents"
        v-loading="loading"
        style="width: 100%"
        :default-sort="{ prop: 'composite_score', order: 'ascending' }"
      >
        <el-table-column prop="student_no" label="学号" width="120" sortable />
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="gender" label="性别" width="80" />
        <el-table-column prop="class_name" label="班级" width="180" />
        <el-table-column prop="composite_score" label="综合得分" width="120" sortable>
          <template #default="{ row }">
            <el-progress
              :percentage="Math.round(row.composite_score)"
              :status="row.composite_score >= 60 ? 'success' : 'exception'"
              :stroke-width="6"
            />
          </template>
        </el-table-column>
        <el-table-column prop="learning_stats.avg_progress" label="视频进度" width="100">
          <template #default="{ row }">
            <span>{{ row.learning_stats?.avg_progress || 0 }}%</span>
          </template>
        </el-table-column>
        <el-table-column prop="homework_stats.avg_score" label="作业均分" width="100">
          <template #default="{ row }">
            <span>{{ row.homework_stats?.avg_score || 0 }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="exam_stats.avg_score" label="考试均分" width="100">
          <template #default="{ row }">
            <span>{{ row.exam_stats?.avg_score || 0 }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="warning_level" label="预警等级" width="100" sortable>
          <template #default="{ row }">
            <el-tag
              :type="getWarningType(row.warning_level)"
              effect="dark"
              size="small"
            >
              {{ getWarningLabel(row.warning_level) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="viewDetail(row)">
              <el-icon><View /></el-icon>
              详情
            </el-button>
            <el-button type="warning" link @click="sendReminder(row)">
              <el-icon><Message /></el-icon>
              提醒
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && filteredStudents.length === 0" description="暂无学生数据" />
    </el-card>

    <!-- 学生详情弹窗 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="学生学情详情"
      width="800px"
      destroy-on-close
    >
      <div v-if="selectedStudent" class="student-detail">
        <div class="detail-header">
          <div class="detail-info">
            <h3>{{ selectedStudent.name }}</h3>
            <p>学号：{{ selectedStudent.student_no }} | 班级：{{ selectedStudent.class_name }}</p>
          </div>
          <el-tag
            :type="getWarningType(selectedStudent.warning_level)"
            effect="dark"
            size="large"
          >
            {{ getWarningLabel(selectedStudent.warning_level) }}
          </el-tag>
        </div>

        <el-divider />

        <el-row :gutter="20" class="detail-stats">
          <el-col :span="8">
            <div class="detail-stat-item">
              <div class="stat-label">综合得分</div>
              <div class="stat-value" :class="selectedStudent.composite_score >= 60 ? 'success' : 'danger'">
                {{ selectedStudent.composite_score?.toFixed(1) }}
              </div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="detail-stat-item">
              <div class="stat-label">视频进度</div>
              <div class="stat-value">{{ selectedStudent.learning_stats?.avg_progress || 0 }}%</div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="detail-stat-item">
              <div class="stat-label">作业均分</div>
              <div class="stat-value">{{ selectedStudent.homework_stats?.avg_score || 0 }}</div>
            </div>
          </el-col>
        </el-row>

        <el-divider />

        <div class="detail-section">
          <h4>学习统计</h4>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="学习活动数">{{ selectedStudent.learning_stats?.activity_count || 0 }}</el-descriptions-item>
            <el-descriptions-item label="学习时长">{{ selectedStudent.learning_stats?.total_duration || 0 }}分钟</el-descriptions-item>
            <el-descriptions-item label="作业提交">{{ selectedStudent.homework_stats?.submit_count || 0 }}</el-descriptions-item>
            <el-descriptions-item label="考试次数">{{ selectedStudent.exam_stats?.exam_count || 0 }}</el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
    </el-dialog>

    <!-- 导入数据弹窗 -->
    <el-dialog
      v-model="showUploadDialog"
      title="导入学生数据"
      width="500px"
    >
      <el-upload
        drag
        action=""
        :auto-upload="false"
        accept=".xlsx,.xls"
        :on-change="handleFileChange"
        class="upload-area"
      >
        <el-icon :size="48"><Upload /></el-icon>
        <div class="el-upload__text">
          拖拽文件到此处或 <em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持 .xlsx, .xls 格式文件，单次不超过1000条数据
          </div>
        </template>
      </el-upload>
      <template #footer>
        <el-button @click="showUploadDialog = false">取消</el-button>
        <el-button type="primary" :loading="uploading" @click="confirmUpload">
          确认导入
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  ArrowLeft, User, Warning, CircleCheck, CircleClose,
  List, Search, Refresh, View, Message, Upload
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getCourseStudents } from '@/api/teacher'

const route = useRoute()
const router = useRouter()
const courseId = computed(() => route.params.courseId)

// 状态
const loading = ref(false)
const uploading = ref(false)
const searchQuery = ref('')
const selectedClass = ref(null)
const detailDialogVisible = ref(false)
const showUploadDialog = ref(false)
const selectedStudent = ref(null)
const courseName = ref('')

// 数据
const students = ref([])
const classOptions = ref([])
const stats = ref({
  totalStudents: 0,
  normalStudents: 0,
  warningStudents: 0,
  criticalStudents: 0
})

// 过滤后的学生列表
const filteredStudents = computed(() => {
  let result = students.value

  // 搜索过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(s =>
      s.name.toLowerCase().includes(query) ||
      s.student_no.includes(query)
    )
  }

  return result
})

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const params = {}
    if (selectedClass.value) {
      params.class_id = selectedClass.value
    }

    const res = await getCourseStudents(courseId.value, params)
    if (res.code === 200) {
      const data = res.data
      courseName.value = data.course.name
      students.value = data.students || []
      classOptions.value = data.classes || []

      // 计算统计
      const total = students.value.length
      const critical = students.value.filter(s => s.warning_level === 'high').length
      const warning = students.value.filter(s => s.warning_level === 'medium').length
      const normal = total - critical - warning

      stats.value = {
        totalStudents: total,
        normalStudents: normal,
        warningStudents: warning,
        criticalStudents: critical
      }
    }
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 班级筛选变化
const handleClassChange = () => {
  loadData()
}

// 刷新数据
const refreshData = () => {
  loadData()
  ElMessage.success('数据已刷新')
}

// 返回
const goBack = () => {
  router.push('/teacher/dashboard')
}


// 预警类型映射
const getWarningType = (level) => {
  const types = {
    'high': 'danger',
    'medium': 'warning',
    'low': 'info',
    null: 'success'
  }
  return types[level] || 'success'
}

// 预警标签映射
const getWarningLabel = (level) => {
  const labels = {
    'high': '高危',
    'medium': '预警',
    'low': '低危',
    null: '正常'
  }
  return labels[level] || '正常'
}

// 查看详情
const viewDetail = (student) => {
  selectedStudent.value = student
  detailDialogVisible.value = true
}

// 发送提醒
const sendReminder = (student) => {
  ElMessageBox.confirm(
    `确定向 ${student.name} 发送学习提醒吗？`,
    '发送提醒',
    { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
  ).then(() => {
    ElMessage.success(`已向 ${student.name} 发送提醒`)
  })
}

// 文件上传
const handleFileChange = (file) => {
  console.log('Selected file:', file)
}

const confirmUpload = () => {
  uploading.value = true
  setTimeout(() => {
    uploading.value = false
    showUploadDialog.value = false
    ElMessage.success('数据导入成功')
  }, 1500)
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.course-students-page {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-left h1 {
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.stats-row {
  margin-bottom: 24px;
}

.stat-card :deep(.el-card__body) {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
}

.stat-icon.blue {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.green {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-icon.orange {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.stat-icon.red {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #1f2937;
}

.stat-label {
  font-size: 13px;
  color: #6b7280;
  margin-top: 4px;
}

.students-card {
  border-radius: 12px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 16px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.student-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.success {
  color: #67c23a;
}

.warning {
  color: #e6a23c;
}

.danger {
  color: #f56c6c;
}

/* 详情弹窗 */
.student-detail {
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

.detail-header .el-tag {
  margin-left: auto;
}

.detail-stats {
  margin: 20px 0;
}

.detail-stat-item {
  text-align: center;
  padding: 16px;
  background: #f8fafc;
  border-radius: 8px;
}

.detail-stat-item .stat-label {
  font-size: 13px;
  color: #6b7280;
  margin-bottom: 8px;
}

.detail-stat-item .stat-value {
  font-size: 24px;
  font-weight: 700;
}

.detail-section h4 {
  margin: 20px 0 16px;
  color: #1f2937;
  font-size: 16px;
}

.upload-area {
  width: 100%;
}

.upload-area :deep(.el-upload) {
  width: 100%;
}

.upload-area :deep(.el-upload-dragger) {
  width: 100%;
  padding: 40px 20px;
}
</style>
