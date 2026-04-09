<template>
  <div class="student-analysis">
    <!-- 欢迎横幅 -->
    <div class="welcome-banner" v-if="studentInfo">
      <div class="welcome-content">
        <div class="welcome-text">
          <h2>欢迎回来，{{ studentInfo.name || '同学' }}</h2>
          <p>查看你的学习进展和预警状态</p>
        </div>
        <div class="quick-stats">
          <div class="quick-stat">
            <div class="stat-num">{{ learningStats.activity_count || 0 }}</div>
            <div class="stat-label">学习活动</div>
          </div>
          <div class="quick-stat">
            <div class="stat-num">{{ Math.round(learningStats.avg_progress || 0) }}%</div>
            <div class="stat-label">平均进度</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 预警卡片 -->
    <el-card v-if="currentWarning" class="warning-card" :class="currentWarning.risk_level">
      <div class="warning-header">
        <div class="warning-icon-wrapper">
          <el-icon :size="32"><WarningFilled /></el-icon>
        </div>
        <div class="warning-info">
          <h3>{{ getRiskTitle(currentWarning.risk_level) }}</h3>
          <p class="warning-desc">综合得分: <strong>{{ currentWarning.composite_score }}</strong> 分</p>
        </div>
        <el-tag :type="getRiskTagType(currentWarning.risk_level)" size="large" effect="dark">
          {{ getRiskLevelText(currentWarning.risk_level) }}
        </el-tag>
      </div>
      <el-divider />
      <div class="suggestion-section" v-if="currentWarning.suggestion">
        <h4><el-icon><LightBulb /></el-icon> 学习建议</h4>
        <p class="suggestion-text">{{ currentWarning.suggestion }}</p>
      </div>
    </el-card>

    <!-- 学习概览统计 -->
    <el-row :gutter="20" class="overview-row">
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon-bg" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%)">
            <el-icon><Clock /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ formatDuration(learningStats.total_duration) }}</div>
            <div class="stat-label">学习时长</div>
            <div class="stat-trend" v-if="learningStats.total_duration > 0">
              <el-icon><ArrowUp /></el-icon>
              <span>保持学习</span>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon-bg" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%)">
            <el-icon><DocumentChecked /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ homeworkStats.avg_score || 0 }}</div>
            <div class="stat-label">作业平均分</div>
            <div class="stat-trend" :class="getScoreTrend(homeworkStats.avg_score)">
              <el-icon><component :is="getTrendIcon(homeworkStats.avg_score)" /></el-icon>
              <span>{{ getScoreText(homeworkStats.avg_score) }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon-bg" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)">
            <el-icon><TrendCharts /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ examStats.avg_score || 0 }}</div>
            <div class="stat-label">考试平均分</div>
            <div class="stat-trend" :class="getScoreTrend(examStats.avg_score)">
              <el-icon><component :is="getTrendIcon(examStats.avg_score)" /></el-icon>
              <span>{{ getScoreText(examStats.avg_score) }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon-bg" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)">
            <el-icon><CircleCheck /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ Math.round(homeworkStats.completion_rate || 0) }}%</div>
            <div class="stat-label">作业完成率</div>
            <el-progress
              :percentage="Math.round(homeworkStats.completion_rate || 0)"
              :color="getProgressColor"
              :show-text="false"
              class="mini-progress"
            />
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
                <el-icon><TrendCharts /></el-icon>
                成绩趋势
              </span>
              <el-radio-group v-model="chartPeriod" size="small" @change="updateChart">
                <el-radio-button label="week">近7天</el-radio-button>
                <el-radio-button label="month">本月</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="scoreChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span class="card-title">
                <el-icon><PieChart /></el-icon>
                能力分析
              </span>
            </div>
          </template>
          <div ref="radarChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近活动 -->
    <el-card class="activity-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="card-title">
            <el-icon><Timer /></el-icon>
            最近学习活动
          </span>
          <el-button type="primary" link @click="loadData">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>
      <el-timeline v-if="recentActivities.length > 0">
        <el-timeline-item
          v-for="activity in recentActivities"
          :key="activity.id"
          :type="getActivityType(activity.activity_type)"
          :timestamp="formatTime(activity.created_at)"
        >
          <div class="activity-item">
            <span class="activity-name">{{ activity.activity_name }}</span>
            <el-tag size="small" :type="getActivityTagType(activity.activity_type)">
              {{ getActivityTypeText(activity.activity_type) }}
            </el-tag>
            <span class="activity-duration" v-if="activity.duration">
              {{ Math.round(activity.duration / 60) }}分钟
            </span>
          </div>
        </el-timeline-item>
      </el-timeline>
      <el-empty v-else description="暂无学习记录" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import {
  WarningFilled, LightBulb, Clock, DocumentChecked, TrendCharts,
  CircleCheck, ArrowUp, ArrowDown, PieChart, Timer, Refresh
} from '@element-plus/icons-vue'
import {
  getStudentAnalysisSummary, getLearningActivities, getHomeworkSubmissions, getExamResults
} from '@/api/student'

const studentInfo = ref({ name: '同学' })
const currentWarning = ref(null)
const learningStats = ref({})
const homeworkStats = ref({})
const examStats = ref({})
const recentActivities = ref([])
const chartPeriod = ref('week')

const scoreChartRef = ref(null)
const radarChartRef = ref(null)
let scoreChart = null
let radarChart = null

const getRiskTitle = (level) => {
  const titles = { high: '学业高风险预警', medium: '学业中等风险预警', low: '学业低风险提醒', normal: '学习状态正常' }
  return titles[level] || '未知状态'
}

const getRiskLevelText = (level) => {
  const texts = { high: '高风险', medium: '中等风险', low: '低风险', normal: '正常' }
  return texts[level] || '未知'
}

const getRiskTagType = (level) => {
  const types = { high: 'danger', medium: 'warning', low: 'info', normal: 'success' }
  return types[level] || 'info'
}

const getScoreTrend = (score) => {
  if (score >= 80) return 'trend-up'
  if (score >= 60) return 'trend-normal'
  return 'trend-down'
}

const getTrendIcon = (score) => {
  if (score >= 80) return 'ArrowUp'
  if (score >= 60) return 'Minus'
  return 'ArrowDown'
}

const getScoreText = (score) => {
  if (score >= 90) return '优秀'
  if (score >= 80) return '良好'
  if (score >= 60) return '及格'
  return '需努力'
}

const getProgressColor = (percentage) => {
  if (percentage < 30) return '#ef4444'
  if (percentage < 70) return '#f59e0b'
  return '#10b981'
}

const formatDuration = (seconds) => {
  if (!seconds) return '0小时'
  const hours = Math.floor(seconds / 3600)
  if (hours < 1) return Math.floor(seconds / 60) + '分钟'
  return hours + '小时'
}

const getActivityType = (type) => {
  const types = { video: 'primary', homework: 'success', exam: 'warning', sign_in: 'info' }
  return types[type] || 'info'
}

const getActivityTagType = (type) => {
  const types = { video: '', homework: 'success', exam: 'warning', sign_in: 'info' }
  return types[type] || ''
}

const getActivityTypeText = (type) => {
  const texts = { video: '视频学习', homework: '作业', exam: '考试', sign_in: '签到' }
  return texts[type] || type
}

const formatTime = (time) => {
  if (!time) return ''
  const date = new Date(time)
  return date.toLocaleString('zh-CN')
}

const loadData = async () => {
  try {
    const res = await getStudentAnalysisSummary()
    if (res.code === 200) {
      const data = res.data
      currentWarning.value = data.warnings?.[0] || null
      learningStats.value = data.learning || {}
      homeworkStats.value = data.homework || {}
      examStats.value = data.exam || {}
    }

    // 加载最近活动
    const activitiesRes = await getLearningActivities({ page_size: 5 })
    if (activitiesRes.code === 200) {
      recentActivities.value = activitiesRes.data?.results || []
    }

    updateCharts()
  } catch (error) {
    console.error('加载数据失败:', error)
  }
}

const updateCharts = async () => {
  try {
    const [hwRes, examRes] = await Promise.all([
      getHomeworkSubmissions(),
      getExamResults()
    ])

    const hwScores = hwRes.data?.results?.slice(-5) || []
    const examScores = examRes.data?.results?.slice(-5) || []

    // 成绩趋势图
    if (scoreChart) scoreChart.dispose()
    scoreChart = echarts.init(scoreChartRef.value)
    scoreChart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: {
        type: 'category',
        data: [...hwScores.map(h => h.assignment_title), ...examScores.map(e => e.exam_title)],
        axisLabel: { rotate: 30, fontSize: 10 }
      },
      yAxis: { type: 'value', min: 0, max: 100 },
      series: [{
        data: [...hwScores.map(h => h.score), ...examScores.map(e => e.score)],
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        lineStyle: { width: 3, color: '#667eea' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(102, 126, 234, 0.5)' },
            { offset: 1, color: 'rgba(102, 126, 234, 0.05)' }
          ])
        },
        itemStyle: { color: '#667eea' }
      }]
    })

    // 雷达图
    if (radarChart) radarChart.dispose()
    radarChart = echarts.init(radarChartRef.value)
    radarChart.setOption({
      tooltip: {},
      radar: {
        indicator: [
          { name: '视频进度', max: 100 },
          { name: '作业成绩', max: 100 },
          { name: '考试成绩', max: 100 },
          { name: '出勤率', max: 100 },
          { name: '学习时长', max: 100 }
        ],
        splitArea: {
          areaStyle: {
            color: ['rgba(102, 126, 234, 0.05)', 'rgba(102, 126, 234, 0.1)']
          }
        }
      },
      series: [{
        type: 'radar',
        data: [{
          value: [
            Math.round(learningStats.value.avg_progress || 0),
            Math.round(homeworkStats.value.avg_score || 0),
            Math.round(examStats.value.avg_score || 0),
            85, // 假设出勤率
            Math.min(100, Math.round((learningStats.value.total_duration || 0) / 3600))
          ],
          name: '能力分析',
          areaStyle: { color: 'rgba(102, 126, 234, 0.3)' },
          lineStyle: { color: '#667eea', width: 2 },
          itemStyle: { color: '#667eea' }
        }]
      }]
    })
  } catch (error) {
    console.error('加载图表失败:', error)
  }
}

onMounted(() => {
  loadData()
  window.addEventListener('resize', () => {
    scoreChart?.resize()
    radarChart?.resize()
  })
})

onUnmounted(() => {
  scoreChart?.dispose()
  radarChart?.dispose()
})
</script>

<style scoped>
.student-analysis {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

/* 欢迎横幅 */
.welcome-banner {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  padding: 32px;
  margin-bottom: 24px;
  color: white;
}

.welcome-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.welcome-text h2 {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 8px;
}

.welcome-text p {
  opacity: 0.9;
}

.quick-stats {
  display: flex;
  gap: 32px;
}

.quick-stat {
  text-align: center;
}

.stat-num {
  font-size: 32px;
  font-weight: 700;
}

.stat-label {
  font-size: 12px;
  opacity: 0.8;
  margin-top: 4px;
}

/* 预警卡片 */
.warning-card {
  margin-bottom: 24px;
  border-radius: 16px;
}

.warning-card.high {
  background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
  border: 1px solid #fca5a5;
}

.warning-card.medium {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  border: 1px solid #fcd34d;
}

.warning-card.low {
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  border: 1px solid #6ee7b7;
}

.warning-header {
  display: flex;
  align-items: center;
  gap: 16px;
}

.warning-icon-wrapper {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.5);
}

.warning-card.high .warning-icon-wrapper { color: #dc2626; }
.warning-card.medium .warning-icon-wrapper { color: #d97706; }
.warning-card.low .warning-icon-wrapper { color: #059669; }

.warning-info {
  flex: 1;
}

.warning-info h3 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 4px;
}

.warning-desc {
  color: #6b7280;
}

.suggestion-section h4 {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #374151;
  margin-bottom: 8px;
}

.suggestion-text {
  color: #6b7280;
  line-height: 1.6;
}

/* 统计概览 */
.overview-row {
  margin-bottom: 24px;
}

.stat-card {
  border-radius: 16px;
  overflow: hidden;
}

.stat-card :deep(.el-card__body) {
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon-bg {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.stat-icon-bg .el-icon {
  font-size: 28px;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
}

.stat-label {
  font-size: 13px;
  color: #6b7280;
  margin-top: 2px;
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  margin-top: 4px;
}

.stat-trend.trend-up {
  color: #10b981;
}

.stat-trend.trend-normal {
  color: #f59e0b;
}

.stat-trend.trend-down {
  color: #ef4444;
}

.mini-progress {
  margin-top: 8px;
}

/* 图表区域 */
.charts-row {
  margin-bottom: 24px;
}

.chart-card {
  border-radius: 16px;
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

/* 活动记录 */
.activity-card {
  border-radius: 16px;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.activity-name {
  font-weight: 500;
  color: #374151;
}

.activity-duration {
  font-size: 12px;
  color: #9ca3af;
  margin-left: auto;
}
</style>
