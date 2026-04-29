<template>
  <div class="batch-import-buttons">
    <el-upload
      action="#"
      :auto-upload="false"
      :show-file-list="false"
      :on-change="handleFileChange"
      class="upload-inline"
    >
      <el-button type="success">
        <el-icon><Upload /></el-icon>
        批量导入
      </el-button>
    </el-upload>
    <el-button type="info" @click="handleDownloadTemplate">
      <el-icon><Download /></el-icon>
      模板下载
    </el-button>
  </div>
</template>

<script setup>
import { Upload, Download } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  module: { type: String, required: true },
  templateUrl: { type: String, default: '' },
  importApi: { type: Function, default: null },
  templateName: { type: String, default: '' }
})

const moduleLabelMap = {
  course: '课程',
  teacher: '教师',
  student: '学生',
  counselor: '辅导员',
  class: '班级'
}

const getModuleLabel = () => moduleLabelMap[props.module] || props.module

const handleFileChange = (file) => {
  if (props.importApi) {
    // 后续接入真实导入逻辑：props.importApi(file.raw)
    ElMessage.info(`${getModuleLabel()} 批量导入功能开发中`)
  } else {
    ElMessage.info(`${getModuleLabel()} 批量导入功能开发中`)
  }
}

const handleDownloadTemplate = () => {
  if (props.templateUrl) {
    // 后续接入真实下载逻辑：window.open(props.templateUrl)
    ElMessage.info(`${getModuleLabel()} 模板下载功能开发中`)
  } else {
    ElMessage.info(`${getModuleLabel()} 模板下载功能开发中`)
  }
}
</script>

<style scoped>
.batch-import-buttons {
  display: inline-flex;
  gap: 8px;
  margin-left: 8px;
}
.upload-inline {
  display: inline-block;
}
</style>
