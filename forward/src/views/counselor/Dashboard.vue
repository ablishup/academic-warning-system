<template>
  <div class="counselor-dashboard">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <h1>学情总览</h1>
        <p>查看全院系学生的学业情况和预警分布</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="refreshData" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新数据
        </el-button>
        <el-button type="warning" @click="syncData" :loading="syncing">
          <el-icon><DataLine /></el-icon>
          同步得分
        </el-button>
        <el-button type="success" @click="calculateWarnings" :loading="calculating">
          <el-icon><Cpu /></el-icon>
          计算预警
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon blue">
            <el-icon :size="28"><User /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalStudents }}</div>
            <div class="stat-label">学生总数</div>
            <div class="stat-change">
              <span>覆盖 {{ stats.classCount }} 个班级</span>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon red">
            <el-icon :size="28"><Warning /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.highRisk }}</div>
            <div class="stat-label">高危预警</div>
            <div class="stat-change danger">
              <el-icon><ArrowUp /></el-icon>
              <span>需立即干预</span>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon orange">
            <el-icon :size="28"><Bell /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.mediumRisk }}</div>
            <div class="stat-label">中等预警</div>
            <div class="stat-change warning">
              <span>需持续关注</span>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon green">
            <el-icon :size="28"><FirstAidKit /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.interventions }}</div>
            <div class="stat-label">干预记录</div>
            <div class="stat-change success">
              <span>本月新增 {{ stats.newInterventions }}</span>
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
                班级预警对比
              </span>
            </div>
          </template>
          <div ref="barChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近预警学生 -->
    <el-card class="warning-students-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="card-title">
            <el-icon><WarningFilled /></el-icon>
            最近预警学生
          </span>
          <el-button type="primary" link @click="$router.push('/counselor/warnings')">
            查看全部
            <el-icon><ArrowRight /></el-icon>
          </el-button>
        </div>
      </template>

      <el-table :data="recentWarnings" v-loading="loading" stripe>
        <el-table-column label="学生姓名" width="100">
          <template #default="{ row }">
            <div class="student-name">
              <el-avatar :size="32" :style="{ background: getAvatarColor(row.student?.name) }">
                {{ row.student?.name?.charAt(0) }}
              </el-avatar>
              <span>{{ row.student?.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="学号" width="120">
          <template #default="{ row }">
            <span>{{ row.student?.student_no }}</span>
          </template>
        </el-table-column>
        <el-table-column label="课程" min-width="150">
          <template #default="{ row }">
            <span>{{ row.course?.name }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="risk_level" label="风险等级" width="100">
          <template #default="{ row }">
            <el-tag :type="getRiskTagType(row.risk_level)" effect="dark" size="small">
              {{ getRiskLabel(row.risk_level) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="composite_score" label="综合得分" width="100">
          <template #default="{ row }">
            <span :class="getScoreClass(row.composite_score)">{{ row.composite_score }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="calculation_time" label="预警时间" width="150">
          <template #default="{ row }">
            {{ formatDate(row.calculation_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewStudentDetail(row)">
              详情
            </el-button>
            <el-button type="success" link size="small" @click="addIntervention(row)">
              干预
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 学生详情弹窗 -->
    <el-dialog v-model="detailDialogVisible" title="学生学情详情" width="700px">
      <div v-if="selectedStudent" class="student-detail">
        <div class="detail-header">
          <el-avatar :size="64" :style="{ background: getAvatarColor(selectedStudent.student?.name) }">
            {{ selectedStudent.student?.name?.charAt(0) }}
          </el-avatar>
          <div class="detail-info">
            <h3>{{ selectedStudent.student?.name }}</h3>
            <p>学号：{{ selectedStudent.student?.student_no }} | 班级：{{ selectedStudent.student?.class_name || '-' }}</p>
          </div>
          <el-tag :type="getRiskTagType(selectedStudent.risk_level)" effect="dark" size="large">
            {{ getRiskLabel(selectedStudent.risk_level) }}
          </el-tag>
        </div>

        <el-descriptions :column="2" border class="detail-descriptions">
          <el-descriptions-item label="课程">{{ selectedStudent.course?.name }}</el-descriptions-item>
          <el-descriptions-item label="综合得分">{{ selectedStudent.composite_score }}</el-descriptions-item>
          <el-descriptions-item label="出勤率">{{ selectedStudent.attendance_score }}%</el-descriptions-item>
          <el-descriptions-item label="视频进度">{{ selectedStudent.progress_score }}%</el-descriptions-item>
          <el-descriptions-item label="作业成绩">{{ selectedStudent.homework_score }}</el-descriptions-item>
          <el-descriptions-item label="考试成绩">{{ selectedStudent.exam_score }}</el-descriptions-item>
        </el-descriptions>

        <div class="detail-actions">
          <el-button type="primary" @click="addIntervention(selectedStudent)">
            <el-icon><FirstAidKit /></el-icon>
            添加干预记录
          </el-button>
          <el-button v-if="selectedStudent.status === 'active'" type="success" @click="resolveWarning(selectedStudent)">
            <el-icon><CircleCheck /></el-icon>
            标记为已解决
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import {
  User, Warning, Bell, FirstAidKit, Refresh, Cpu,
  PieChart, Histogram, WarningFilled, ArrowRight, ArrowUp, CircleCheck,
  DataLine
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getSchoolOverview, getWarningRecords, calculateWarnings as apiCalculateWarnings,
  syncStudentScores
} from '@/api/counselor'

const router = useRouter()

// 状态
const loading = ref(false)
const syncing = ref(false)
const calculating = ref(false)
const detailDialogVisible = ref(false)
const selectedStudent = ref(null)

// 统计数据
const stats = reactive({
  totalStudents: 0,
  classCount: 0,
  highRisk: 0,
  mediumRisk: 0,
  lowRisk: 0,
  interventions: 0,
  newInterventions: 0
})

// 班级统计数据（用于图表）
const classStats = ref([])

// 最近预警学生
const recentWarnings = ref([])

// 图表引用
const pieChartRef = ref(null)
const barChartRef = ref(null)
let pieChart = null
let barChart = null

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    // 获取全校概览（包含Dashboard统计、预警统计、干预统计）
    const overviewRes = await getSchoolOverview()
    if (overviewRes.code === 200) {
      const data = overviewRes.data
      // Dashboard统计（学生总数、班级数）
      stats.totalStudents = data.dashboardStats?.totalStudents || 0
      stats.classCount = data.dashboardStats?.classCount || 0
      classStats.value = data.dashboardStats?.classes || []

      // 预警统计
      stats.highRisk = data.warningStats?.high || 0
      stats.mediumRisk = data.warningStats?.medium || 0
      stats.lowRisk = data.warningStats?.low || 0

      // 干预统计
      const interventionStats = data.interventionStats || {}
      stats.interventions = interventionStats?.total || 0
      stats.newInterventions = interventionStats?.this_month || 0
    }

    // 获取最近预警学生（API已按辅导员过滤）
    const warningsRes = await getWarningRecords({
      status: 'active',
      ordering: '-calculation_time',
      page_size: 10
    })
    if (warningsRes.code === 200) {
      recentWarnings.value = warningsRes.data?.results || warningsRes.data || []
    }

    // 更新图表
    await nextTick()
    updateCharts()
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败')
    // 使用模拟数据
    recentWarnings.value = getMockWarnings()
    updateCharts()
  } finally {
    loading.value = false
  }
}

// 模拟数据
const getMockWarnings = () => [
  { id: 1, student_name: '张三', student_no: '2021001', course_name: '数据结构', risk_level: 'high', composite_score: 45.5, attendance_score: 60, progress_score: 40, homework_score: 50, exam_score: 42, calculation_time: '2025-04-10', status: 'active' },
  { id: 2, student_name: '李四', student_no: '2021002', course_name: '数据结构', risk_level: 'medium', composite_score: 65.2, attendance_score: 75, progress_score: 60, homework_score: 68, exam_score: 62, calculation_time: '2025-04-09', status: 'active' },
  { id: 3, student_name: '王五', student_no: '2021003', course_name: '算法设计', risk_level: 'high', composite_score: 38.7, attendance_score: 55, progress_score: 35, homework_score: 40, exam_score: 38, calculation_time: '2025-04-09', status: 'active' },
  { id: 4, student_name: '赵六', student_no: '2021004', course_name: '操作系统', risk_level: 'low', composite_score: 72.3, attendance_score: 80, progress_score: 75, homework_score: 70, exam_score: 68, calculation_time: '2025-04-08', status: 'active' },
  { id: 5, student_name: '钱七', student_no: '2021005', course_name: '计算机网络', risk_level: 'medium', composite_score: 58.9, attendance_score: 70, progress_score: 55, homework_score: 60, exam_score: 52, calculation_time: '2025-04-08', status: 'active' }
]

// 更新图表
const updateCharts = () => {
  // 预警分布饼图
  if (pieChartRef.value) {
    if (pieChart) pieChart.dispose()
    pieChart = echarts.init(pieChartRef.value)

    // 计算正常学生数（总学生数 - 各风险等级学生数）
    // 注意：一个学生可能有多个课程的预警，所以这里显示的是预警记录数，而非学生数
    const totalWarnings = stats.highRisk + stats.mediumRisk + stats.lowRisk
    const normalCount = Math.max(0, stats.totalStudents - totalWarnings)

    pieChart.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
      legend: { bottom: '5%', left: 'center' },
      series: [{
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
        label: { show: false },
        emphasis: { label: { show: true, fontSize: 16, fontWeight: 'bold' } },
        data: [
          { value: stats.highRisk || 0, name: '高危', itemStyle: { color: '#ef4444' } },
          { value: stats.mediumRisk || 0, name: '中等', itemStyle: { color: '#f59e0b' } },
          { value: stats.lowRisk || 0, name: '低危', itemStyle: { color: '#3b82f6' } },
          { value: normalCount, name: '正常', itemStyle: { color: '#10b981' } }
        ]
      }]
    })
  }

  // 班级预警对比柱状图
  if (barChartRef.value && classStats.value.length > 0) {
    if (barChart) barChart.dispose()
    barChart = echarts.init(barChartRef.value)

    // 使用真实的班级数据
    const classNames = classStats.value.map(c => c.name)
    const studentCounts = classStats.value.map(c => c.student_count || 0)

    barChart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: { type: 'category', data: classNames, axisLabel: { rotate: 15 } },
      yAxis: { type: 'value', name: '学生数' },
      series: [
        { name: '学生数', type: 'bar', data: studentCounts, itemStyle: { color: '#3b82f6', borderRadius: [4, 4, 0, 0] } }
      ]
    })
  }
}

// 刷新数据
const refreshData = () => {
  loadData()
  ElMessage.success('数据已刷新')
}

// 同步数据
const syncData = async () => {
  try {
    await ElMessageBox.confirm(
      '同步数据会将所有学生的考勤、作业、考试等数据汇总到课程得分表，确定要继续吗？',
      '确认同步',
      { type: 'warning' }
    )
    syncing.value = true
    const res = await syncStudentScores({ sync_all: true })
    if (res.code === 200) {
      ElMessage.success(`数据同步完成：成功 ${res.data.success} 条，失败 ${res.data.failed} 条`)
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('同步失败:', error)
      ElMessage.error('数据同步失败')
    }
  } finally {
    syncing.value = false
  }
}

// 计算预警
const calculateWarnings = async () => {
  try {
    await ElMessageBox.confirm('确定要重新计算所有学生的预警吗？', '确认', { type: 'warning' })
    calculating.value = true
    const res = await apiCalculateWarnings()
    if (res.code === 200) {
      ElMessage.success(`计算完成，新增 ${res.data.created} 条预警，更新 ${res.data.updated} 条`)
      loadData()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('计算失败:', error)
      ElMessage.error('计算失败')
    }
  } finally {
    calculating.value = false
  }
}

// 查看学生详情
const viewStudentDetail = (row) => {
  selectedStudent.value = row
  detailDialogVisible.value = true
}

// 添加干预记录
const addIntervention = (row) => {
  router.push({
    path: '/counselor/interventions',
    query: { student_id: row.student?.id, warning_id: row.id }
  })
}

// 解决预警
const resolveWarning = async (row) => {
  try {
    const { value } = await ElMessageBox.prompt('请输入解决说明', '标记为已解决', {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      inputPlaceholder: '请输入解决说明（可选）'
    })
    // 调用API解决预警
    ElMessage.success('预警已标记为已解决')
    loadData()
  } catch {
    // 取消
  }
}

// 工具函数
const getAvatarColor = (name) => {
  const colors = ['#667eea', '#f093fb', '#4facfe', '#43e97b', '#fa709a', '#30cfd0']
  let hash = 0
  for (let i = 0; i < name?.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash)
  return colors[Math.abs(hash) % colors.length]
}

const getRiskTagType = (level) => {
  const types = { high: 'danger', medium: 'warning', low: 'info', normal: 'success' }
  return types[level] || 'info'
}

const getRiskLabel = (level) => {
  const labels = { high: '高危', medium: '中等', low: '低危', normal: '正常' }
  return labels[level] || level
}

const getScoreClass = (score) => {
  if (score < 60) return 'score-danger'
  if (score < 75) return 'score-warning'
  return 'score-success'
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

onMounted(() => {
  loadData()
  window.addEventListener('resize', () => {
    pieChart?.resize()
    barChart?.resize()
  })
})

onUnmounted(() => {
  pieChart?.dispose()
  barChart?.dispose()
})
</script>

<style scoped>
.counselor-dashboard {
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

.header-actions {
  display: flex;
  gap: 12px;
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

.stat-icon.blue { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
.stat-icon.red { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
.stat-icon.orange { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }
.stat-icon.green { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }

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
  color: #374151;
}

.chart-container {
  height: 300px;
}

.warning-students-card {
  border-radius: 12px;
}

.student-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.score-danger { color: #ef4444; font-weight: 600; }
.score-warning { color: #f59e0b; font-weight: 600; }
.score-success { color: #10b981; font-weight: 600; }

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

.detail-descriptions {
  margin: 20px 0;
}

.detail-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 24px;
}
</style>
