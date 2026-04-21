<template>
  <div class="warnings-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <h1>预警管理</h1>
        <p>管理学生的学业预警记录，进行干预和跟踪</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="refreshData" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
        <el-button type="success" @click="exportData">
          <el-icon><Download /></el-icon>
          导出
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card danger" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon"><el-icon :size="28"><Warning /></el-icon></div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.activeHigh }}</div>
              <div class="stat-label">待处理高危</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card warning" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon"><el-icon :size="28"><Bell /></el-icon></div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.activeMedium }}</div>
              <div class="stat-label">待处理中等</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card success" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon"><el-icon :size="28"><CircleCheck /></el-icon></div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.resolvedThisMonth }}</div>
              <div class="stat-label">本月已解决</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card info" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon"><el-icon :size="28"><MagicStick /></el-icon></div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.aiGenerated }}</div>
              <div class="stat-label">AI评语已生成</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 主内容区：左右布局 -->
    <el-row :gutter="20" class="main-content-row">
      <!-- 左侧：预警列表 -->
      <el-col :span="14">
        <el-card class="warnings-table-card" shadow="never" v-loading="loading">
          <template #header>
            <div class="card-header">
              <span class="card-title">预警学生列表</span>
              <el-tag v-if="selectedRow" type="primary">已选择: {{ selectedRow.student?.name }}</el-tag>
            </div>
          </template>

          <!-- 筛选栏 -->
          <div class="filter-row">
            <el-select v-model="filters.risk_level" placeholder="风险等级" clearable @change="handleFilterChange" size="small">
              <el-option label="高危" value="high" />
              <el-option label="中等" value="medium" />
              <el-option label="低危" value="low" />
            </el-select>
            <el-select v-model="filters.status" placeholder="状态" clearable @change="handleFilterChange" size="small">
              <el-option label="待处理" value="active" />
              <el-option label="已解决" value="resolved" />
            </el-select>
            <el-input v-model="filters.search" placeholder="姓名/学号/课程" clearable size="small" style="width: 150px" @change="handleFilterChange">
              <template #prefix><el-icon><Search /></el-icon></template>
            </el-input>
            <el-button size="small" @click="resetFilters">重置</el-button>
          </div>

          <!-- 数据信息 -->
          <div v-if="!loading" style="padding: 10px; background: #f0f0f0; margin-bottom: 10px; font-size: 12px;">
            预警学生: {{ allStudentWarnings.length }} 人, 总预警: {{ warnings.length }} 条, 当前页: {{ pagination.page }}
          </div>

          <!-- 预警列表 -->
          <el-table
            :data="studentWarnings"
            stripe
            highlight-current-row
            row-key="student.id"
            @current-change="handleStudentSelect"
            v-loading="loading"
            style="margin-top: 16px; min-height: 200px;"
            size="small"
            empty-text="暂无预警数据"
            expandable
          >
            <el-table-column type="expand">
              <template #default="{ row }">
                <div class="expand-content">
                  <el-table :data="row.warnings" size="small" :border="true" style="width: 100%">
                    <el-table-column label="课程" min-width="120">
                      <template #default="{ row: w }">
                        <span>{{ w.course?.name }}</span>
                      </template>
                    </el-table-column>
                    <el-table-column label="风险" width="60">
                      <template #default="{ row: w }">
                        <el-tag :type="getRiskTagType(w.risk_level)" size="small" effect="dark">
                          {{ getRiskLabel(w.risk_level) }}
                        </el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column label="得分" width="70">
                      <template #default="{ row: w }">
                        <span :class="getScoreClass(w.composite_score)">{{ w.composite_score }}</span>
                      </template>
                    </el-table-column>
                    <el-table-column label="操作" width="80">
                      <template #default="{ row: w }">
                        <el-button type="primary" link size="small" @click="addIntervention(w)">
                          干预
                        </el-button>
                      </template>
                    </el-table-column>
                  </el-table>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="学生" width="100">
              <template #default="{ row }">
                <div class="student-cell">
                  <el-avatar :size="28" :style="{ background: getAvatarColor(row.student?.name) }">{{ row.student?.name?.charAt(0) }}</el-avatar>
                  <span>{{ row.student?.name }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="学号" width="100">
              <template #default="{ row }">
                <span>{{ row.student?.student_no }}</span>
              </template>
            </el-table-column>
            <el-table-column label="预警课程数" width="90">
              <template #default="{ row }">
                <el-tag
                  :type="row.warnings.length > 2 ? 'danger' : row.warnings.length > 1 ? 'warning' : 'info'"
                  size="small"
                >
                  {{ row.warnings.length }} 门
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="风险分布" min-width="120">
              <template #default="{ row }">
                <div class="risk-distribution">
                  <el-tag v-if="row.risk_count?.high > 0" type="danger" size="small" effect="dark" class="risk-tag">
                    高 {{ row.risk_count.high }}
                  </el-tag>
                  <el-tag v-if="row.risk_count?.medium > 0" type="warning" size="small" effect="dark" class="risk-tag">
                    中 {{ row.risk_count.medium }}
                  </el-tag>
                  <el-tag v-if="row.risk_count?.low > 0" type="info" size="small" effect="dark" class="risk-tag">
                    低 {{ row.risk_count.low }}
                  </el-tag>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="最高风险" width="80">
              <template #default="{ row }">
                <el-tag :type="getRiskTagType(row.highest_risk)" size="small" effect="dark">
                  {{ getRiskLabel(row.highest_risk) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="平均得分" width="80" sortable :sort-method="(a, b) => (a.avg_score || 0) - (b.avg_score || 0)">
              <template #default="{ row }">
                <span :class="getScoreClass(row.avg_score)">{{ row.avg_score ?? '-' }}</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="70" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click.stop="addInterventionForStudent(row)">
                  <el-icon><FirstAidKit /></el-icon>
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <div class="pagination-wrapper">
            <el-pagination
              v-model:current-page="pagination.page"
              v-model:page-size="pagination.pageSize"
              :total="pagination.total"
              :page-sizes="[10, 20, 50]"
              layout="total, prev, pager, next"
              @size-change="handleSizeChange"
              @current-change="handlePageChange"
              small
            />
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：AI智能助手面板 -->
      <el-col :span="10">
        <div class="ai-panel">
          <!-- AI评语卡片 -->
          <el-card class="ai-comment-card" shadow="hover" v-loading="aiLoading">
            <template #header>
              <div class="ai-header">
                <div class="ai-title">
                  <el-icon :size="20" color="#7c3aed"><MagicStick /></el-icon>
                  <span>AI智能评语</span>
                </div>
                <el-button
                  v-if="selectedRow"
                  type="primary"
                  size="small"
                  :loading="generatingAI"
                  @click="generateAIComment"
                  :disabled="!selectedRow"
                >
                  <el-icon><Refresh /></el-icon>
                  重新生成
                </el-button>
              </div>
            </template>

            <div v-if="!selectedRow" class="empty-state">
              <el-empty description="请选择左侧预警学生查看AI评语">
                <template #image>
                  <el-icon :size="60" color="#cbd5e1"><User /></el-icon>
                </template>
              </el-empty>
            </div>

            <div v-else-if="!aiComment.summary" class="empty-state">
              <el-empty description="暂无AI评语，点击生成">
                <template #image>
                  <el-icon :size="60" color="#7c3aed"><MagicStick /></el-icon>
                </template>
                <el-button type="primary" @click="generateAIComment" :loading="generatingAI">
                  <el-icon><MagicStick /></el-icon>
                  生成AI评语
                </el-button>
              </el-empty>
            </div>

            <div v-else class="ai-content">
              <!-- 总体评价 -->
              <div class="ai-section">
                <h4 class="section-title">
                  <el-icon><Document /></el-icon>
                  总体评价
                </h4>
                <p class="section-content">{{ aiComment.summary }}</p>
              </div>

              <!-- 问题分析 -->
              <div class="ai-section">
                <h4 class="section-title">
                  <el-icon><TrendCharts /></el-icon>
                  问题分析
                </h4>
                <p class="section-content">{{ aiComment.analysis }}</p>
              </div>

              <!-- 干预建议 -->
              <div class="ai-section">
                <h4 class="section-title">
                  <el-icon><List /></el-icon>
                  干预建议
                </h4>
                <ul class="suggestion-list">
                  <li v-for="(item, index) in aiComment.suggestions" :key="index">
                    <el-icon color="#10b981"><CircleCheck /></el-icon>
                    <span>{{ item }}</span>
                  </li>
                </ul>
              </div>

              <!-- 行动计划 -->
              <div class="ai-section">
                <h4 class="section-title">
                  <el-icon><Calendar /></el-icon>
                  行动计划
                </h4>
                <p class="section-content">{{ aiComment.action_plan }}</p>
              </div>

              <!-- 沟通话术 -->
              <div class="ai-section talking-points">
                <h4 class="section-title">
                  <el-icon><ChatDotRound /></el-icon>
                  沟通话术
                </h4>
                <div class="talking-box">
                  <p>{{ aiComment.talking_points }}</p>
                  <el-button
                    type="primary"
                    link
                    size="small"
                    @click="copyTalkingPoints"
                    class="copy-btn"
                  >
                    <el-icon><CopyDocument /></el-icon>
                    复制话术
                  </el-button>
                </div>
              </div>

              <!-- 操作按钮 -->
              <div class="ai-actions">
                <el-button type="primary" @click="showSMSDialog" :disabled="smsSent">
                  <el-icon><Message /></el-icon>
                  {{ smsSent ? '已发送短信' : '发送短信通知' }}
                </el-button>
                <el-button type="success" @click="addIntervention(selectedRow)">
                  <el-icon><FirstAidKit /></el-icon>
                  添加干预记录
                </el-button>
              </div>

              <div v-if="aiComment.generated_at" class="ai-meta">
                生成时间: {{ aiComment.generated_at }}
              </div>
            </div>
          </el-card>

          <!-- 快捷操作卡片 -->
          <el-card class="quick-actions-card" shadow="hover" v-if="selectedRow">
            <template #header>
              <span class="card-title">学生信息</span>
            </template>
            <div class="student-info">
              <div class="info-item">
                <span class="info-label">姓名：</span>
                <span class="info-value">{{ selectedRow.student?.name }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">学号：</span>
                <span class="info-value">{{ selectedRow.student?.student_no }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">班级：</span>
                <span class="info-value">{{ selectedRow.student?.class_name || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">预警课程数：</span>
                <span class="info-value">{{ selectedRow.warnings?.length || 0 }} 门</span>
              </div>
              <div class="info-item">
                <span class="info-label">最高风险：</span>
                <el-tag :type="getRiskTagType(selectedRow.highest_risk)" size="small" effect="dark">
                  {{ getRiskLabel(selectedRow.highest_risk) }}
                </el-tag>
              </div>
              <el-divider />
              <div class="info-item">
                <span class="info-label">出勤率：</span>
                <span class="info-value" :class="getScoreClass(selectedRow.attendance_score)">
                  {{ selectedRow.attendance_score }}%
                </span>
              </div>
              <div class="info-item">
                <span class="info-label">学习进度：</span>
                <span class="info-value" :class="getScoreClass(selectedRow.progress_score)">
                  {{ selectedRow.progress_score }}%
                </span>
              </div>
              <div class="info-item">
                <span class="info-label">作业成绩：</span>
                <span class="info-value" :class="getScoreClass(selectedRow.homework_score)">
                  {{ selectedRow.homework_score }}
                </span>
              </div>
              <div class="info-item">
                <span class="info-label">考试成绩：</span>
                <span class="info-value" :class="getScoreClass(selectedRow.exam_score)">
                  {{ selectedRow.exam_score }}
                </span>
              </div>
            </div>
          </el-card>
        </div>
      </el-col>
    </el-row>

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailDialogVisible" title="预警详情" width="700px">
      <div v-if="selectedWarning" class="warning-detail">
        <div class="detail-header">
          <el-avatar :size="64" :style="{ background: getAvatarColor(selectedWarning.student_name) }">
            {{ selectedWarning.student_name?.charAt(0) }}
          </el-avatar>
          <div class="detail-info">
            <h3>{{ selectedWarning.student_name }}</h3>
            <p>学号：{{ selectedWarning.student_no }} | 班级：{{ selectedWarning.class_name || '-' }}</p>
          </div>
          <div class="detail-tags">
            <el-tag :type="getRiskTagType(selectedWarning.risk_level)" effect="dark" size="large">
              {{ getRiskLabel(selectedWarning.risk_level) }}
            </el-tag>
            <el-tag :type="selectedWarning.status === 'active' ? 'danger' : 'success'" size="large">
              {{ selectedWarning.status === 'active' ? '待处理' : '已解决' }}
            </el-tag>
          </div>
        </div>

        <el-divider />

        <div class="detail-scores">
          <h4><el-icon><TrendCharts /></el-icon> 得分详情</h4>
          <el-row :gutter="16">
            <el-col :span="6">
              <div class="score-item">
                <div class="score-label">综合得分</div>
                <div class="score-value" :class="getScoreClass(selectedWarning.composite_score)">
                  {{ selectedWarning.composite_score }}
                </div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="score-item">
                <div class="score-label">出勤率</div>
                <div class="score-value">{{ selectedWarning.attendance_score }}%</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="score-item">
                <div class="score-label">视频进度</div>
                <div class="score-value">{{ selectedWarning.progress_score }}%</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="score-item">
                <div class="score-label">作业成绩</div>
                <div class="score-value">{{ selectedWarning.homework_score }}</div>
              </div>
            </el-col>
          </el-row>
        </div>

        <el-divider />

        <div class="detail-suggestion" v-if="selectedWarning.suggestion">
          <h4><el-icon><InfoFilled /></el-icon> 系统建议</h4>
          <p>{{ selectedWarning.suggestion }}</p>
        </div>

        <div class="detail-actions">
          <el-button type="primary" @click="addIntervention(selectedWarning)">
            <el-icon><FirstAidKit /></el-icon>添加干预
          </el-button>
          <el-button v-if="selectedWarning.status === 'active'" type="success" @click="resolveWarning(selectedWarning)">
            <el-icon><CircleCheck /></el-icon>标记解决
          </el-button>
        </div>
      </div>
    </el-dialog>

    <!-- 发送短信弹窗 -->
    <el-dialog v-model="smsDialogVisible" title="发送短信通知" width="500px">
      <el-form :model="smsForm" label-width="80px">
        <el-form-item label="接收人">
          <span>{{ selectedRow?.student?.name }} ({{ selectedRow?.student?.student_no }})</span>
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="smsForm.phone" placeholder="请输入学生手机号" />
        </el-form-item>
        <el-form-item label="短信内容">
          <el-input
            v-model="smsForm.message"
            type="textarea"
            :rows="4"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="smsDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="sendSMS" :loading="sendingSMS">
          <el-icon><Message /></el-icon>
          发送
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch, computed } from 'vue'
import {
  Warning, Bell, CircleCheck, Refresh, Download, Search,
  View, FirstAidKit, TrendCharts, MagicStick, Document,
  List, Calendar, ChatDotRound, Message, CopyDocument,
  InfoFilled, User
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import {
  getWarningRecordsByStudent, resolveWarning as apiResolveWarning, getWarningStats,
  generateCounselorComment, getStoredComment, sendSMSNotification
} from '@/api/counselor'

const router = useRouter()

// 状态
const loading = ref(false)
const aiLoading = ref(false)
const generatingAI = ref(false)
const detailDialogVisible = ref(false)
const selectedWarning = ref(null)
const selectedRow = ref(null)
const smsDialogVisible = ref(false)
const sendingSMS = ref(false)
const smsSent = ref(false)

// 统计数据
const stats = reactive({
  activeHigh: 0,
  activeMedium: 0,
  resolvedThisMonth: 0,
  aiGenerated: 0
})

// 筛选条件
const filters = reactive({
  risk_level: '',
  status: 'active',
  search: ''
})

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

// 预警列表（原始数据，保留用于展开行显示）
const warnings = ref([])

// 按学生汇总的预警列表（来自后端API，已排序）
const allStudentWarnings = ref([])

// 分页后的学生预警列表
const studentWarnings = computed(() => {
  const start = (pagination.page - 1) * pagination.pageSize
  const end = start + pagination.pageSize
  return allStudentWarnings.value.slice(start, end)
})

// AI评语数据
const aiComment = reactive({
  summary: '',
  analysis: '',
  suggestions: [],
  action_plan: '',
  talking_points: '',
  generated_at: ''
})

// 短信表单
const smsForm = reactive({
  phone: '',
  message: ''
})

// 加载预警列表数据（使用按学生汇总的API）
const loadData = async () => {
  loading.value = true
  try {
    console.log('正在加载按学生汇总的预警数据...')
    const res = await getWarningRecordsByStudent()
    console.log('API响应:', res)
    if (res.code === 200) {
      // 直接使用后端返回的按学生汇总数据（已按风险排序）
      const studentList = res.data?.students || []
      allStudentWarnings.value = studentList
      warnings.value = studentList.flatMap(s => s.warnings || [])

      // 更新分页总数
      pagination.total = studentList.length
      console.log('学生预警汇总数据:', studentList)
      console.log('总数:', pagination.total)

      // 如果有数据且未选择，默认选择第一条
      if (studentList.length > 0 && !selectedRow.value) {
        // 等待响应式更新后再选择
        setTimeout(() => {
          const firstPage = studentWarnings.value
          if (firstPage.length > 0) {
            handleStudentSelect(firstPage[0])
          }
        }, 0)
      }
    } else {
      console.error('API返回错误:', res)
      ElMessage.error(res.message || '加载数据失败')
    }
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 加载统计数据
const loadStats = async () => {
  try {
    const res = await getWarningStats()
    if (res.code === 200) {
      const data = res.data || {}
      stats.activeHigh = data.high_risk_count || 0
      stats.activeMedium = data.medium_risk_count || 0
      stats.resolvedThisMonth = data.resolved_count || 0
      // AI生成数量需要额外统计，这里用模拟
      stats.aiGenerated = Math.floor((data.active_count || 0) * 0.3)
    }
  } catch (error) {
    console.error('加载统计失败:', error)
  }
}

// 加载AI评语
const loadAIComment = async (warningId) => {
  if (!warningId) return

  aiLoading.value = true
  try {
    const res = await getStoredComment(warningId)
    if (res.code === 200) {
      const data = res.data || {}
      const counselorComment = data.counselor_comment || {}

      aiComment.summary = counselorComment.summary || ''
      aiComment.analysis = counselorComment.analysis || ''
      aiComment.suggestions = counselorComment.suggestions || []
      aiComment.action_plan = counselorComment.action_plan || ''
      aiComment.talking_points = counselorComment.talking_points || ''
      aiComment.generated_at = data.generated_at || ''
      smsSent.value = data.sms_sent || false
    }
  } catch (error) {
    // 可能没有存储的评语，清空
    aiComment.summary = ''
    aiComment.analysis = ''
    aiComment.suggestions = []
    aiComment.action_plan = ''
    aiComment.talking_points = ''
    aiComment.generated_at = ''
  } finally {
    aiLoading.value = false
  }
}

// 生成AI评语
const generateAIComment = async () => {
  if (!selectedRow.value) {
    ElMessage.warning('请先选择一个预警学生')
    return
  }

  generatingAI.value = true
  try {
    // 使用第一个预警的ID
    const warningId = selectedRow.value.warnings?.[0]?.id
    const res = await generateCounselorComment({
      student_id: selectedRow.value.student?.id,
      warning_id: warningId
    })

    if (res.code === 200) {
      const data = res.data || {}
      aiComment.summary = data.summary || ''
      aiComment.analysis = data.analysis || ''
      aiComment.suggestions = data.suggestions || []
      aiComment.action_plan = data.action_plan || ''
      aiComment.talking_points = data.talking_points || ''
      aiComment.generated_at = new Date().toLocaleString('zh-CN')
      smsSent.value = false
      ElMessage.success('AI评语生成成功')
    }
  } catch (error) {
    console.error('生成AI评语失败:', error)
    ElMessage.error('生成AI评语失败，请稍后重试')
  } finally {
    generatingAI.value = false
  }
}

// 选择学生行变化
const handleStudentSelect = (row) => {
  selectedRow.value = row
  if (row && row.warnings && row.warnings.length > 0) {
    // 使用第一个预警的ID来加载AI评语
    loadAIComment(row.warnings[0].id)
  }
}

// 筛选变化
const handleFilterChange = () => {
  pagination.page = 1
  loadData()
}

// 重置筛选
const resetFilters = () => {
  filters.risk_level = ''
  filters.status = 'active'
  filters.search = ''
  pagination.page = 1
  loadData()
}

// 分页变化
const handleSizeChange = (val) => {
  pagination.pageSize = val
  loadData()
}

const handlePageChange = (val) => {
  pagination.page = val
  loadData()
}

// 添加干预
const addIntervention = (row) => {
  router.push({
    path: '/counselor/interventions',
    query: {
      student_id: row.student?.id,
      warning_id: row.id
    }
  })
}

// 为学生添加干预（选择最高风险的预警）
const addInterventionForStudent = (studentRow) => {
  // 找到最高风险的预警
  const highestRiskWarning = studentRow.warnings.reduce((highest, current) => {
    const riskOrder = { high: 3, medium: 2, low: 1, normal: 0 }
    return riskOrder[current.risk_level] > riskOrder[highest.risk_level] ? current : highest
  }, studentRow.warnings[0])

  router.push({
    path: '/counselor/interventions',
    query: {
      student_id: studentRow.student?.id,
      warning_id: highestRiskWarning?.id
    }
  })
}

// 解决预警
const resolveWarning = async (row) => {
  try {
    const { value } = await ElMessageBox.prompt('请输入解决说明', '标记预警为已解决', {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      inputPlaceholder: '请输入解决说明（可选）'
    })
    const res = await apiResolveWarning(row.id, { resolve_note: value })
    if (res.code === 200) {
      ElMessage.success('预警已标记为已解决')
      loadData()
      if (detailDialogVisible.value) detailDialogVisible.value = false
    }
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('操作失败')
  }
}

// 刷新数据
const refreshData = () => {
  loadData()
  loadStats()
  ElMessage.success('数据已刷新')
}

// 导出数据
const exportData = () => {
  // 导出学生汇总数据
  const headers = ['学生姓名', '学号', '班级', '预警课程数', '高危', '中等', '低危', '最高风险', '平均得分']
  const rows = allStudentWarnings.value.map(s => [
    s.student?.name,
    s.student?.student_no,
    s.student?.class_name || '-',
    s.warnings?.length || 0,
    s.risk_count?.high || 0,
    s.risk_count?.medium || 0,
    s.risk_count?.low || 0,
    getRiskLabel(s.highest_risk),
    s.avg_score ?? '-'
  ])

  const csvContent = [headers, ...rows].map(row => row.join(',')).join('\n')
  const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `预警列表_${new Date().toLocaleDateString('zh-CN')}.csv`
  link.click()
  ElMessage.success('导出成功')
}

// 显示短信弹窗
const showSMSDialog = () => {
  if (!aiComment.talking_points) {
    ElMessage.warning('请先生成AI评语')
    return
  }

  // 默认短信内容
  const summary = aiComment.summary?.substring(0, 30) || '辅导员查看了你的学习情况'
  smsForm.message = `【学业预警】${selectedRow.value.student?.name}同学您好，${summary}。请登录系统查看详情。`
  smsDialogVisible.value = true
}

// 发送短信
const sendSMS = async () => {
  if (!smsForm.phone) {
    ElMessage.warning('请输入手机号')
    return
  }

  const phoneRegex = /^1[3-9]\d{9}$/
  if (!phoneRegex.test(smsForm.phone)) {
    ElMessage.warning('手机号格式不正确')
    return
  }

  sendingSMS.value = true
  try {
    const res = await sendSMSNotification({
      warning_id: selectedRow.value.warnings?.[0]?.id,
      phone: smsForm.phone,
      message: smsForm.message
    })

    if (res.code === 200) {
      ElMessage.success('短信发送成功')
      smsSent.value = true
      smsDialogVisible.value = false
    } else {
      ElMessage.error(res.message || '发送失败')
    }
  } catch (error) {
    console.error('发送短信失败:', error)
    ElMessage.error('发送失败，请稍后重试')
  } finally {
    sendingSMS.value = false
  }
}

// 复制话术
const copyTalkingPoints = () => {
  if (!aiComment.talking_points) return

  navigator.clipboard.writeText(aiComment.talking_points).then(() => {
    ElMessage.success('话术已复制到剪贴板')
  }).catch(() => {
    // 降级方案
    const textarea = document.createElement('textarea')
    textarea.value = aiComment.talking_points
    document.body.appendChild(textarea)
    textarea.select()
    document.execCommand('copy')
    document.body.removeChild(textarea)
    ElMessage.success('话术已复制到剪贴板')
  })
}

// 工具函数
const getAvatarColor = (name) => {
  const colors = ['#667eea', '#f093fb', '#4facfe', '#43e97b', '#fa709a', '#30cfd0']
  let hash = 0
  for (let i = 0; i < name?.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash)
  return colors[Math.abs(hash) % colors.length]
}

const getRiskTagType = (level) => {
  const types = { high: 'danger', medium: 'warning', low: 'info', normal: 'success' }
  return types[level] || 'info'
}

const getRiskLabel = (level) => {
  const labels = { high: '高', medium: '中', low: '低', normal: '正常' }
  return labels[level] || level
}

const getScoreClass = (score) => {
  if (score < 60) return 'score-danger'
  if (score < 75) return 'score-warning'
  return 'score-success'
}

onMounted(() => {
  loadData()
  loadStats()
})
</script>

<style scoped>
.warnings-page {
  max-width: 1600px;
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
}

.header-actions {
  display: flex;
  gap: 12px;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card :deep(.el-card__body) {
  padding: 0;
}

.stat-content {
  display: flex;
  align-items: center;
  padding: 16px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-right: 12px;
}

.stat-card.danger .stat-icon { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
.stat-card.warning .stat-icon { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }
.stat-card.success .stat-icon { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }
.stat-card.info .stat-icon { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #1f2937;
}

.stat-label {
  font-size: 12px;
  color: #6b7280;
  margin-top: 2px;
}

/* 主内容区 */
.main-content-row {
  margin-top: 0;
}

/* 左侧列表 */
.warnings-table-card {
  border-radius: 12px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-weight: 600;
  font-size: 16px;
  color: #374151;
}

.filter-row {
  display: flex;
  gap: 10px;
  margin-bottom: 8px;
}

.student-cell {
  display: flex;
  align-items: center;
  gap: 6px;
}

.score-danger { color: #ef4444; font-weight: 600; }
.score-warning { color: #f59e0b; font-weight: 600; }
.score-success { color: #10b981; font-weight: 600; }

/* 展开行内容样式 */
.expand-content {
  padding: 10px 20px;
  background: #f8fafc;
}

/* 风险分布标签 */
.risk-distribution {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.risk-tag {
  font-size: 11px;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid #e5e7eb;
}

/* 右侧AI面板 */
.ai-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.ai-comment-card {
  border-radius: 12px;
}

.ai-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.ai-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 16px;
  color: #374151;
}

.empty-state {
  padding: 40px 20px;
}

.ai-content {
  padding: 4px;
}

.ai-section {
  margin-bottom: 16px;
}

.ai-section:last-child {
  margin-bottom: 0;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 8px;
}

.section-content {
  color: #4b5563;
  line-height: 1.6;
  font-size: 13px;
  padding: 10px 12px;
  background: #f9fafb;
  border-radius: 8px;
}

.suggestion-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.suggestion-list li {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 8px 0;
  border-bottom: 1px solid #f3f4f6;
  font-size: 13px;
  color: #4b5563;
}

.suggestion-list li:last-child {
  border-bottom: none;
}

.talking-points {
  background: #f0f9ff;
  border-radius: 8px;
  padding: 12px;
}

.talking-box {
  position: relative;
}

.talking-box p {
  color: #0369a1;
  line-height: 1.7;
  font-size: 13px;
  padding-right: 60px;
}

.copy-btn {
  position: absolute;
  top: 0;
  right: 0;
}

.ai-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #e5e7eb;
}

.ai-meta {
  margin-top: 12px;
  font-size: 11px;
  color: #9ca3af;
  text-align: right;
}

/* 快捷操作卡片 */
.quick-actions-card {
  border-radius: 12px;
}

.student-info {
  font-size: 13px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
}

.info-label {
  color: #6b7280;
}

.info-value {
  color: #1f2937;
  font-weight: 500;
}

/* 详情弹窗 */
.warning-detail {
  padding: 0 10px;
}

.detail-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.detail-info h3 {
  margin: 0 0 8px 0;
  font-size: 20px;
  color: #1f2937;
}

.detail-info p {
  margin: 0;
  color: #6b7280;
  font-size: 14px;
}

.detail-tags {
  margin-left: auto;
  display: flex;
  gap: 8px;
}

.detail-scores {
  margin: 20px 0;
}

.detail-scores h4 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  color: #374151;
}

.score-item {
  text-align: center;
  padding: 14px;
  background: #f9fafb;
  border-radius: 8px;
}

.score-label {
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 6px;
}

.score-value {
  font-size: 20px;
  font-weight: 700;
  color: #1f2937;
}

.detail-suggestion {
  margin: 20px 0;
}

.detail-suggestion h4 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  color: #374151;
}

.detail-suggestion p {
  color: #6b7280;
  line-height: 1.6;
  padding: 12px;
  background: #f0f9ff;
  border-radius: 8px;
  border-left: 4px solid #3b82f6;
}

.detail-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 24px;
}
</style>
