<template>
  <div class="courses-page">
    <!-- 页面标题区 -->
    <div class="page-header">
      <div class="header-content">
        <div>
          <h1 class="page-title">我的课程</h1>
          <p class="page-subtitle">共 {{ totalCourses }} 门课程，继续加油学习吧！</p>
        </div>
        <div class="header-stats">
          <div class="mini-stat">
            <el-icon class="stat-icon-blue"><VideoCamera /></el-icon>
            <span>{{ totalVideos }} 视频</span>
          </div>
          <div class="mini-stat">
            <el-icon class="stat-icon-green"><Document /></el-icon>
            <span>{{ totalDocs }} 文档</span>
          </div>
          <div class="mini-stat">
            <el-icon class="stat-icon-orange"><Edit /></el-icon>
            <span>{{ totalExercises }} 习题</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <el-card class="search-card" shadow="never">
      <div class="search-bar">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索课程名称或课程编号..."
          :prefix-icon="Search"
          size="large"
          clearable
          class="search-input"
        />
        <el-select
          v-model="selectedSemester"
          placeholder="选择学期"
          clearable
          size="large"
          class="semester-select"
        >
          <el-option label="2024-2025学年" value="2024-2025">
            <el-tag size="small" type="primary" style="margin-right: 8px">当前</el-tag>
            2024-2025学年
          </el-option>
          <el-option label="2023-2024学年" value="2023-2024" />
        </el-select>
        <el-button type="primary" size="large" :icon="Filter" @click="handleSearch" :loading="loading">
          筛选
        </el-button>
      </div>
    </el-card>

    <!-- 课程网格 -->
    <div class="courses-grid" v-loading="loading" element-loading-text="加载课程中...">
      <transition-group name="course-fade">
        <div
          v-for="course in filteredCourses"
          :key="course.id"
          class="course-card"
          @click="goToCourseResources(course)"
        >
          <div class="course-cover" :style="{ background: getCourseGradient(course.id) }">
            <div class="course-icon-wrapper">
              <el-icon :size="40"><component :is="getCourseIcon(course.id)" /></el-icon>
            </div>
            <div class="course-semester">{{ course.semester }}</div>
          </div>
          <div class="course-body">
            <div class="course-header">
              <h3 class="course-name">{{ course.name }}</h3>
              <el-tag size="small" type="info" effect="plain">{{ course.course_no }}</el-tag>
            </div>
            <p class="course-teacher">
              <el-icon><User /></el-icon>
              <span>{{ course.teacher_name || '暂无教师' }}</span>
            </p>
            <el-divider />
            <div class="course-footer">
              <div class="resource-stats">
                <div class="res-item" :class="{ 'has-data': course.videoCount }">
                  <el-icon><VideoPlay /></el-icon>
                  <span>{{ course.videoCount || 0 }}</span>
                </div>
                <div class="res-item" :class="{ 'has-data': course.docCount }">
                  <el-icon><Document /></el-icon>
                  <span>{{ course.docCount || 0 }}</span>
                </div>
                <div class="res-item" :class="{ 'has-data': course.exerciseCount }">
                  <el-icon><EditPen /></el-icon>
                  <span>{{ course.exerciseCount || 0 }}</span>
                </div>
              </div>
              <el-button type="primary" class="enter-btn" size="small">
                进入学习
                <el-icon class="btn-icon"><ArrowRight /></el-icon>
              </el-button>
            </div>
          </div>
        </div>
      </transition-group>
    </div>

    <!-- 空状态 -->
    <el-empty
      v-if="!loading && filteredCourses.length === 0"
      :image-size="200"
      description="暂无相关课程"
    >
      <template #description>
        <p class="empty-title">暂无相关课程</p>
        <p class="empty-desc">试试其他搜索条件吧</p>
      </template>
    </el-empty>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  Search, Filter, VideoCamera, Document, EditPen,
  User, ArrowRight, VideoPlay
} from '@element-plus/icons-vue'
import { getStudentCourses, getCourseResources } from '@/api/student'
import { ElMessage } from 'element-plus'

const router = useRouter()
const searchKeyword = ref('')
const selectedSemester = ref('')
const loading = ref(false)
const courses = ref([])

const totalCourses = computed(() => courses.value.length)
const totalVideos = computed(() => courses.value.reduce((sum, c) => sum + (c.videoCount || 0), 0))
const totalDocs = computed(() => courses.value.reduce((sum, c) => sum + (c.docCount || 0), 0))
const totalExercises = computed(() => courses.value.reduce((sum, c) => sum + (c.exerciseCount || 0), 0))

const filteredCourses = computed(() => {
  let list = [...courses.value]
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    list = list.filter(c =>
      c.name?.toLowerCase().includes(keyword) ||
      c.course_no?.toLowerCase().includes(keyword)
    )
  }
  if (selectedSemester.value) {
    list = list.filter(c => c.semester?.includes(selectedSemester.value))
  }
  return list
})

const iconMap = ['Monitor', 'DataAnalysis', 'Cpu', 'Connection', 'Document', 'SetUp', 'Grid']
const gradientMap = [
  'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
  'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
  'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
  'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
  'linear-gradient(135deg, #30cfd0 0%, #330867 100%)',
  'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)'
]

const getCourseIcon = (id) => iconMap[(id - 1) % iconMap.length]
const getCourseGradient = (id) => gradientMap[(id - 1) % gradientMap.length]

const loadCourses = async () => {
  loading.value = true
  try {
    const studentId = 1
    const res = await getStudentCourses(studentId)
    if (res.code === 200) {
      const coursesWithStats = await Promise.all(
        res.data.map(async (course) => {
          try {
            const resourcesRes = await getCourseResources({ course_id: course.id })
            const resources = resourcesRes.data?.results || []
            return {
              ...course,
              videoCount: resources.filter(r => r.resource_type === 'video').length,
              docCount: resources.filter(r => r.resource_type === 'document' || r.resource_type === 'ppt').length,
              exerciseCount: resources.filter(r => r.resource_type === 'exercise').length
            }
          } catch (error) {
            return { ...course, videoCount: 0, docCount: 0, exerciseCount: 0 }
          }
        })
      )
      courses.value = coursesWithStats
    }
  } catch (error) {
    ElMessage.error('加载课程列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {}

const goToCourseResources = (course) => {
  router.push({
    path: '/student/course-resources',
    query: { courseId: course.id, courseName: course.name }
  })
}

onMounted(() => {
  loadCourses()
})
</script>

<style scoped>
.courses-page {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

/* 页面头部 */
.page-header {
  margin-bottom: 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  padding: 32px;
  color: white;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 8px;
}

.page-subtitle {
  font-size: 14px;
  opacity: 0.9;
}

.header-stats {
  display: flex;
  gap: 24px;
}

.mini-stat {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255,255,255,0.2);
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 14px;
}

.stat-icon-blue { color: #60a5fa; }
.stat-icon-green { color: #34d399; }
.stat-icon-orange { color: #fbbf24; }

/* 搜索栏 */
.search-card {
  margin-bottom: 24px;
  border-radius: 12px;
}

.search-bar {
  display: flex;
  gap: 16px;
  align-items: center;
}

.search-input {
  flex: 1;
}

.semester-select {
  width: 200px;
}

/* 课程网格 */
.courses-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 24px;
}

/* 课程卡片 */
.course-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  border: 1px solid #e5e7eb;
}

.course-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.course-cover {
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  position: relative;
}

.course-icon-wrapper {
  background: rgba(255,255,255,0.2);
  border-radius: 50%;
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
}

.course-semester {
  position: absolute;
  top: 12px;
  right: 12px;
  background: rgba(255,255,255,0.2);
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  backdrop-filter: blur(10px);
}

.course-body {
  padding: 20px;
}

.course-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.course-name {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
  flex: 1;
}

.course-teacher {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #6b7280;
  font-size: 14px;
}

.el-divider {
  margin: 16px 0;
}

.course-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.resource-stats {
  display: flex;
  gap: 16px;
}

.res-item {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #9ca3af;
  font-size: 14px;
}

.res-item.has-data {
  color: #3b82f6;
  font-weight: 500;
}

.enter-btn {
  border-radius: 20px;
  padding: 8px 20px;
}

.btn-icon {
  margin-left: 4px;
  transition: transform 0.2s;
}

.course-card:hover .btn-icon {
  transform: translateX(4px);
}

/* 空状态 */
.empty-title {
  font-size: 18px;
  font-weight: 600;
  color: #374151;
  margin-top: 16px;
}

.empty-desc {
  font-size: 14px;
  color: #6b7280;
  margin-top: 8px;
}

/* 动画 */
.course-fade-enter-active,
.course-fade-leave-active {
  transition: all 0.5s ease;
}

.course-fade-enter-from,
.course-fade-leave-to {
  opacity: 0;
  transform: translateY(20px);
}
</style>
