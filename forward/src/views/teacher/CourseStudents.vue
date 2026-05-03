<template>
  <div class="course-students-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <el-button link @click="goBack">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <div>
          <h1>{{ courseName }} - 学生列表</h1>
          <p>查看课程学生学情和预警情况</p>
        </div>
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
          <div class="stat-icon green">
            <el-icon :size="28"><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.normalStudents }}</div>
            <div class="stat-label">正常学生</div>
            <div class="stat-change success">
              <span>整体良好</span>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon blue">
            <el-icon :size="28"><InfoFilled /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.lowStudents }}</div>
            <div class="stat-label">低危学生</div>
            <div class="stat-change">
              <span>需留意</span>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon orange">
            <el-icon :size="28"><Warning /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.warningStudents }}</div>
            <div class="stat-label">中等预警</div>
            <div class="stat-change warning">
              <span>需关注</span>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon red">
            <el-icon :size="28"><CircleClose /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.criticalStudents }}</div>
            <div class="stat-label">高危学生</div>
            <div class="stat-change danger">
              <el-icon><ArrowUp /></el-icon>
              <span>需立即干预</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="charts-row">
      <el-col :span="12">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span class="card-title">
                <el-icon><PieChart /></el-icon>
                预警分布
              </span>
            </div>
          </template>
          <div ref="pieChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span class="card-title">
                <el-icon><Histogram /></el-icon>
                班级学生对比
              </span>
            </div>
          </template>
          <div ref="barChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 课程整体建议 -->
    <el-card v-if="courseSuggestion" class="suggestion-card" shadow="hover">
      <div class="suggestion-header">
        <el-icon :size="20"><MagicStick /></el-icon>
        <span>课程教学建议</span>
      </div>
      <p class="suggestion-text">{{ courseSuggestion }}</p>
    </el-card>

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
      >
        <el-table-column prop="student_no" label="学号" width="120" sortable />
        <el-table-column prop="name" label="姓名" width="100" />
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
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import * as echarts from 'echarts'
import {
  ArrowLeft, User, Warning, CircleCheck, CircleClose,
  List, Search, Refresh, View, Message, Upload, MagicStick,
  PieChart, Histogram, ArrowUp, InfoFilled
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getCourseStudents, getCourseStats } from '@/api/teacher'

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
  lowStudents: 0,
  criticalStudents: 0
})
const courseSuggestion = ref('')

// 图表引用
const pieChartRef = ref(null)
const barChartRef = ref(null)
let pieChart = null
let barChart = null

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

  // 按预警程度降序排列（高危 > 中等 > 低危 > 正常）
  const riskOrder = { high: 3, medium: 2, low: 1, null: 0 }
  result = [...result].sort((a, b) => {
    const aRisk = riskOrder[a.warning_level] || 0
    const bRisk = riskOrder[b.warning_level] || 0
    return bRisk - aRisk
  })

  return result
})

// 更新图表
const updateCharts = () => {
  // 预警分布饼图
  if (pieChartRef.value) {
    if (pieChart) pieChart.dispose()
    pieChart = echarts.init(pieChartRef.value)

    const normalCount = stats.value.normalStudents || 0
    const warningCount = stats.value.warningStudents || 0
    const lowCount = stats.value.lowStudents || 0
    const criticalCount = stats.value.criticalStudents || 0

    pieChart.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: {c}人 ({d}%)' },
      legend: { bottom: '5%', left: 'center' },
      series: [{
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
        label: { show: false },
        emphasis: { label: { show: true, fontSize: 14, fontWeight: 'bold' } },
        data: [
          { value: criticalCount, name: '高危', itemStyle: { color: '#ef4444' } },
          { value: warningCount, name: '中等', itemStyle: { color: '#f59e0b' } },
          { value: lowCount, name: '低危', itemStyle: { color: '#3b82f6' } },
          { value: normalCount, name: '正常', itemStyle: { color: '#10b981' } }
        ].filter(d => d.value > 0)
      }]
    })
  }

  // 班级学生对比柱状图
  if (barChartRef.value && classOptions.value.length > 0) {
    if (barChart) barChart.dispose()
    barChart = echarts.init(barChartRef.value)

    const classNames = classOptions.value.map(c => c.name)
    const studentCounts = classOptions.value.map(c => c.student_count || 0)

    barChart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: { type: 'category', data: classNames, axisLabel: { rotate: 15 } },
      yAxis: { type: 'value', name: '学生数' },
      series: [{
        name: '学生数',
        type: 'bar',
        data: studentCounts,
        itemStyle: { color: '#3b82f6', borderRadius: [4, 4, 0, 0] }
      }]
    })
  }
}

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const params = {}
    if (selectedClass.value) {
      params.class_id = selectedClass.value
    }

    const [studentsRes, statsRes] = await Promise.all([
      getCourseStudents(courseId.value, params),
      getCourseStats(courseId.value)
    ])

    if (studentsRes.code === 200) {
      const data = studentsRes.data
      courseName.value = data.course.name
      students.value = data.students || []
      classOptions.value = data.classes || []

      // 计算统计
      const total = students.value.length
      const critical = students.value.filter(s => s.warning_level === 'high').length
      const warning = students.value.filter(s => s.warning_level === 'medium').length
      const low = students.value.filter(s => s.warning_level === 'low').length
      const normal = total - critical - warning - low

      stats.value = {
        totalStudents: total,
        normalStudents: normal,
        warningStudents: warning,
        lowStudents: low,
        criticalStudents: critical
      }
    }

    if (statsRes.code === 200) {
      courseSuggestion.value = statsRes.data?.course_suggestion || ''
    }

    // 更新图表
    await nextTick()
    updateCharts()
  } catch (error) {
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
    'low': 'primary',
    null: 'success'
  }
  return types[level] || 'success'
}

// 预警标签映射
const getWarningLabel = (level) => {
  const labels = {
    'high': '高危',
    'medium': '中等',
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
  window.addEventListener('resize', () => {
    pieChart?.resize()
    barChart?.resize()
  })
})
</script>

<style scoped>
.course-students-page {
  max-width: 1400px;
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
  margin: 0 0 4px 0;
}

.header-left p {
  color: #6b7280;
  font-size: 14px;
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
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
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
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
}

.stat-label {
  font-size: 14px;
  color: #6b7280;
  margin-top: 4px;
}

.stat-change {
  font-size: 12px;
  margin-top: 4px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.stat-change.danger { color: #ef4444; }
.stat-change.warning { color: #f59e0b; }
.stat-change.success { color: #10b981; }

.charts-row {
  margin-bottom: 24px;
}

.chart-card {
  border-radius: 12px;
}

.chart-container {
  height: 300px;
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

.suggestion-card {
  margin-bottom: 20px;
  border-radius: 12px;
  background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
  border: 1px solid #7dd3fc;
}

.suggestion-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #0369a1;
  margin-bottom: 12px;
}

.suggestion-text {
  margin: 0;
  color: #1e40af;
  font-size: 14px;
  line-height: 1.6;
}
</style>
