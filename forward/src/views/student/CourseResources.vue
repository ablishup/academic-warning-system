<template>
  <div class="course-resources">
    <div class="course-header">
      <el-button :icon="ArrowLeft" @click="goBack">返回课程列表</el-button>
      <h2>{{ courseName }}</h2>
    </div>

    <el-tabs v-model="activeTab" v-loading="loading">
      <el-tab-pane label="视频" name="video">
        <div v-for="item in videoResources" :key="item.id" class="resource-item">
          <span>{{ item.name }}</span>
          <el-button type="primary" size="small" @click="watchVideo(item)">观看</el-button>
        </div>
        <el-empty v-if="videoResources.length === 0" description="暂无视频资源" />
      </el-tab-pane>
      <el-tab-pane label="文档" name="document">
        <div v-for="item in documentResources" :key="item.id" class="resource-item">
          <span>{{ item.name }}</span>
          <el-button type="primary" size="small" @click="downloadResource(item)">下载</el-button>
        </div>
        <el-empty v-if="documentResources.length === 0" description="暂无文档" />
      </el-tab-pane>
      <el-tab-pane label="习题" name="exercise">
        <div v-for="item in exerciseResources" :key="item.id" class="resource-item">
          <span>{{ item.name }}</span>
          <el-button type="primary" size="small" @click="downloadResource(item)">下载</el-button>
        </div>
        <el-empty v-if="exerciseResources.length === 0" description="暂无习题" />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft } from '@element-plus/icons-vue'
import { getCourseResources, downloadCourseResource, recordLearningActivity } from '@/api/student'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const courseId = ref(route.query.courseId)
const courseName = ref(route.query.courseName || '课程资源')
const activeTab = ref('video')
const loading = ref(false)
const resources = ref([])

const videoResources = computed(() => resources.value.filter(r => r.resource_type === 'video'))
const documentResources = computed(() => resources.value.filter(r => r.resource_type === 'document' || r.resource_type === 'ppt'))
const exerciseResources = computed(() => resources.value.filter(r => r.resource_type === 'exercise'))

const loadResources = async () => {
  if (!courseId.value) return
  loading.value = true
  try {
    const res = await getCourseResources({ course_id: courseId.value })
    if (res.code === 200) {
      resources.value = res.data?.results || []
    }
  } catch (error) {
    ElMessage.error('加载资源失败')
  } finally {
    loading.value = false
  }
}

const goBack = () => router.push('/student/courses')

const watchVideo = async (item) => {
  ElMessage.success(`开始播放: ${item.name}`)
  // 记录学习活动
  await recordLearningActivity({
    course_id: parseInt(courseId.value),
    activity_type: 'video',
    activity_name: item.name,
    duration: 0,
    progress: 0
  })
}

const downloadResource = async (item) => {
  try {
    const res = await downloadCourseResource(item.id)
    const blob = new Blob([res.data])
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = item.name
    link.click()
    URL.revokeObjectURL(link.href)
    ElMessage.success('下载成功')
  } catch (error) {
    ElMessage.error('下载失败')
  }
}

onMounted(() => {
  loadResources()
})
</script>

<style scoped>
.course-resources {
  padding: 20px;
}
.course-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 24px;
}
.resource-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  margin: 8px 0;
  background: #f8fafc;
  border-radius: 8px;
}
</style>
