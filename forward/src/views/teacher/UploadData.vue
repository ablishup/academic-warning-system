<template>
  <div class="upload-page">
    <div class="page-header">
      <h1>数据上传</h1>
      <p>上传学生成绩、学习活动等数据</p>
    </div>

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
          >
            <el-button type="primary" :loading="uploading.activities">
              <el-icon><Upload /></el-icon>
              上传文件
            </el-button>
          </el-upload>
          <el-button link type="primary" @click="downloadTemplate('activities')">
            下载模板
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
          >
            <el-button type="primary" :loading="uploading.homework">
              <el-icon><Upload /></el-icon>
              上传文件
            </el-button>
          </el-upload>
          <el-button link type="primary" @click="downloadTemplate('homework')">
            下载模板
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
          >
            <el-button type="primary" :loading="uploading.exams">
              <el-icon><Upload /></el-icon>
              上传文件
            </el-button>
          </el-upload>
          <el-button link type="primary" @click="downloadTemplate('exams')">
            下载模板
          </el-button>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="tip-card" shadow="never">
      <template #header>
        <span>上传说明</span>
      </template>
      <ul>
        <li>请使用Excel文件（.xlsx 或 .xls 格式）</li>
        <li>数据格式请参考模板文件</li>
        <li>单次上传数据量建议不超过1000条</li>
        <li>上传后会自动更新学生学情分析</li>
      </ul>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Document, EditPen, TrendCharts, Upload } from '@element-plus/icons-vue'
import { importActivities, importHomework, importExams, getImportTemplate } from '@/api/teacher'
import { ElMessage } from 'element-plus'

const uploading = ref({
  activities: false,
  homework: false,
  exams: false
})

const uploadUrl = 'http://localhost:8000/api/import/activities/'

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
  try {
    const res = await getImportTemplate(type)
    const blob = new Blob([res.data])
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `${type}_template.xlsx`
    link.click()
    URL.revokeObjectURL(link.href)
    ElMessage.success('模板下载成功')
  } catch (error) {
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
