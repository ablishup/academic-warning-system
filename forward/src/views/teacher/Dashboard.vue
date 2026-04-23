<template>
  <div class="teacher-dashboard">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>课程概览</h1>
      <p>管理您的课程和学生学习情况</p>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="8">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon-bg blue">
            <el-icon><Reading /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalCourses }}</div>
            <div class="stat-label">教授课程</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon-bg green">
            <el-icon><User /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalStudents }}</div>
            <div class="stat-label">学生总数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon-bg red">
            <el-icon><Warning /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalWarnings }}</div>
            <div class="stat-label">预警学生</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 课程列表 -->
    <el-card class="courses-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="card-title">
            <el-icon><Collection /></el-icon>
            我的课程
          </span>
          <el-button type="primary" @click="refreshData" :loading="loading">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>

      <el-table :data="courses" v-loading="loading" style="width: 100%">
        <el-table-column prop="name" label="课程名称" min-width="200">
          <template #default="{ row }">
            <div class="course-name-cell">
              <div class="course-icon" :style="{ background: getCourseColor(row.id) }">
                <el-icon><Monitor /></el-icon>
              </div>
              <div>
                <div class="name">{{ row.name }}</div>
                <div class="code">{{ row.course_no }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="semester" label="学期" width="150" />
        <el-table-column prop="studentCount" label="学生数" width="100" align="center">
          <template #default="{ row }">
            <el-tag>{{ row.studentCount }} 人</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="avgScore" label="平均成绩" width="120" align="center">
          <template #default="{ row }">
            <el-progress
              :percentage="Math.round(row.avgScore)"
              :status="row.avgScore >= 60 ? 'success' : 'exception'"
              :stroke-width="8"
            />
          </template>
        </el-table-column>
        <el-table-column prop="warningCount" label="预警" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.warningCount > 0" type="danger">{{ row.warningCount }}</el-tag>
            <span v-else class="text-gray">-</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="viewStudents(row)">
              <el-icon><View /></el-icon>
              查看学生
            </el-button>
            <el-button type="primary" link @click="uploadData(row)">
              <el-icon><Upload /></el-icon>
              上传数据
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && courses.length === 0" description="暂无课程数据" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  Reading, User, Warning, Collection, Refresh,
  Monitor, View, Upload
} from '@element-plus/icons-vue'
import { getTeacherDashboard } from '@/api/teacher'
import { ElMessage } from 'element-plus'

const router = useRouter()
const loading = ref(false)
const courses = ref([])
const stats = ref({
  totalCourses: 0,
  totalStudents: 0,
  totalWarnings: 0
})

const courseColors = [
  '#667eea', '#f093fb', '#4facfe', '#43e97b', '#fa709a', '#30cfd0'
]

const getCourseColor = (id) => courseColors[(id - 1) % courseColors.length]

const loadData = async () => {
  loading.value = true
  try {
    const res = await getTeacherDashboard()
    if (res.code === 200) {
      courses.value = res.data.courses
      stats.value = {
        totalCourses: res.data.totalCourses,
        totalStudents: res.data.totalStudents,
        totalWarnings: res.data.totalWarnings
      }
    }
  } catch (error) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const refreshData = () => {
  loadData()
}

const viewStudents = (course) => {
  router.push(`/teacher/courses/${course.id}/students`)
}

const uploadData = (course) => {
  router.push({
    path: '/teacher/upload',
    query: { course_id: course.id }
  })
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.teacher-dashboard {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 8px;
}

.page-header p {
  color: #6b7280;
}

/* 统计卡片 */
.stats-row {
  margin-bottom: 24px;
}

.stat-card :deep(.el-card__body) {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 24px;
}

.stat-icon-bg {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.stat-icon-bg.blue {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon-bg.green {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-icon-bg.red {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.stat-icon-bg .el-icon {
  font-size: 32px;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #1f2937;
}

.stat-label {
  font-size: 14px;
  color: #6b7280;
  margin-top: 4px;
}

/* 课程卡片 */
.courses-card {
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

.course-name-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.course-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
}

.course-name-cell .name {
  font-weight: 600;
  color: #1f2937;
}

.course-name-cell .code {
  font-size: 12px;
  color: #9ca3af;
  margin-top: 2px;
}

.text-gray {
  color: #9ca3af;
}
</style>
