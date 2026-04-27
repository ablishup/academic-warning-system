<template>
  <div class="upload-page">
    <div class="page-header">
      <h1>数据上传</h1>
      <p>上传学生成绩、学习活动等数据</p>
    </div>

    <!-- 课程选择 -->
    <el-card class="course-select-card" shadow="never">
      <div class="course-select-wrapper">
        <span class="select-label">选择课程：</span>
        <el-select
          v-model="selectedCourse"
          placeholder="请选择要上传数据的课程"
          style="width: 300px"
          @change="handleCourseChange"
        >
          <el-option
            v-for="course in courses"
            :key="course.id"
            :label="course.name"
            :value="course.id"
          />
        </el-select>
        <el-tag v-if="selectedCourse" type="success" class="student-count-tag">
          {{ getStudentCount(selectedCourse) }} 名学生
        </el-tag>
      </div>
    </el-card>

    <el-row :gutter="20">
      <el-col :span="8">
        <el-card class="upload-card" shadow="hover">
          <div class="upload-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%)">
            <el-icon :size="32"><Document /></el-icon>
          </div>
          <h3>学习活动数据</h3>
          <p>上传学生视频观看、签到等学习活动记录</p>
          <el-upload
            class="upload-btn"
            :action="uploadUrl"
            :http-request="customUpload('activities')"
            :show-file-list="false"
            accept=".xlsx,.xls"
            :disabled="!selectedCourse"
          >
            <el-button type="primary" :loading="uploading.activities" :disabled="!selectedCourse">
              <el-icon><Upload /></el-icon>
              上传文件
            </el-button>
          </el-upload>
          <el-button
            link
            type="primary"
            @click="downloadTemplate('activities')"
            :disabled="!selectedCourse"
          >
            {{ selectedCourse ? '下载模板（含学生名单）' : '请先选择课程' }}
          </el-button>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="upload-card" shadow="hover">
          <div class="upload-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%)">
            <el-icon :size="32"><EditPen /></el-icon>
          </div>
          <h3>作业成绩</h3>
          <p>上传学生作业提交情况和成绩</p>
          <el-upload
            class="upload-btn"
            :http-request="customUpload('homework')"
            :show-file-list="false"
            accept=".xlsx,.xls"
            :disabled="!selectedCourse"
          >
            <el-button type="primary" :loading="uploading.homework" :disabled="!selectedCourse">
              <el-icon><Upload /></el-icon>
              上传文件
            </el-button>
          </el-upload>
          <el-button
            link
            type="primary"
            @click="downloadTemplate('homework')"
            :disabled="!selectedCourse"
          >
            {{ selectedCourse ? '下载模板（含学生名单）' : '请先选择课程' }}
          </el-button>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="upload-card" shadow="hover">
          <div class="upload-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)">
            <el-icon :size="32"><TrendCharts /></el-icon>
          </div>
          <h3>考试成绩</h3>
          <p>上传学生考试成绩和测验结果</p>
          <el-upload
            class="upload-btn"
            :http-request="customUpload('exams')"
            :show-file-list="false"
            accept=".xlsx,.xls"
            :disabled="!selectedCourse"
          >
            <el-button type="primary" :loading="uploading.exams" :disabled="!selectedCourse">
              <el-icon><Upload /></el-icon>
              上传文件
            </el-button>
          </el-upload>
          <el-button
            link
            type="primary"
            @click="downloadTemplate('exams')"
            :disabled="!selectedCourse"
          >
            {{ selectedCourse ? '下载模板（含学生名单）' : '请先选择课程' }}
          </el-button>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="tip-card" shadow="never">
      <template #header>
        <span>上传说明</span>
      </template>
      <ul>
        <li><strong>请先选择课程</strong>，再下载模板或上传文件</li>
        <li>下载的模板已自动填充该课程的<strong>学生学号和姓名</strong>，请勿修改</li>
        <li>请使用Excel文件（.xlsx 或 .xls 格式）</li>
        <li>单次上传数据量建议不超过1000条</li>
        <li>上传后会自动更新学生学情分析</li>
      </ul>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { Document, EditPen, TrendCharts, Upload } from '@element-plus/icons-vue'
import { importActivities, importHomework, importExams, getImportTemplate, getTeacherCourses, getCourseStudents } from '@/api/teacher'
import { ElMessage } from 'element-plus'

const route = useRoute()

// 课程相关
const courses = ref([])
const selectedCourse = ref('')
const courseStudents = ref({})

const uploading = ref({
  activities: false,
  homework: false,
  exams: false
})

const uploadUrl = `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'}/import/activities/`

// 加载教师课程列表
const loadCourses = async () => {
  try {
    const res = await getTeacherCourses()
    if (res.code === 200) {
      courses.value = res.data || []

      // 检查URL查询参数中是否有course_id
      const queryCourseId = route.query.course_id
      if (queryCourseId) {
        const courseId = parseInt(queryCourseId)
        // 验证该课程是否在教师课程列表中
        const courseExists = courses.value.some(c => c.id === courseId)
        if (courseExists) {
          selectedCourse.value = courseId
          loadCourseStudents(courseId)
          ElMessage.success(`已自动选择课程：${courses.value.find(c => c.id === courseId)?.name}`)
        } else {
          // 如果URL中的course_id无效，默认选中第一个
          selectDefaultCourse()
        }
      } else {
        // 没有URL参数，默认选中第一个
        selectDefaultCourse()
      }
    }
  } catch (error) {
    console.error('加载课程列表失败:', error)
  }
}

// 默认选中第一个课程
const selectDefaultCourse = () => {
  if (courses.value.length > 0) {
    selectedCourse.value = courses.value[0].id
    loadCourseStudents(courses.value[0].id)
  }
}

// 加载课程学生数
const loadCourseStudents = async (courseId) => {
  try {
    const res = await getCourseStudents(courseId)
    if (res.code === 200) {
      const students = res.data?.students || []
      courseStudents.value[courseId] = students.length
    }
  } catch (error) {
    console.error('加载课程学生失败:', error)
  }
}

// 获取学生数
const getStudentCount = (courseId) => {
  return courseStudents.value[courseId] || 0
}

// 处理课程切换
const handleCourseChange = (courseId) => {
  if (courseId && !courseStudents.value[courseId]) {
    loadCourseStudents(courseId)
  }
}

onMounted(() => {
  loadCourses()
})

const customUpload = (type) => async (options) => {
  uploading.value[type] = true
  try {
    const formData = new FormData()
    formData.append('file', options.file)

    let res
    switch (type) {
      case 'activities':
        res = await importActivities(formData)
        break
      case 'homework':
        res = await importHomework(formData)
        break
      case 'exams':
        res = await importExams(formData)
        break
    }

    if (res.code === 200) {
      ElMessage.success('上传成功')
    } else {
      ElMessage.error(res.message || '上传失败')
    }
  } catch (error) {
    ElMessage.error('上传失败: ' + (error.message || '未知错误'))
  } finally {
    uploading.value[type] = false
  }
}

const downloadTemplate = async (type) => {
  if (!selectedCourse.value) {
    ElMessage.warning('请先选择课程')
    return
  }

  try {
    // 传入课程ID，后端会生成带学生名单的模板
    const blob = await getImportTemplate(type, selectedCourse.value)

    // 根据课程名称生成文件名
    const course = courses.value.find(c => c.id === selectedCourse.value)
    const courseName = course ? course.name : '课程'

    const filenameMap = {
      activities: `${courseName}_学习活动导入模板.xlsx`,
      homework: `${courseName}_作业成绩导入模板.xlsx`,
      exams: `${courseName}_考试成绩导入模板.xlsx`
    }
    const filename = filenameMap[type] || `${courseName}_导入模板.xlsx`

    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(link.href)

    ElMessage.success('模板下载成功，已包含该课程学生名单')
  } catch (error) {
    console.error('下载模板失败:', error)
    ElMessage.error('下载模板失败')
  }
}
</script>

<style scoped>
.upload-page {
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

.course-select-card {
  margin-bottom: 20px;
  border-radius: 12px;
}

.course-select-wrapper {
  display: flex;
  align-items: center;
  gap: 16px;
}

.select-label {
  font-size: 16px;
  font-weight: 500;
  color: #374151;
}

.student-count-tag {
  font-size: 14px;
}

.page-header p {
  color: #6b7280;
}

.upload-card {
  text-align: center;
  padding: 20px;
}

.upload-card :deep(.el-card__body) {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.upload-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-bottom: 16px;
}

.upload-card h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 8px;
}

.upload-card p {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 20px;
  min-height: 40px;
}

.upload-btn {
  margin-bottom: 12px;
}

.tip-card {
  margin-top: 24px;
  border-radius: 12px;
}

.tip-card ul {
  padding-left: 20px;
  color: #6b7280;
  line-height: 2;
}
</style>
