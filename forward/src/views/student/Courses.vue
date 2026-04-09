<template>
  <div class="courses-page">
    <div class="page-header">
      <h2>我的课程</h2>
      <p>查看已选课程及学习资源</p>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon" style="background: #3b82f6">
          <el-icon><Reading /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ totalCourses }}</div>
          <div class="stat-title">总课程数</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: #10b981">
          <el-icon><VideoCamera /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ totalVideos }}</div>
          <div class="stat-title">视频资源</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: #f59e0b">
          <el-icon><Document /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ totalDocs }}</div>
          <div class="stat-title">文档资料</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: #8b5cf6">
          <el-icon><Edit /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ totalExercises }}</div>
          <div class="stat-title">习题资源</div>
        </div>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <div class="search-card">
      <div class="search-bar">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索课程名称..."
          :prefix-icon="Search"
          size="large"
          clearable
          style="flex: 1"
        />
        <el-select v-model="selectedSemester" placeholder="选择学期" clearable style="width: 150px">
          <el-option label="2024-2025学年" value="2024-2025" />
          <el-option label="2023-2024学年" value="2023-2024" />
        </el-select>
        <el-button type="primary" size="large" :icon="Search" @click="handleSearch" :loading="loading">
          搜索
        </el-button>
      </div>
    </div>

    <!-- 课程列表 -->
    <div class="courses-grid" v-loading="loading">
      <div
        v-for="course in filteredCourses"
        :key="course.id"
        class="course-card"
        @click="goToCourseResources(course)"
      >
        <div class="course-cover" :style="{ background: getCourseGradient(course.id) }">
          <el-icon :size="48"><component :is="getCourseIcon(course.id)" /></el-icon>
        </div>
        <div class="course-info">
          <h3 class="course-name">{{ course.name }}</h3>
          <p class="course-code">{{ course.course_no }}</p>
          <div class="course-stats">
            <span><el-icon><VideoCamera /></el-icon> {{ course.videoCount || 0 }}视频</span>
            <span><el-icon><Document /></el-icon> {{ course.docCount || 0 }}文档</span>
            <span><el-icon><Edit /></el-icon> {{ course.exerciseCount || 0 }}习题</span>
          </div>
          <div class="course-teacher">
            <el-icon><User /></el-icon>
            <span>{{ course.teacher_name || '暂无教师' }}</span>
          </div>
        </div>
        <div class="course-action">
          <el-button type="primary" round size="small">
            进入学习
            <el-icon><Right /></el-icon>
          </el-button>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="!loading && filteredCourses.length === 0" class="empty-state">
      <el-icon :size="80"><FolderOpened /></el-icon>
      <p>暂无相关课程</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Search, Reading, VideoCamera, Document, Edit, User, Right, FolderOpened } from '@element-plus/icons-vue'
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
    list = list.filter(c =>
      c.name?.includes(searchKeyword.value) ||
      c.course_no?.includes(searchKeyword.value)
    )
  }
  if (selectedSemester.value) {
    list = list.filter(c => c.semester?.includes(selectedSemester.value))
  }
  return list
})

const iconMap = ['Monitor', 'DataAnalysis', 'Cpu', 'Connection', 'Document', 'SetUp', 'Grid']
const gradientMap = [
  'linear-gradient(135deg, #3b82f6, #1e3a8a)',
  'linear-gradient(135deg, #10b981, #059669)',
  'linear-gradient(135deg, #f59e0b, #d97706)',
  'linear-gradient(135deg, #8b5cf6, #7c3aed)',
  'linear-gradient(135deg, #ec489a, #db2777)',
  'linear-gradient(135deg, #06b6d4, #0891b2)',
  'linear-gradient(135deg, #f97316, #ea580c)'
]

const getCourseIcon = (id) => iconMap[(id - 1) % iconMap.length]
const getCourseGradient = (id) => gradientMap[(id - 1) % gradientMap.length]

const loadCourses = async () => {
  loading.value = true
  try {
    const res = await getStudentCourses()
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
  padding: 20px;
}
.page-header {
  margin-bottom: 24px;
}
.page-header h2 {
  font-size: 24px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 8px;
}
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}
.stat-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}
.stat-icon {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}
.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
}
.search-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 24px;
}
.search-bar {
  display: flex;
  gap: 16px;
  align-items: center;
}
.courses-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}
.course-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  cursor: pointer;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
}
.course-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px -8px rgba(0, 0, 0, 0.15);
}
.course-cover {
  height: 140px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}
.course-info {
  padding: 20px;
}
.course-name {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 4px;
}
.course-stats {
  display: flex;
  gap: 16px;
  margin: 12px 0;
  font-size: 12px;
  color: #64748b;
}
.course-action {
  padding: 0 20px 20px;
}
.empty-state {
  text-align: center;
  padding: 60px;
  color: #94a3b8;
}
</style>
