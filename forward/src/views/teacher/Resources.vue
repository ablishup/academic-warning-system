<template>
  <div class="resources-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <h1>教学资源管理</h1>
        <p>管理课程相关的教学资料，包括视频、文档、课件等</p>
      </div>
      <el-button type="primary" size="large" @click="showUploadDialog = true">
        <el-icon><Upload /></el-icon>
        上传资源
      </el-button>
    </div>

    <!-- 筛选栏 -->
    <el-card class="filter-card" shadow="never">
      <div class="filter-row">
        <div class="filter-item">
          <span class="filter-label">选择课程：</span>
          <el-select
            v-model="selectedCourse"
            placeholder="请选择课程"
            clearable
            style="width: 220px"
            @change="handleCourseChange"
          >
            <el-option
              v-for="course in courses"
              :key="course.id"
              :label="course.name"
              :value="course.id"
            />
          </el-select>
        </div>

        <div class="filter-tabs">
          <el-radio-group v-model="selectedType" @change="handleTypeChange">
            <el-radio-button label="">全部</el-radio-button>
            <el-radio-button label="video">视频</el-radio-button>
            <el-radio-button label="document">文档</el-radio-button>
            <el-radio-button label="ppt">课件</el-radio-button>
            <el-radio-button label="exercise">习题</el-radio-button>
          </el-radio-group>
        </div>

        <el-input
          v-model="searchQuery"
          placeholder="搜索资源名称"
          style="width: 200px"
          clearable
          :prefix-icon="Search"
        />
      </div>
    </el-card>

    <!-- 资源列表 -->
    <el-card class="resources-card" shadow="never" v-loading="loading">
      <!-- 空状态 -->
      <el-empty
        v-if="!loading && filteredResources.length === 0"
        description="暂无资源"
      >
        <template #image>
          <el-icon :size="60" color="#dcdfe6"><FolderOpened /></el-icon>
        </template>
        <template #description>
          <p>{{ emptyText }}</p>
        </template>
        <el-button type="primary" @click="showUploadDialog = true">立即上传</el-button>
      </el-empty>

      <!-- 资源网格 -->
      <div v-else class="resources-grid">
        <div
          v-for="resource in filteredResources"
          :key="resource.id"
          class="resource-card"
        >
          <div class="resource-icon" :style="{ background: getIconBg(resource.resource_type) }">
            <el-icon :size="32" color="#fff">
              <component :is="getIcon(resource.resource_type)" />
            </el-icon>
          </div>

          <div class="resource-info">
            <h4 class="resource-name" :title="resource.name">{{ resource.name }}</h4>
            <div class="resource-meta">
              <el-tag size="small" :type="getTypeTag(resource.resource_type)">
                {{ getTypeLabel(resource.resource_type) }}
              </el-tag>
              <span class="resource-size">{{ formatSize(resource.file_size) }}</span>
            </div>
            <div class="resource-stats">
              <span>
                <el-icon><Download /></el-icon>
                {{ resource.download_count }} 次下载
              </span>
              <span>{{ formatDate(resource.created_at) }}</span>
            </div>
          </div>

          <div class="resource-actions">
            <el-button
              type="primary"
              link
              size="small"
              @click="downloadResource(resource)"
            >
              <el-icon><Download /></el-icon>
              下载
            </el-button>
            <el-button
              type="danger"
              link
              size="small"
              @click="deleteResource(resource)"
            >
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </div>
        </div>
      </div>

      <!-- 分页 -->
      <div v-if="filteredResources.length > 0" class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[12, 24, 36]"
          :total="total"
          layout="total, sizes, prev, pager, next"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 上传资源弹窗 -->
    <el-dialog
      v-model="showUploadDialog"
      title="上传教学资源"
      width="550px"
      destroy-on-close
    >
      <el-form
        ref="uploadFormRef"
        :model="uploadForm"
        :rules="uploadRules"
        label-width="100px"
      >
        <el-form-item label="选择课程" prop="course">
          <el-select
            v-model="uploadForm.course"
            placeholder="请选择课程"
            style="width: 100%"
          >
            <el-option
              v-for="course in courses"
              :key="course.id"
              :label="course.name"
              :value="course.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="资源类型" prop="resource_type">
          <el-radio-group v-model="uploadForm.resource_type">
            <el-radio label="video">视频</el-radio>
            <el-radio label="document">文档</el-radio>
            <el-radio label="ppt">课件</el-radio>
            <el-radio label="exercise">习题</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="资源描述" prop="description">
          <el-input
            v-model="uploadForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入资源描述（可选）"
          />
        </el-form-item>

        <el-form-item label="上传文件" prop="file">
          <el-upload
            ref="uploadRef"
            drag
            action=""
            :auto-upload="false"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
            :limit="1"
            accept=".mp4,.avi,.pdf,.doc,.docx,.ppt,.pptx,.xls,.xlsx,.zip,.rar"
          >
            <el-icon :size="48" class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              将文件拖到此处，或 <em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持视频、文档、课件等格式，单个文件不超过500MB
              </div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showUploadDialog = false">取消</el-button>
        <el-button
          type="primary"
          :loading="uploading"
          @click="confirmUpload"
        >
          确认上传
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import {
  Upload, Search, FolderOpened, Download, Delete,
  VideoPlay, Document, DataAnalysis, QuestionFilled,
  UploadFilled
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getTeacherCourses, uploadCourseResource, deleteCourseResource } from '@/api/teacher'
import request from '@/api/request'

// 状态
const loading = ref(false)
const uploading = ref(false)
const showUploadDialog = ref(false)
const selectedCourse = ref('')
const selectedType = ref('')
const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = ref(12)
const total = ref(0)

// 数据
const courses = ref([])
const resources = ref([])
const uploadRef = ref(null)
const uploadFormRef = ref(null)

// 上传表单
const uploadForm = reactive({
  course: '',
  resource_type: 'document',
  description: '',
  file: null
})

// 上传验证规则
const uploadRules = {
  course: [{ required: true, message: '请选择课程', trigger: 'change' }],
  resource_type: [{ required: true, message: '请选择资源类型', trigger: 'change' }],
  file: [{ required: true, message: '请上传文件', trigger: 'change' }]
}

// 资源类型映射
const typeMap = {
  video: { label: '视频', icon: VideoPlay, tag: 'danger', bg: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' },
  document: { label: '文档', icon: Document, tag: 'primary', bg: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)' },
  ppt: { label: '课件', icon: DataAnalysis, tag: 'warning', bg: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)' },
  exercise: { label: '习题', icon: QuestionFilled, tag: 'success', bg: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)' }
}

// 计算属性
const filteredResources = computed(() => {
  let result = resources.value

  if (selectedCourse.value) {
    result = result.filter(r => r.course === selectedCourse.value || r.course_id === selectedCourse.value)
  }

  if (selectedType.value) {
    result = result.filter(r => r.resource_type === selectedType.value)
  }

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(r => r.name.toLowerCase().includes(query))
  }

  return result
})

const emptyText = computed(() => {
  if (selectedCourse.value && resources.value.length === 0) {
    return '该课程暂无资源，请上传'
  }
  if (selectedType.value && resources.value.length === 0) {
    return '暂无该类型的资源'
  }
  if (searchQuery.value) {
    return '未找到匹配的资源'
  }
  return '暂无资源，请上传'
})

// 方法
const loadCourses = async () => {
  try {
    const res = await getTeacherCourses()
    if (res.code === 200) {
      courses.value = res.data
      // 默认选择第一个课程
      if (courses.value.length > 0 && !selectedCourse.value) {
        selectedCourse.value = courses.value[0].id
        loadResources()
      }
    }
  } catch (error) {
    ElMessage.error('加载课程列表失败')
  }
}

const loadResources = async () => {
  loading.value = true
  try {
    const params = {}
    if (selectedCourse.value) {
      params.course_id = selectedCourse.value
    }
    if (selectedType.value) {
      params.resource_type = selectedType.value
    }

    const res = await request({
      url: '/courses/resources/',
      method: 'get',
      params
    })

    if (res.code === 200) {
      resources.value = res.data.results || res.data
      total.value = res.data.count || resources.value.length
    }
  } catch (error) {
    ElMessage.error('加载资源列表失败')
    // 使用模拟数据
    resources.value = getMockResources()
  } finally {
    loading.value = false
  }
}

const getMockResources = () => {
  const mockData = [
    { id: 1, name: '第一章：绪论讲解视频.mp4', resource_type: 'video', file_size: 1024 * 1024 * 50, download_count: 128, created_at: '2025-04-08', course: 1 },
    { id: 2, name: '课程大纲与教学计划.pdf', resource_type: 'document', file_size: 1024 * 512, download_count: 256, created_at: '2025-04-07', course: 1 },
    { id: 3, name: '第二章：核心概念课件.pptx', resource_type: 'ppt', file_size: 1024 * 1024 * 5, download_count: 89, created_at: '2025-04-06', course: 1 },
    { id: 4, name: '第一次作业习题集.docx', resource_type: 'exercise', file_size: 1024 * 256, download_count: 167, created_at: '2025-04-05', course: 1 },
    { id: 5, name: '实验指导手册.pdf', resource_type: 'document', file_size: 1024 * 1024 * 2, download_count: 98, created_at: '2025-04-04', course: 1 },
    { id: 6, name: '复习重点讲解视频.mp4', resource_type: 'video', file_size: 1024 * 1024 * 80, download_count: 234, created_at: '2025-04-03', course: 1 },
  ]
  return selectedCourse.value
    ? mockData.filter(r => r.course === selectedCourse.value)
    : mockData
}

const handleCourseChange = () => {
  loadResources()
}

const handleTypeChange = () => {
  loadResources()
}

const handleSizeChange = (val) => {
  pageSize.value = val
  loadResources()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  loadResources()
}

const getIcon = (type) => {
  return typeMap[type]?.icon || Document
}

const getIconBg = (type) => {
  return typeMap[type]?.bg || '#909399'
}

const getTypeLabel = (type) => {
  return typeMap[type]?.label || type
}

const getTypeTag = (type) => {
  return typeMap[type]?.tag || 'info'
}

const formatSize = (bytes) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

const handleFileChange = (file) => {
  uploadForm.file = file.raw
}

const handleFileRemove = () => {
  uploadForm.file = null
}

const confirmUpload = async () => {
  if (!uploadFormRef.value) return

  await uploadFormRef.value.validate(async (valid) => {
    if (!valid) return

    if (!uploadForm.file) {
      ElMessage.warning('请上传文件')
      return
    }

    uploading.value = true
    try {
      const formData = new FormData()
      formData.append('file', uploadForm.file)
      formData.append('course', uploadForm.course)
      formData.append('resource_type', uploadForm.resource_type)
      if (uploadForm.description) {
        formData.append('description', uploadForm.description)
      }

      const res = await uploadCourseResource(formData)

      if (res.code === 200) {
        ElMessage.success('上传成功')
        showUploadDialog.value = false
        // 重置表单
        uploadForm.course = ''
        uploadForm.resource_type = 'document'
        uploadForm.description = ''
        uploadForm.file = null
        uploadRef.value?.clearFiles()
        // 刷新列表
        loadResources()
      } else {
        ElMessage.error(res.message || '上传失败')
      }
    } catch (error) {
      ElMessage.error('上传失败')
    } finally {
      uploading.value = false
    }
  })
}

const downloadResource = (resource) => {
  try {
    // 使用 window.open 下载文件
    const url = `http://localhost:8000/api/courses/resources/${resource.id}/download/`
    window.open(url, '_blank')
    ElMessage.success('开始下载')
  } catch (error) {
    ElMessage.error('下载失败')
  }
}

const deleteResource = (resource) => {
  ElMessageBox.confirm(
    `确定要删除资源 "${resource.name}" 吗？此操作不可恢复。`,
    '删除确认',
    {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      const res = await deleteCourseResource(resource.id)
      if (res.code === 200) {
        ElMessage.success('删除成功')
        loadResources()
      } else {
        ElMessage.error(res.message || '删除失败')
      }
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

onMounted(() => {
  loadCourses()
})
</script>

<style scoped>
.resources-page {
  max-width: 1200px;
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
  font-size: 14px;
}

.filter-card {
  margin-bottom: 20px;
  border-radius: 12px;
}

.filter-row {
  display: flex;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-label {
  font-size: 14px;
  color: #374151;
  font-weight: 500;
}

.filter-tabs {
  flex: 1;
}

.resources-card {
  border-radius: 12px;
  min-height: 400px;
}

.resources-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.resource-card {
  background: #f9fafb;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  transition: all 0.3s ease;
  border: 1px solid #e5e7eb;
}

.resource-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
  border-color: #3b82f6;
}

.resource-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.resource-info {
  flex: 1;
}

.resource-name {
  font-size: 15px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.resource-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.resource-size {
  font-size: 12px;
  color: #6b7280;
}

.resource-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #9ca3af;
}

.resource-stats span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.resource-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding-top: 12px;
  border-top: 1px solid #e5e7eb;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #e5e7eb;
}

/* 上传弹窗样式 */
:deep(.el-upload-dragger) {
  width: 100%;
  padding: 30px 20px;
}

:deep(.el-upload__tip) {
  text-align: center;
  color: #6b7280;
}

/* 响应式 */
@media (max-width: 768px) {
  .filter-row {
    flex-direction: column;
    align-items: stretch;
  }

  .resources-grid {
    grid-template-columns: 1fr;
  }
}
</style>
