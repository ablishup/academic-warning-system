<template>
  <div class="ai-comment-page">
    <el-page-header title="AI评语管理" @back="$router.back()">
      <template #content>
        <span class="page-title">AI评语管理</span>
      </template>
    </el-page-header>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon blue">
            <el-icon><Warning /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalWarnings }}</div>
            <div class="stat-label">预警总数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon green">
            <el-icon><ChatDotRound /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.generatedComments }}</div>
            <div class="stat-label">已生成评语</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon orange">
            <el-icon><Message /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.sentSMS }}</div>
            <div class="stat-label">已发送短信</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon purple">
            <el-icon><User /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.pendingComments }}</div>
            <div class="stat-label">待生成评语</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 筛选栏 -->
    <el-card class="filter-card">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-input
            v-model="filter.search"
            placeholder="搜索学生姓名/学号"
            clearable
            @keyup.enter="loadWarnings"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :span="4">
          <el-select v-model="filter.riskLevel" placeholder="风险等级" clearable @change="loadWarnings">
            <el-option label="全部" value="" />
            <el-option label="红色预警" value="high">
              <el-tag type="danger" size="small">红色预警</el-tag>
            </el-option>
            <el-option label="橙色预警" value="medium">
              <el-tag type="warning" size="small">橙色预警</el-tag>
            </el-option>
            <el-option label="黄色预警" value="low">
              <el-tag type="info" size="small">黄色预警</el-tag>
            </el-option>
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="filter.commentStatus" placeholder="评语状态" clearable @change="loadWarnings">
            <el-option label="全部" value="" />
            <el-option label="已生成" value="generated" />
            <el-option label="未生成" value="pending" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-button type="primary" @click="loadWarnings">
            <el-icon><Search /></el-icon>查询
          </el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 预警列表 -->
    <el-card class="list-card">
      <el-table
        :data="warningList"
        v-loading="loading"
        stripe
        style="width: 100%"
      >
        <el-table-column type="index" width="50" />
        <el-table-column label="学生" min-width="150">
          <template #default="{ row }">
            <div class="student-cell">
              <div class="student-info">
                <div class="name">{{ row.student_name }}</div>
                <div class="no">{{ row.student_no }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="课程" prop="course_name" min-width="120" />
        <el-table-column label="风险等级" width="100">
          <template #default="{ row }">
            <RiskBadge :level="row.risk_level" />
          </template>
        </el-table-column>
        <el-table-column label="综合得分" width="100">
          <template #default="{ row }">
            <el-tag :type="getScoreType(row.composite_score)">
              {{ row.composite_score }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="AI评语" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.counselor_comment" type="success">已生成</el-tag>
            <el-tag v-else type="info">未生成</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="短信通知" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.sms_sent" type="success">已发送</el-tag>
            <el-tag v-else type="info">未发送</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="生成时间" width="150">
          <template #default="{ row }">
            {{ formatTime(row.ai_generated_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              @click="generateComment(row)"
              :loading="row.generating"
            >
              {{ row.counselor_comment ? '重新生成' : '生成评语' }}
            </el-button>
            <el-button
              type="success"
              size="small"
              @click="viewDetail(row)"
              :disabled="!row.counselor_comment"
            >
              查看
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next"
          @size-change="loadWarnings"
          @current-change="loadWarnings"
        />
      </div>
    </el-card>

    <!-- 评语详情弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      title="AI评语详情"
      width="700px"
      :close-on-click-modal="false"
    >
      <div v-if="currentComment" class="comment-detail">
        <!-- 学生信息 -->
        <div class="student-header">
          <div class="student-info">
            <h3>{{ currentComment.student_name }}</h3>
            <p>{{ currentComment.student_no }} | {{ currentComment.class_name || '未知班级' }}</p>
          </div>
          <RiskBadge :level="currentComment.risk_level" />
        </div>

        <el-divider />

        <!-- 评语内容 -->
        <div class="comment-content">
          <section v-if="currentComment.summary">
            <h4><el-icon><Document /></el-icon> 总体评价</h4>
            <p class="summary">{{ currentComment.summary }}</p>
          </section>

          <section v-if="currentComment.analysis">
            <h4><el-icon><Warning /></el-icon> 问题分析</h4>
            <p>{{ currentComment.analysis }}</p>
          </section>

          <section v-if="currentComment.suggestions?.length">
            <h4><el-icon><List /></el-icon> 建议措施</h4>
            <ol>
              <li v-for="(item, index) in currentComment.suggestions" :key="index">
                {{ item }}
              </li>
            </ol>
          </section>

          <section v-if="currentComment.action_plan">
            <h4><el-icon><Calendar /></el-icon> 行动计划</h4>
            <el-alert type="info" :closable="false">
              {{ currentComment.action_plan }}
            </el-alert>
          </section>

          <section v-if="currentComment.talking_points" class="talking-section">
            <h4><el-icon><ChatDotRound /></el-icon> 沟通话术建议</h4>
            <el-card shadow="never" class="talking-card">
              {{ currentComment.talking_points }}
            </el-card>
          </section>
        </div>

        <!-- 操作按钮 -->
        <div class="comment-actions">
          <el-button type="primary" @click="showSMSEditor = true">
            <el-icon><Message /></el-icon>
            发送短信通知
          </el-button>
          <el-button @click="regenerateComment">
            <el-icon><Refresh /></el-icon>
            重新生成
          </el-button>
        </div>
      </div>
    </el-dialog>

    <!-- 短信编辑弹窗 -->
    <el-dialog
      v-model="showSMSEditor"
      title="发送短信通知"
      width="500px"
    >
      <el-form :model="smsForm" label-position="top">
        <el-form-item label="接收手机号">
          <el-input v-model="smsForm.phone" placeholder="请输入手机号">
            <template #prepend>
              <el-icon><Iphone /></el-icon>
            </template>
          </el-input>
          <div class="form-tip" v-if="currentComment?.student_phone">
            学生注册手机号: {{ currentComment.student_phone }}
            <el-link type="primary" @click="smsForm.phone = currentComment.student_phone">
              使用此号码
            </el-link>
          </div>
        </el-form-item>

        <el-form-item label="短信内容">
          <el-input
            v-model="smsForm.message"
            type="textarea"
            :rows="4"
            maxlength="200"
            show-word-limit
            placeholder="请输入短信内容"
          />
        </el-form-item>

        <div class="quick-templates">
          <span class="label">快速模板:</span>
          <el-tag
            v-for="t in smsTemplates"
            :key="t.value"
            @click="applyTemplate(t)"
            class="template-tag"
            size="small"
          >
            {{ t.label }}
          </el-tag>
        </div>
      </el-form>

      <template #footer>
        <el-button @click="showSMSEditor = false">取消</el-button>
        <el-button type="primary" @click="sendSMS" :loading="sending">
          发送
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Warning, ChatDotRound, Message, User, Search,
  UserFilled, Document, List, Calendar, ChatDotRound as ChatIcon,
  Refresh, Iphone
} from '@element-plus/icons-vue'
// RiskBadge 组件内联定义
const RiskBadge = {
  props: ['level'],
  setup(props) {
    const typeMap = {
      high: 'danger',
      medium: 'warning',
      low: 'info',
      normal: 'success'
    }
    const labelMap = {
      high: '红色预警',
      medium: '橙色预警',
      low: '黄色预警',
      normal: '正常'
    }
    return { typeMap, labelMap }
  },
  template: '<el-tag :type="typeMap[level] || \'info\'" size="small">{{ labelMap[level] || level }}</el-tag>'
}
import {
  getWarningRecords,
  generateCounselorComment,
  getStoredComment,
  sendSMSNotification
} from '@/api/counselor'

// 状态
const loading = ref(false)
const dialogVisible = ref(false)
const showSMSEditor = ref(false)
const sending = ref(false)
const warningList = ref([])
const currentComment = ref(null)
const currentWarning = ref(null)

// 筛选
const filter = reactive({
  search: '',
  riskLevel: '',
  commentStatus: ''
})

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

// 统计
const stats = reactive({
  totalWarnings: 0,
  generatedComments: 0,
  sentSMS: 0,
  pendingComments: 0
})

// 短信表单
const smsForm = reactive({
  phone: '',
  message: ''
})

const smsTemplates = [
  { label: '标准通知', value: 'standard' },
  { label: '紧急提醒', value: 'urgent' },
  { label: '关怀鼓励', value: 'care' }
]

// 加载预警列表
const loadWarnings = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      status: 'active'
    }
    if (filter.search) params.search = filter.search
    if (filter.riskLevel) params.risk_level = filter.riskLevel

    const res = await getWarningRecords(params)
    if (res.code === 200) {
      warningList.value = res.data.results || []
      pagination.total = res.data.count || 0

      // 计算统计
      calculateStats()
    }
  } catch (error) {
    console.error('加载预警列表失败:', error)
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

// 计算统计
const calculateStats = () => {
  const list = warningList.value
  stats.totalWarnings = list.length
  stats.generatedComments = list.filter(w => w.counselor_comment).length
  stats.sentSMS = list.filter(w => w.sms_sent).length
  stats.pendingComments = list.filter(w => !w.counselor_comment).length
}

// 重置筛选
const resetFilter = () => {
  filter.search = ''
  filter.riskLevel = ''
  filter.commentStatus = ''
  loadWarnings()
}

// 生成评语
const generateComment = async (row) => {
  row.generating = true
  try {
    const res = await generateCounselorComment({
      student_id: row.student_id,
      warning_id: row.id
    })
    if (res.code === 200) {
      ElMessage.success('生成成功')
      // 更新当前行数据
      row.counselor_comment = res.data.summary
      row.ai_generated_at = new Date().toISOString()
      // 打开详情查看
      viewDetail(row)
      calculateStats()
    } else {
      ElMessage.error(res.message || '生成失败')
    }
  } catch (error) {
    console.error('生成评语失败:', error)
    ElMessage.error('生成失败: ' + error.message)
  } finally {
    row.generating = false
  }
}

// 查看详情
const viewDetail = async (row) => {
  currentWarning.value = row
  try {
    const res = await getStoredComment(row.id)
    if (res.code === 200) {
      currentComment.value = {
        ...res.data,
        summary: res.data.counselor_comment?.summary,
        analysis: res.data.counselor_comment?.analysis,
        suggestions: res.data.counselor_comment?.suggestions,
        action_plan: res.data.counselor_comment?.action_plan,
        talking_points: res.data.counselor_comment?.talking_points,
        student_phone: res.data.student_phone
      }
      dialogVisible.value = true
    }
  } catch (error) {
    console.error('获取评语详情失败:', error)
    ElMessage.error('获取详情失败')
  }
}

// 重新生成
const regenerateComment = async () => {
  if (!currentWarning.value) return
  await generateComment(currentWarning.value)
}

// 应用短信模板
const applyTemplate = (template) => {
  const studentName = currentComment.value?.student_name || '同学'
  const templates = {
    standard: `【学业预警】${studentName}您好，辅导员查看了您的学习情况，有一些建议想和您分享。请登录系统查看详情。`,
    urgent: `【学业预警】${studentName}您好，您的学习状态需要关注，辅导员希望尽快与您沟通。请登录系统查看详情。`,
    care: `【学业预警】${studentName}您好，辅导员注意到您最近的学习情况，想给您一些鼓励和建议。请登录系统查看详情。`
  }
  smsForm.message = templates[template.value]
}

// 发送短信
const sendSMS = async () => {
  if (!smsForm.phone) {
    ElMessage.warning('请输入手机号')
    return
  }
  if (!smsForm.message) {
    ElMessage.warning('请输入短信内容')
    return
  }

  sending.value = true
  try {
    const res = await sendSMSNotification({
      warning_id: currentWarning.value.id,
      phone: smsForm.phone,
      message: smsForm.message
    })
    if (res.code === 200) {
      ElMessage.success('发送成功')
      showSMSEditor.value = false
      // 更新当前行状态
      currentWarning.value.sms_sent = true
      currentWarning.value.sms_sent_at = new Date().toISOString()
      calculateStats()
    } else {
      ElMessage.error(res.message || '发送失败')
    }
  } catch (error) {
    console.error('发送短信失败:', error)
    ElMessage.error('发送失败: ' + error.message)
  } finally {
    sending.value = false
  }
}

// 辅助函数
const getScoreType = (score) => {
  if (score >= 80) return 'success'
  if (score >= 60) return 'warning'
  return 'danger'
}

const formatTime = (time) => {
  if (!time) return '-'
  return new Date(time).toLocaleString('zh-CN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(loadWarnings)
</script>

<style scoped lang="scss">
.ai-comment-page {
  padding: 20px;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
}

// 统计卡片
.stats-row {
  margin: 20px 0;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 16px;

  .stat-icon {
    width: 48px;
    height: 48px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    color: #fff;
    margin-right: 16px;

    &.blue { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    &.green { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }
    &.orange { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
    &.purple { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
  }

  .stat-info {
    .stat-value {
      font-size: 24px;
      font-weight: 700;
      color: #303133;
    }
    .stat-label {
      font-size: 13px;
      color: #909399;
      margin-top: 4px;
    }
  }
}

// 筛选卡片
.filter-card {
  margin-bottom: 20px;
}

// 列表卡片
.list-card {
  .student-cell {
    display: flex;
    align-items: center;
    gap: 10px;

    .student-info {
      .name {
        font-weight: 500;
        color: #303133;
      }
      .no {
        font-size: 12px;
        color: #909399;
      }
    }
  }
}

// 分页
.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

// 评语详情
.comment-detail {
  .student-header {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 16px;

    .student-info {
      flex: 1;
      h3 {
        margin: 0;
        font-size: 18px;
      }
      p {
        margin: 4px 0 0;
        font-size: 13px;
        color: #909399;
      }
    }
  }

  .comment-content {
    section {
      margin-bottom: 20px;

      h4 {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 14px;
        color: #606266;
        margin: 0 0 10px;
        padding-bottom: 8px;
        border-bottom: 1px dashed #e4e7ed;
      }

      p, li {
        font-size: 14px;
        line-height: 1.8;
        color: #303133;
      }

      .summary {
        font-size: 15px;
        font-weight: 500;
        color: #409eff;
      }

      ol {
        padding-left: 20px;
        margin: 0;

        li {
          margin-bottom: 6px;
        }
      }
    }

    .talking-section {
      .talking-card {
        background: #f0f9ff;
        border-color: #409eff;

        :deep(.el-card__body) {
          padding: 16px;
          font-style: italic;
          color: #1a1a1a;
        }
      }
    }
  }

  .comment-actions {
    display: flex;
    justify-content: center;
    gap: 16px;
    margin-top: 24px;
    padding-top: 20px;
    border-top: 1px solid #e4e7ed;
  }
}

// 短信表单
.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.quick-templates {
  margin-top: 16px;

  .label {
    font-size: 13px;
    color: #606266;
    margin-right: 10px;
  }

  .template-tag {
    margin-right: 8px;
    cursor: pointer;

    &:hover {
      background: #409eff;
      color: #fff;
    }
  }
}
</style>
