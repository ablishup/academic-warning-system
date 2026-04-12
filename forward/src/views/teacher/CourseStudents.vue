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
        :default-sort="{ prop: 'warningLevel', order: 'descending' }"
      >
        <el-table-column prop="studentNo" label="学号" width="120" sortable />
        <el-table-column prop="name" label="姓名" width="100">
          <template #default="{ row }">
            <div class="student-name">
              <el-avatar :size="32" :style="{ background: getAvatarColor(row.name) }">
                {{ row.name.charAt(0) }}
              </el-avatar>
              <span>{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="gender" label="性别" width="80" />
        <el-table-column prop="className" label="班级" width="150" />
        <el-table-column prop="avgScore" label="平均成绩" width="120" sortable>
          <template #default="{ row }">
            <el-progress
              :percentage="Math.round(row.avgScore)"
              :status="row.avgScore >= 60 ? 'success' : 'exception'"
              :stroke-width="6"
            />
          </template>
        </el-table-column>
        <el-table-column prop="attendanceRate" label="出勤率" width="100">
          <template #default="{ row }">
            <span :class="getAttendanceClass(row.attendanceRate)">
              {{ row.attendanceRate }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="videoProgress" label="视频进度" width="100">
          <template #default="{ row }">
            <span>{{ row.videoProgress }}%</span>
          </template>
        </el-table-column>
        <el-table-column prop="warningLevel" label="预警等级" width="100" sortable>
          <template #default="{ row }">
            <el-tag
              :type="getWarningType(row.warningLevel)"
              effect="dark"
              size="small"
            >
              {{ getWarningLabel(row.warningLevel) }}
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
          <el-avatar :size="64" :style="{ background: getAvatarColor(selectedStudent.name) }">
            {{ selectedStudent.name.charAt(0) }}
          </el-avatar>
          <div class="detail-info">
            <h3>{{ selectedStudent.name }}</h3>
            <p>学号：{{ selectedStudent.studentNo }} | 班级：{{ selectedStudent.className }}</p>
          </div>
          <el-tag
            :type="getWarningType(selectedStudent.warningLevel)"
            effect="dark"
            size="large"
          >
            {{ getWarningLabel(selectedStudent.warningLevel) }}
          </el-tag>
        </div>

        <el-divider />

        <el-row :gutter="20" class="detail-stats">
          <el-col :span="8">
            <div class="detail-stat-item">
              <div class="stat-label">平均成绩</div>
              <div class="stat-value" :class="selectedStudent.avgScore >= 60 ? 'success' : 'danger'">
                {{ selectedStudent.avgScore }}
              </div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="detail-stat-item">
              <div class="stat-label">出勤率</div>
              <div class="stat-value" :class="getAttendanceClass(selectedStudent.attendanceRate)">
                {{ selectedStudent.attendanceRate }}%
              </div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="detail-stat-item">
              <div class="stat-label">视频进度</div>
              <div class="stat-value">{{ selectedStudent.videoProgress }}%</div>
            </div>
          </el-col>
        </el-row>

        <el-divider />

        <div class="detail-section">
          <h4>学习趋势</h4>
          <div ref="trendChartRef" style="height: 200px"></div>
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
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import * as echarts from 'echarts'
import {
  ArrowLeft, User, Warning, CircleCheck, CircleClose,
  List, Search, Refresh, View, Message, Upload
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const courseId = computed(() => route.params.courseId)

// 状态
const loading = ref(false)
const uploading = ref(false)
const searchQuery = ref('')
const detailDialogVisible = ref(false)
const showUploadDialog = ref(false)
const selectedStudent = ref(null)
const trendChartRef = ref(null)
const courseName = ref('数据结构')

// 统计数据
const stats = ref({
  totalStudents: 45,
  normalStudents: 32,
  warningStudents: 10,
  criticalStudents: 3
})

// 学生列表数据（模拟）
const students = ref([
  { id: 1, studentNo: '2021001', name: '张三', gender: '男', className: '计算机2101', avgScore: 85, attendanceRate: 95, videoProgress: 88, warningLevel: 0 },
  { id: 2, studentNo: '2021002', name: '李四', gender: '女', className: '计算机2101', avgScore: 78, attendanceRate: 88, videoProgress: 75, warningLevel: 0 },
  { id: 3, studentNo: '2021003', name: '王五', gender: '男', className: '计算机2101', avgScore: 45, attendanceRate: 65, videoProgress: 40, warningLevel: 2 },
  { id: 4, studentNo: '2021004', name: '赵六', gender: '女', className: '计算机2101', avgScore: 92, attendanceRate: 98, videoProgress: 95, warningLevel: 0 },
  { id: 5, studentNo: '2021005', name: '钱七', gender: '男', className: '计算机2101', avgScore: 55, attendanceRate: 70, videoProgress: 60, warningLevel: 1 },
  { id: 6, studentNo: '2021006', name: '孙八', gender: '女', className: '计算机2101', avgScore: 38, attendanceRate: 55, videoProgress: 35, warningLevel: 2 },
  { id: 7, studentNo: '2021007', name: '周九', gender: '男', className: '计算机2101', avgScore: 72, attendanceRate: 82, videoProgress: 70, warningLevel: 0 },
  { id: 8, studentNo: '2021008', name: '吴十', gender: '女', className: '计算机2101', avgScore: 68, attendanceRate: 78, videoProgress: 65, warningLevel: 1 },
])

// 过滤后的学生列表
const filteredStudents = computed(() => {
  if (!searchQuery.value) return students.value
  const query = searchQuery.value.toLowerCase()
  return students.value.filter(s =>
    s.name.toLowerCase().includes(query) ||
    s.studentNo.includes(query)
  )
})

// 方法
const goBack = () => {
  router.push('/teacher/dashboard')
}

const refreshData = () => {
  loading.value = true
  setTimeout(() => {
    loading.value = false
    ElMessage.success('数据已刷新')
  }, 500)
}

const getAvatarColor = (name) => {
  const colors = ['#667eea', '#f093fb', '#4facfe', '#43e97b', '#fa709a', '#30cfd0']
  let hash = 0
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash)
  }
  return colors[Math.abs(hash) % colors.length]
}

const getWarningType = (level) => {
  const types = ['success', 'warning', 'danger']
  return types[level] || 'info'
}

const getWarningLabel = (level) => {
  const labels = ['正常', '预警', '高危']
  return labels[level] || '未知'
}

const getAttendanceClass = (rate) => {
  if (rate >= 90) return 'success'
  if (rate >= 70) return 'warning'
  return 'danger'
}

const viewDetail = async (student) => {
  selectedStudent.value = student
  detailDialogVisible.value = true
  await nextTick()
  initTrendChart()
}

const initTrendChart = () => {
  if (!trendChartRef.value) return
  const chart = echarts.init(trendChartRef.value)
  const option = {
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: ['第1周', '第2周', '第3周', '第4周', '第5周', '第6周', '第7周', '第8周'],
      axisLine: { lineStyle: { color: '#e0e0e0' } },
      axisLabel: { color: '#666' }
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 100,
      axisLine: { show: false },
      splitLine: { lineStyle: { color: '#f0f0f0' } },
      axisLabel: { color: '#666' }
    },
    series: [{
      data: [75, 78, 72, 80, 76, 82, 79, 85],
      type: 'line',
      smooth: true,
      symbol: 'circle',
      symbolSize: 8,
      itemStyle: { color: '#667eea' },
      lineStyle: { width: 3 },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(102, 126, 234, 0.3)' },
            { offset: 1, color: 'rgba(102, 126, 234, 0.05)' }
          ]
        }
      }
    }]
  }
  chart.setOption(option)
}

const sendReminder = (student) => {
  ElMessageBox.confirm(
    `确定向 ${student.name} 发送学习提醒吗？`,
    '发送提醒',
    { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
  ).then(() => {
    ElMessage.success(`已向 ${student.name} 发送提醒`)
  })
}

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
  refreshData()
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
