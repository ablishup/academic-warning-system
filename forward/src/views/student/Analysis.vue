<template>
  <div class="student-analysis">
    <div class="page-header">
      <h2>学情分析</h2>
      <p>查看个人学习情况和预警信息</p>
    </div>

    <!-- 预警信息卡片 -->
    <el-card v-if="currentWarning" class="warning-card" :class="currentWarning.risk_level">
      <div class="warning-content">
        <el-icon :size="28"><WarningFilled /></el-icon>
        <div>
          <h3>{{ getRiskTitle(currentWarning.risk_level) }}</h3>
          <p>综合得分: {{ currentWarning.composite_score }}分</p>
          <p v-if="currentWarning.suggestion">{{ currentWarning.suggestion }}</p>
        </div>
      </div>
    </el-card>

    <!-- 学习统计 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card>
          <div class="stat-item">
            <div class="stat-label">学习时长</div>
            <div class="stat-value">{{ learningStats.total_duration || 0 }}小时</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="stat-item">
            <div class="stat-label">作业平均分</div>
            <div class="stat-value">{{ homeworkStats.avg_score || 0 }}分</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="stat-item">
            <div class="stat-label">考试平均分</div>
            <div class="stat-value">{{ examStats.avg_score || 0 }}分</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="stat-item">
            <div class="stat-label">平均进度</div>
            <div class="stat-value">{{ Math.round(learningStats.avg_progress || 0) }}%</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 成绩趋势图 -->
    <el-card class="chart-card">
      <template #header>
        <span>成绩趋势</span>
      </template>
      <div ref="chartRef" style="height: 300px;"></div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import { WarningFilled } from '@element-plus/icons-vue'
import { getStudentAnalysisSummary, getHomeworkSubmissions, getExamResults } from '@/api/student'

const currentWarning = ref(null)
const learningStats = ref({})
const homeworkStats = ref({})
const examStats = ref({})
const chartRef = ref(null)
let chart = null

const getRiskTitle = (level) => {
  const titles = { high: '高风险', medium: '中等风险', low: '低风险', normal: '正常' }
  return titles[level] || '未知'
}

const loadData = async () => {
  try {
    const res = await getStudentAnalysisSummary()
    if (res.code === 200) {
      const data = res.data
      warnings.value = data.warnings || []
      currentWarning.value = warnings.value[0] || null
      learningStats.value = data.learning || {}
      homeworkStats.value = data.homework || {}
      examStats.value = data.exam || {}
    }
    await loadChartData()
  } catch (error) {
    console.error('加载数据失败:', error)
  }
}

const warnings = ref([])

const loadChartData = async () => {
  try {
    const [hwRes, examRes] = await Promise.all([
      getHomeworkSubmissions(),
      getExamResults()
    ])
    const hwScores = hwRes.data?.results?.map(h => ({ name: h.assignment_title, value: h.score })) || []
    const examScores = examRes.data?.results?.map(e => ({ name: e.exam_title, value: e.score })) || []
    const allScores = [...hwScores, ...examScores].slice(-10)

    if (chart) chart.dispose()
    chart = echarts.init(chartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: allScores.map(s => s.name) },
      yAxis: { type: 'value', min: 0, max: 100 },
      series: [{
        data: allScores.map(s => s.value),
        type: 'line',
        smooth: true
      }]
    })
  } catch (error) {
    console.error('加载图表数据失败:', error)
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.student-analysis {
  padding: 20px;
}
.page-header {
  margin-bottom: 24px;
}
.warning-card {
  margin-bottom: 20px;
}
.warning-card.high {
  background: #fee2e2;
}
.warning-card.medium {
  background: #fef3c7;
}
.warning-card.low {
  background: #d1fae5;
}
.warning-content {
  display: flex;
  align-items: center;
  gap: 16px;
}
.stats-row {
  margin-bottom: 20px;
}
.stat-item {
  text-align: center;
}
.stat-label {
  color: #64748b;
  font-size: 14px;
  margin-bottom: 8px;
}
.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #1e293b;
}
.chart-card {
  margin-top: 20px;
}
</style>
