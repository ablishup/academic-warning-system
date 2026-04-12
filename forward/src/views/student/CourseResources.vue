<template>
  <div class="course-resources">
    <div class="course-header">
      <el-button :icon="ArrowLeft" @click="goBack">返回课程列表</el-button>
      <h2>{{ courseName }}</h2>
    </div>

    <el-tabs v-model="activeTab" v-loading="loading">
      <el-tab-pane label="视频" name="video">
        <div v-for="item in videoResources" :key="item.id" class="resource-item">
          <div class="resource-info">
            <el-icon :size="24" class="resource-icon video-icon"><VideoPlay /></el-icon>
            <div class="resource-meta">
              <span class="resource-name">{{ item.name }}</span>
              <span class="resource-size" v-if="item.size">{{ formatFileSize(item.size) }}</span>
            </div>
          </div>
          <el-button type="primary" size="small" @click="watchVideo(item)">
            <el-icon><VideoPlay /></el-icon>
            观看
          </el-button>
        </div>
        <el-empty v-if="videoResources.length === 0" description="暂无视频资源" />
      </el-tab-pane>
      <el-tab-pane label="文档" name="document">
        <div v-for="item in documentResources" :key="item.id" class="resource-item">
          <div class="resource-info">
            <el-icon :size="24" class="resource-icon doc-icon"><Document /></el-icon>
            <div class="resource-meta">
              <span class="resource-name">{{ item.name }}</span>
              <span class="resource-size" v-if="item.size">{{ formatFileSize(item.size) }}</span>
            </div>
          </div>
          <el-button type="primary" size="small" @click="downloadResource(item)">
            <el-icon><Download /></el-icon>
            下载
          </el-button>
        </div>
        <el-empty v-if="documentResources.length === 0" description="暂无文档" />
      </el-tab-pane>
      <el-tab-pane label="习题" name="exercise">
        <div v-for="item in exerciseResources" :key="item.id" class="resource-item">
          <div class="resource-info">
            <el-icon :size="24" class="resource-icon exercise-icon"><EditPen /></el-icon>
            <div class="resource-meta">
              <span class="resource-name">{{ item.name }}</span>
              <span class="resource-size" v-if="item.size">{{ formatFileSize(item.size) }}</span>
            </div>
          </div>
          <el-button type="primary" size="small" @click="downloadResource(item)">
            <el-icon><Download /></el-icon>
            下载
          </el-button>
        </div>
        <el-empty v-if="exerciseResources.length === 0" description="暂无习题" />
      </el-tab-pane>
    </el-tabs>

    <!-- 视频播放弹窗 -->
    <el-dialog
      v-model="videoDialogVisible"
      :title="currentVideo?.name"
      width="800px"
      destroy-on-close
      :close-on-click-modal="false"
      @close="handleVideoClose"
    >
      <div class="video-player-container">
        <video
          ref="videoPlayer"
          class="video-player"
          controls
          :src="currentVideo?.file_url || currentVideo?.url"
          @play="handleVideoPlay"
          @pause="handleVideoPause"
          @ended="handleVideoEnded"
          @timeupdate="handleTimeUpdate"
        ></video>
      </div>
      <div class="video-info">
        <el-alert
          v-if="currentVideoProgress > 0"
          :title="`上次观看到 ${Math.floor(currentVideoProgress)}%`"
          type="info"
          :closable="false"
          show-icon
        />
        <div class="video-status">
          <el-tag :type="uploadStatus.type" size="small">
            {{ uploadStatus.text }}
          </el-tag>
          <span v-if="currentDuration > 0" class="duration-text">
            本次观看: {{ formatDuration(currentDuration) }}
          </span>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, VideoPlay, Document, EditPen, Download } from '@element-plus/icons-vue'
import { getCourseResources, downloadCourseResource, recordLearningActivity } from '@/api/student'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const courseId = ref(route.query.courseId)
const courseName = ref(route.query.courseName || '课程资源')
const activeTab = ref('video')
const loading = ref(false)
const resources = ref([])

// 视频播放相关
const videoDialogVisible = ref(false)
const currentVideo = ref(null)
const videoPlayer = ref(null)
const currentVideoProgress = ref(0)
const currentDuration = ref(0)
const uploadStatus = ref({ type: 'info', text: '准备就绪' })

// 进度上报相关
const progressTimer = ref(null)
const lastReportedTime = ref(0)
const videoStartTime = ref(0)
const isPlaying = ref(false)

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

// 格式化文件大小
const formatFileSize = (size) => {
  if (!size) return ''
  if (size < 1024) return size + ' B'
  if (size < 1024 * 1024) return (size / 1024).toFixed(1) + ' KB'
  if (size < 1024 * 1024 * 1024) return (size / (1024 * 1024)).toFixed(1) + ' MB'
  return (size / (1024 * 1024 * 1024)).toFixed(1) + ' GB'
}

// 格式化时长
const formatDuration = (seconds) => {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  if (mins > 0) {
    return `${mins}分${secs}秒`
  }
  return `${secs}秒`
}

// 观看视频
const watchVideo = async (item) => {
  currentVideo.value = item
  currentVideoProgress.value = item.progress || 0
  currentDuration.value = 0
  videoStartTime.value = 0
  lastReportedTime.value = 0
  isPlaying.value = false
  uploadStatus.value = { type: 'info', text: '准备就绪' }
  videoDialogVisible.value = true

  // 记录视频开始播放的学习活动
  try {
    await recordLearningActivity({
      course_id: parseInt(courseId.value),
      activity_type: 'video_start',
      activity_name: item.name,
      duration: 0,
      progress: item.progress || 0
    })
  } catch (error) {
    console.error('记录视频开始失败:', error)
  }
}

// 视频播放事件
const handleVideoPlay = () => {
  isPlaying.value = true
  if (videoStartTime.value === 0) {
    videoStartTime.value = Date.now()
  }
  uploadStatus.value = { type: 'success', text: '正在观看' }

  // 启动定时上报（每30秒）
  if (!progressTimer.value) {
    progressTimer.value = setInterval(() => {
      reportProgress(false)
    }, 30000) // 30秒上报一次
  }
}

// 视频暂停事件
const handleVideoPause = () => {
  isPlaying.value = false
  uploadStatus.value = { type: 'warning', text: '已暂停' }
  // 暂停时立即上报一次
  reportProgress(false)
}

// 视频播放进度更新
const handleTimeUpdate = (e) => {
  const video = e.target
  if (video.duration) {
    const progress = (video.currentTime / video.duration) * 100
    currentVideoProgress.value = progress

    // 更新本次观看时长
    if (videoStartTime.value > 0) {
      currentDuration.value = Math.floor((Date.now() - videoStartTime.value) / 1000)
    }
  }
}

// 视频播放结束
const handleVideoEnded = async () => {
  isPlaying.value = false
  uploadStatus.value = { type: 'success', text: '播放完成' }

  // 清除定时器
  if (progressTimer.value) {
    clearInterval(progressTimer.value)
    progressTimer.value = null
  }

  // 上报最终进度
  await reportProgress(true)

  ElMessage.success('视频观看完成！')
}

// 上报进度
const reportProgress = async (isFinal = false) => {
  if (!currentVideo.value || !videoPlayer.value) return

  const video = videoPlayer.value
  const currentTime = Math.floor(video.currentTime)
  const duration = Math.floor(video.duration || 0)
  const progress = duration > 0 ? (currentTime / duration) * 100 : 0

  // 避免重复上报相同时间点
  if (!isFinal && currentTime === lastReportedTime.value) return

  try {
    uploadStatus.value = { type: 'primary', text: isFinal ? '正在保存...' : '同步中...' }

    await recordLearningActivity({
      course_id: parseInt(courseId.value),
      activity_type: 'video',
      activity_name: currentVideo.value.name,
      duration: currentDuration.value,
      progress: parseFloat(progress.toFixed(1))
    })

    lastReportedTime.value = currentTime
    uploadStatus.value = { type: 'success', text: isFinal ? '已保存' : '已同步' }

    // 3秒后恢复状态
    if (!isFinal) {
      setTimeout(() => {
        if (isPlaying.value) {
          uploadStatus.value = { type: 'success', text: '正在观看' }
        }
      }, 3000)
    }
  } catch (error) {
    console.error('上报进度失败:', error)
    uploadStatus.value = { type: 'danger', text: '同步失败' }
  }
}

// 关闭视频弹窗
const handleVideoClose = () => {
  // 清除定时器
  if (progressTimer.value) {
    clearInterval(progressTimer.value)
    progressTimer.value = null
  }

  // 如果正在播放，上报最终进度
  if (isPlaying.value && currentVideo.value) {
    reportProgress(true)
  }

  // 重置状态
  currentVideo.value = null
  isPlaying.value = false
  videoStartTime.value = 0
  currentDuration.value = 0
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

onUnmounted(() => {
  // 组件卸载时清理定时器
  if (progressTimer.value) {
    clearInterval(progressTimer.value)
    progressTimer.value = null
  }
})
</script>

<style scoped>
.course-resources {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.course-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 24px;
}

.course-header h2 {
  margin: 0;
  font-size: 20px;
  color: #1f2937;
}

.resource-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  margin: 12px 0;
  background: #f8fafc;
  border-radius: 12px;
  transition: all 0.3s;
}

.resource-item:hover {
  background: #f1f5f9;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.resource-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.resource-icon {
  padding: 8px;
  border-radius: 8px;
}

.video-icon {
  color: #ef4444;
  background: #fef2f2;
}

.doc-icon {
  color: #3b82f6;
  background: #eff6ff;
}

.exercise-icon {
  color: #10b981;
  background: #ecfdf5;
}

.resource-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.resource-name {
  font-weight: 500;
  color: #1f2937;
}

.resource-size {
  font-size: 12px;
  color: #6b7280;
}

/* 视频播放器 */
.video-player-container {
  width: 100%;
  background: #000;
  border-radius: 8px;
  overflow: hidden;
}

.video-player {
  width: 100%;
  max-height: 450px;
  display: block;
}

.video-info {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.video-status {
  display: flex;
  align-items: center;
  gap: 12px;
}

.duration-text {
  color: #6b7280;
  font-size: 14px;
}
</style>
