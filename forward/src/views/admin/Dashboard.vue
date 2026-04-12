<template>
  <div class="admin-dashboard">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <h1>系统概览</h1>
        <p>管理系统运行状态和用户数据</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="refreshData" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新数据
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
            <div class="stat-value">{{ stats.totalUsers }}</div>
            <div class="stat-label">总用户数</div>
            <div class="stat-change">
              <span>学生 {{ stats.studentCount }} | 教师 {{ stats.teacherCount }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon green">
            <el-icon :size="28"><Reading /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalCourses }}</div>
            <div class="stat-label">课程总数</div>
            <div class="stat-change success">
              <span>本学期开设</span>
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
            <div class="stat-value">{{ stats.activeWarnings }}</div>
            <div class="stat-label">活跃预警</div>
            <div class="stat-change danger">
              <span>需关注处理</span>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon orange">
            <el-icon :size="28"><FirstAidKit /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.interventions }}</div>
            <div class="stat-label">干预记录</div>
            <div class="stat-change warning">
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
                <el-icon><Histogram /></el-icon>
                用户增长趋势
              </span>
            </div>
          </template>
          <div ref="userChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span class="card-title">
                <el-icon><PieChart /></el-icon>
                用户角色分布
              </span>
            </div>
          </template>
          <div ref="roleChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近用户和课程 -->
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card class="list-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span class="card-title">
                <el-icon><UserFilled /></el-icon>
                最近注册用户
              </span>
              <el-button type="primary" link @click="$router.push('/admin/users')">
                查看全部
                <el-icon><ArrowRight /></el-icon>
              </el-button>
            </div>
          </template>
          <el-table :data="recentUsers" v-loading="loading" stripe>
            <el-table-column prop="username" label="用户名" />
            <el-table-column prop="role" label="角色" width="100">
              <template #default="{ row }">
                <el-tag :type="getRoleTagType(row.role)" size="small">
                  {{ getRoleLabel(row.role) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="date_joined" label="注册时间" width="150">
              <template #default="{ row }">
                {{ formatDate(row.date_joined) }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="list-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span class="card-title">
                <el-icon><Reading /></el-icon>
                热门课程
              </span>
              <el-button type="primary" link @click="$router.push('/admin/courses')">
                查看全部
                <el-icon><ArrowRight /></el-icon>
              </el-button>
            </div>
          </template>
          <el-table :data="popularCourses" v-loading="loading" stripe>
            <el-table-column prop="name" label="课程名称" />
            <el-table-column prop="student_count" label="学生数" width="100" />
            <el-table-column prop="teacher_name" label="任课教师" width="120" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import {
  User, Reading, Warning, FirstAidKit, Refresh,
  Histogram, PieChart, UserFilled, ArrowRight
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const userChartRef = ref(null)
const roleChartRef = ref(null)
let userChart = null
let roleChart = null

// 统计数据
const stats = reactive({
  totalUsers: 520,
  studentCount: 450,
  teacherCount: 50,
  counselorCount: 15,
  adminCount: 5,
  totalCourses: 48,
  activeWarnings: 35,
  interventions: 128,
  newInterventions: 18
})

// 最近用户
const recentUsers = ref([])

// 热门课程
const popularCourses = ref([])

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    // 这里应该调用API获取数据
    // const res = await getAdminDashboard()
    // 使用模拟数据
    await new Promise(resolve => setTimeout(resolve, 500))

    recentUsers.value = [
      { id: 1, username: 'student001', role: 'student', date_joined: '2025-04-10' },
      { id: 2, username: 'teacher005', role: 'teacher', date_joined: '2025-04-09' },
      { id: 3, username: 'student002', role: 'student', date_joined: '2025-04-09' },
      { id: 4, username: 'student003', role: 'student', date_joined: '2025-04-08' },
      { id: 5, username: 'counselor003', role: 'counselor', date_joined: '2025-04-07' }
    ]

    popularCourses.value = [
      { id: 1, name: '数据结构', student_count: 156, teacher_name: '张教授' },
      { id: 2, name: '算法设计', student_count: 142, teacher_name: '李教授' },
      { id: 3, name: '操作系统', student_count: 138, teacher_name: '王教授' },
      { id: 4, name: '计算机网络', student_count: 125, teacher_name: '赵教授' },
      { id: 5, name: '数据库原理', student_count: 118, teacher_name: '钱教授' }
    ]

    await nextTick()
    updateCharts()
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 更新图表
const updateCharts = () => {
  // 用户增长趋势图
  if (userChartRef.value) {
    if (userChart) userChart.dispose()
    userChart = echarts.init(userChartRef.value)
    userChart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: {
        type: 'category',
        data: ['1月', '2月', '3月', '4月', '5月', '6月']
      },
      yAxis: { type: 'value' },
      series: [{
        data: [420, 432, 450, 480, 500, 520],
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
  }

  // 用户角色分布饼图
  if (roleChartRef.value) {
    if (roleChart) roleChart.dispose()
    roleChart = echarts.init(roleChartRef.value)
    roleChart.setOption({
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
          { value: 450, name: '学生', itemStyle: { color: '#667eea' } },
          { value: 50, name: '教师', itemStyle: { color: '#10b981' } },
          { value: 15, name: '辅导员', itemStyle: { color: '#f59e0b' } },
          { value: 5, name: '管理员', itemStyle: { color: '#ef4444' } }
        ]
      }]
    })
  }
}

// 刷新数据
const refreshData = () => {
  loadData()
  ElMessage.success('数据已刷新')
}

// 工具函数
const getRoleTagType = (role) => {
  const types = { student: '', teacher: 'success', counselor: 'warning', admin: 'danger' }
  return types[role] || ''
}

const getRoleLabel = (role) => {
  const labels = { student: '学生', teacher: '教师', counselor: '辅导员', admin: '管理员' }
  return labels[role] || role
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

onMounted(() => {
  loadData()
  window.addEventListener('resize', () => {
    userChart?.resize()
    roleChart?.resize()
  })
})

onUnmounted(() => {
  userChart?.dispose()
  roleChart?.dispose()
})
</script>

<style scoped>
.admin-dashboard {
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
.stat-icon.green { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }
.stat-icon.red { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
.stat-icon.orange { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }

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

.list-card {
  border-radius: 12px;
}
</style>
