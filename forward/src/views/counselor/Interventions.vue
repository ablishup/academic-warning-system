<template>
  <div class="interventions-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <h1>干预记录</h1>
        <p>管理学生干预措施，跟踪干预效果</p>
      </div>
      <div class="header-actions">
        <el-button v-if="selectedStudentId" @click="clearStudentFilter">
          <el-icon><List /></el-icon>
          查看全部
        </el-button>
        <el-button type="primary" @click="openAddDialog">
          <el-icon><Plus /></el-icon>
          新增干预
        </el-button>
      </div>
    </div>

    <!-- 学生信息卡片（从预警页面跳转时显示） -->
    <el-card v-if="selectedStudentInfo" class="student-info-card" shadow="hover">
      <div class="student-header">
        <div class="student-profile">
          <el-avatar :size="56" :style="{ background: getAvatarColor(selectedStudentInfo.student?.name) }">
            {{ selectedStudentInfo.student?.name?.charAt(0) }}
          </el-avatar>
          <div class="profile-text">
            <h3>{{ selectedStudentInfo.student?.name }} <span class="student-no">{{ selectedStudentInfo.student?.student_no }}</span></h3>
            <div class="student-tags">
              <el-tag v-if="selectedStudentInfo.warnings?.length > 0" :type="getRiskTagType(selectedStudentInfo.highest_risk)" effect="dark" size="small">
                {{ getRiskLabel(selectedStudentInfo.highest_risk) }}
              </el-tag>
              <el-tag type="info" size="small">{{ selectedStudentInfo.warnings?.length || 0 }} 门课程预警</el-tag>
              <el-tag v-if="selectedStudentInfo.avg_score" :type="getScoreTagType(selectedStudentInfo.avg_score)" size="small">
                平均分 {{ selectedStudentInfo.avg_score }}
              </el-tag>
            </div>
          </div>
        </div>
        <div class="student-actions">
          <el-button type="primary" link @click="goToWarnings">
            <el-icon><Warning /></el-icon>
            查看预警详情
          </el-button>
        </div>
      </div>

      <!-- 预警课程列表 -->
      <div v-if="selectedStudentInfo.warnings?.length > 0" class="warning-courses">
        <div class="section-title">预警课程</div>
        <div class="course-tags">
          <el-tag
            v-for="w in selectedStudentInfo.warnings"
            :key="w.id"
            :type="getRiskTagType(w.risk_level)"
            effect="plain"
            size="small"
            class="course-tag"
          >
            {{ w.course?.name }} - {{ w.composite_score }}分
          </el-tag>
        </div>
      </div>
    </el-card>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="8">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon blue">
            <el-icon :size="28"><FirstAidKit /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.total }}</div>
            <div class="stat-label">干预总数</div>
            <div class="stat-change">
              <span>本月新增 {{ stats.thisMonth }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon green">
            <el-icon :size="28"><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.effective }}</div>
            <div class="stat-label">有效干预</div>
            <div class="stat-change success">
              <span>有效率 {{ stats.effectivenessRate }}%</span>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon orange">
            <el-icon :size="28"><Timer /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.pending }}</div>
            <div class="stat-label">待评估</div>
            <div class="stat-change warning">
              <span>需及时跟进</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 筛选栏 -->
    <el-card class="filter-card" shadow="hover">
      <el-form :model="filterForm" inline>
        <el-form-item label="干预类型">
          <el-select v-model="filterForm.type" placeholder="全部类型" clearable>
            <el-option label="谈话辅导" value="talk" />
            <el-option label="学业帮扶" value="academic" />
            <el-option label="心理疏导" value="psychological" />
            <el-option label="家校联系" value="family" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="干预效果">
          <el-select v-model="filterForm.is_effective" placeholder="全部" clearable>
            <el-option label="有效" :value="true" />
            <el-option label="无效" :value="false" />
            <el-option label="待评估" :value="null" />
          </el-select>
        </el-form-item>
        <el-form-item label="学生搜索">
          <el-input
            v-model="filterForm.search"
            placeholder="姓名/学号"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleFilter">
            <el-icon><Search /></el-icon>
            筛选
          </el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 干预记录列表 -->
    <el-card class="interventions-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="card-title">
            <el-icon><FirstAidKit /></el-icon>
            干预记录列表
          </span>
          <div class="header-actions">
            <el-radio-group v-model="viewMode" size="small">
              <el-radio-button label="table">表格</el-radio-button>
              <el-radio-button label="timeline">时间线</el-radio-button>
            </el-radio-group>
          </div>
        </div>
      </template>

      <!-- 表格视图 -->
      <div v-if="viewMode === 'table'">
        <el-table :data="interventions" v-loading="loading" stripe>
          <el-table-column prop="student_name" label="学生姓名" width="100">
            <template #default="{ row }">
              <div class="student-name">
                <el-avatar :size="32" :style="{ background: getAvatarColor(row.student_name) }">
                  {{ row.student_name?.charAt(0) }}
                </el-avatar>
                <span>{{ row.student_name }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="student_no" label="学号" width="120" />
          <el-table-column prop="intervention_type" label="干预类型" width="120">
            <template #default="{ row }">
              <el-tag :type="getTypeTagType(row.intervention_type)" size="small">
                {{ getTypeLabel(row.intervention_type) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="content" label="干预内容" min-width="200" show-overflow-tooltip />
          <el-table-column prop="intervention_time" label="干预时间" width="150">
            <template #default="{ row }">
              {{ formatDate(row.intervention_time) }}
            </template>
          </el-table-column>
          <el-table-column prop="is_effective" label="干预效果" width="100">
            <template #default="{ row }">
              <el-tag
                :type="row.is_effective === true ? 'success' : row.is_effective === false ? 'danger' : 'info'"
                size="small"
              >
                {{ row.is_effective === true ? '有效' : row.is_effective === false ? '无效' : '待评估' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="viewDetail(row)">
                详情
              </el-button>
              <el-button type="success" link size="small" @click="evaluateIntervention(row)">
                {{ row.is_effective === null ? '评估' : '修改评估' }}
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="pagination-container">
          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.pageSize"
            :page-sizes="[10, 20, 50]"
            :total="pagination.total"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </div>

      <!-- 时间线视图 -->
      <div v-else class="timeline-view">
        <el-timeline>
          <el-timeline-item
            v-for="item in interventions"
            :key="item.id"
            :type="item.is_effective === true ? 'success' : item.is_effective === false ? 'danger' : 'warning'"
            :timestamp="formatDate(item.intervention_time)"
            placement="top"
          >
            <el-card class="timeline-card" shadow="hover">
              <div class="timeline-header">
                <div class="student-info">
                  <el-avatar :size="40" :style="{ background: getAvatarColor(item.student_name) }">
                    {{ item.student_name?.charAt(0) }}
                  </el-avatar>
                  <div class="info-text">
                    <div class="name">{{ item.student_name }}</div>
                    <div class="no">{{ item.student_no }}</div>
                  </div>
                </div>
                <el-tag :type="getTypeTagType(item.intervention_type)" size="small">
                  {{ getTypeLabel(item.intervention_type) }}
                </el-tag>
              </div>
              <div class="timeline-content">
                <p>{{ item.content }}</p>
              </div>
              <div class="timeline-footer">
                <el-tag
                  :type="item.is_effective === true ? 'success' : item.is_effective === false ? 'danger' : 'info'"
                  size="small"
                >
                  {{ item.is_effective === true ? '有效' : item.is_effective === false ? '无效' : '待评估' }}
                </el-tag>
                <el-button type="primary" link size="small" @click="viewDetail(item)">查看详情</el-button>
              </div>
            </el-card>
          </el-timeline-item>
        </el-timeline>
      </div>
    </el-card>

    <!-- 新增干预弹窗 -->
    <el-dialog v-model="addDialogVisible" title="新增干预记录" width="900px" class="intervention-dialog">
      <div class="dialog-content">
        <!-- 左侧：学生信息和表单 -->
        <div class="dialog-left">
          <!-- 学生信息卡片（只读） -->
          <div v-if="addForm.student_id && selectedStudentForDialog" class="student-info-display">
            <div class="student-profile-header">
              <el-avatar :size="56" :style="{ background: getAvatarColor(selectedStudentForDialog.name) }">
                {{ selectedStudentForDialog.name?.charAt(0) }}
              </el-avatar>
              <div class="profile-details">
                <div class="name">{{ selectedStudentForDialog.name }} <span class="student-no">{{ selectedStudentForDialog.student_no }}</span></div>
                <div class="class-info" v-if="selectedStudentForDialog.class_name">{{ selectedStudentForDialog.class_name }}</div>
                <div class="warning-count" v-if="dialogStudentWarnings.length > 0">
                  <el-tag :type="getRiskTagType(dialogHighestRisk)" effect="dark" size="small">
                    {{ getRiskLabel(dialogHighestRisk) }}
                  </el-tag>
                  <span class="count-text">{{ dialogStudentWarnings.length }} 门课程预警</span>
                </div>
                <div class="no-warning" v-else>
                  <el-tag type="success" size="small">暂无预警</el-tag>
                </div>
              </div>
            </div>

            <!-- 预警课程列表 -->
            <div v-if="dialogStudentWarnings.length > 0" class="warning-courses-list">
              <div class="section-title">选择要干预的课程（点击选择）：</div>
              <div class="course-cards">
                <div
                  v-for="w in dialogStudentWarnings"
                  :key="w.id"
                  :class="['course-card', { active: addForm.warning_id === w.id }]"
                  @click="selectWarningCourse(w.id)"
                >
                  <div class="course-header">
                    <span class="course-name">{{ w.course?.name || w.course_name }}</span>
                    <el-tag :type="getRiskTagType(w.risk_level)" effect="dark" size="small">
                      {{ getRiskLabel(w.risk_level) }}
                    </el-tag>
                  </div>
                  <div class="course-scores">
                    <span class="score-item">综合得分：<b :class="getScoreClass(w.composite_score)">{{ w.composite_score }}</b></span>
                    <span class="score-item" v-if="w.attendance_score !== undefined">出勤：{{ w.attendance_score }}%</span>
                  </div>
                </div>
              </div>
            </div>

            <el-divider />
          </div>

          <!-- 学生选择（仅在未指定学生时显示） -->
          <el-form v-if="!addForm.student_id" :model="addForm" label-width="100px" :rules="addRules" ref="addFormRef">
            <el-form-item label="学生" prop="student_id">
              <el-select
                v-model="addForm.student_id"
                filterable
                remote
                reserve-keyword
                placeholder="输入学号或姓名搜索"
                :remote-method="searchStudents"
                :loading="studentLoading"
                style="width: 100%"
                @change="onStudentChange"
              >
                <el-option
                  v-for="item in studentOptions"
                  :key="item.id"
                  :label="`${item.name} (${item.student_no})`"
                  :value="item.id"
                />
              </el-select>
            </el-form-item>
          </el-form>

          <!-- 干预表单 -->
          <el-form :model="addForm" label-width="100px" :rules="addRules" ref="addFormRef">
            <el-form-item label="干预类型" prop="intervention_type">
              <el-select v-model="addForm.intervention_type" placeholder="选择干预类型" style="width: 100%">
                <el-option label="谈话辅导" value="talk" />
                <el-option label="学业帮扶" value="academic" />
                <el-option label="心理疏导" value="psychological" />
                <el-option label="家校联系" value="family" />
                <el-option label="其他" value="other" />
              </el-select>
            </el-form-item>
            <el-form-item label="干预时间" prop="intervention_time">
              <el-date-picker
                v-model="addForm.intervention_time"
                type="datetime"
                placeholder="选择干预时间"
                style="width: 100%"
              />
            </el-form-item>
            <el-form-item label="干预内容" prop="content">
              <el-input
                v-model="addForm.content"
                type="textarea"
                :rows="4"
                placeholder="详细描述干预内容..."
              />
            </el-form-item>
            <el-form-item label="后续计划">
              <el-input
                v-model="addForm.follow_up_plan"
                type="textarea"
                :rows="2"
                placeholder="输入后续跟进计划（可选）..."
              />
            </el-form-item>
          </el-form>
        </div>

        <!-- 右侧：AI评语参考 -->
        <div class="dialog-right" v-if="addForm.student_id && dialogAIComment.summary">
          <div class="ai-reference-panel">
            <div class="ai-panel-header">
              <el-icon :size="18" color="#7c3aed"><MagicStick /></el-icon>
              <span>AI评语参考</span>
            </div>

            <div class="ai-panel-content">
              <!-- 问题分析 -->
              <div class="ai-section" v-if="dialogAIComment.analysis">
                <h4 class="section-title">
                  <el-icon><TrendCharts /></el-icon>
                  问题分析
                </h4>
                <p class="section-content">{{ dialogAIComment.analysis }}</p>
              </div>

              <!-- 干预建议 -->
              <div class="ai-section" v-if="dialogAIComment.suggestions && dialogAIComment.suggestions.length > 0">
                <h4 class="section-title">
                  <el-icon><List /></el-icon>
                  干预建议
                  <el-button type="primary" link size="small" @click="applyAISuggestions">
                    <el-icon><CopyDocument /></el-icon>
                    引用建议
                  </el-button>
                </h4>
                <ul class="suggestion-list">
                  <li v-for="(item, index) in dialogAIComment.suggestions" :key="index">
                    <el-icon color="#10b981"><CircleCheck /></el-icon>
                    <span>{{ item }}</span>
                  </li>
                </ul>
              </div>

              <!-- 沟通话术 -->
              <div class="ai-section talking-points" v-if="dialogAIComment.talking_points">
                <h4 class="section-title">
                  <el-icon><ChatDotRound /></el-icon>
                  沟通话术
                  <el-button type="primary" link size="small" @click="applyTalkingPoints">
                    <el-icon><CopyDocument /></el-icon>
                    引用话术
                  </el-button>
                </h4>
                <div class="talking-box">
                  <p>{{ dialogAIComment.talking_points }}</p>
                </div>
              </div>

              <!-- 行动计划 -->
              <div class="ai-section" v-if="dialogAIComment.action_plan">
                <h4 class="section-title">
                  <el-icon><Calendar /></el-icon>
                  行动计划
                  <el-button type="primary" link size="small" @click="applyActionPlan">
                    <el-icon><CopyDocument /></el-icon>
                    引用计划
                  </el-button>
                </h4>
                <p class="section-content">{{ dialogAIComment.action_plan }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧空状态（当没有AI评语时） -->
        <div class="dialog-right" v-else-if="addForm.student_id">
          <div class="ai-reference-panel empty">
            <el-empty description="暂无AI评语">
              <template #image>
                <el-icon :size="48" color="#cbd5e1"><MagicStick /></el-icon>
              </template>
              <el-button type="primary" @click="generateDialogAIComment" :loading="dialogAILoading">
                <el-icon><MagicStick /></el-icon>
                生成AI评语
              </el-button>
            </el-empty>
          </div>
        </div>
      </div>

      <template #footer>
        <el-button @click="addDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitAdd" :loading="submitting">确认</el-button>
      </template>
    </el-dialog>

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailDialogVisible" title="干预详情" width="600px">
      <div v-if="selectedIntervention" class="detail-content">
        <div class="detail-header">
          <div class="student-info">
            <el-avatar :size="64" :style="{ background: getAvatarColor(selectedIntervention.student_name) }">
              {{ selectedIntervention.student_name?.charAt(0) }}
            </el-avatar>
            <div class="info-text">
              <h3>{{ selectedIntervention.student_name }}</h3>
              <p>学号：{{ selectedIntervention.student_no }}</p>
            </div>
          </div>
          <el-tag :type="getTypeTagType(selectedIntervention.intervention_type)" size="large">
            {{ getTypeLabel(selectedIntervention.intervention_type) }}
          </el-tag>
        </div>

        <el-descriptions :column="1" border class="detail-descriptions">
          <el-descriptions-item label="干预时间">
            {{ formatDateTime(selectedIntervention.intervention_time) }}
          </el-descriptions-item>
          <el-descriptions-item label="干预内容">
            {{ selectedIntervention.content }}
          </el-descriptions-item>
          <el-descriptions-item label="后续计划" v-if="selectedIntervention.follow_up_plan">
            {{ selectedIntervention.follow_up_plan }}
          </el-descriptions-item>
          <el-descriptions-item label="干预效果">
            <el-tag
              :type="selectedIntervention.is_effective === true ? 'success' : selectedIntervention.is_effective === false ? 'danger' : 'info'"
            >
              {{ selectedIntervention.is_effective === true ? '有效' : selectedIntervention.is_effective === false ? '无效' : '待评估' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="效果评估" v-if="selectedIntervention.evaluation_note">
            {{ selectedIntervention.evaluation_note }}
          </el-descriptions-item>
        </el-descriptions>

        <div class="detail-actions">
          <el-button type="primary" @click="evaluateIntervention(selectedIntervention)">
            {{ selectedIntervention.is_effective === null ? '评估效果' : '修改评估' }}
          </el-button>
        </div>
      </div>
    </el-dialog>

    <!-- 评估弹窗 -->
    <el-dialog v-model="evaluateDialogVisible" title="干预效果评估" width="500px">
      <el-form :model="evaluateForm" label-width="100px">
        <el-form-item label="评估结果">
          <el-radio-group v-model="evaluateForm.is_effective">
            <el-radio :label="true">有效</el-radio>
            <el-radio :label="false">无效</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="评估说明">
          <el-input
            v-model="evaluateForm.evaluation_note"
            type="textarea"
            :rows="4"
            placeholder="请输入评估说明..."
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="evaluateDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitEvaluate" :loading="evaluating">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Plus, FirstAidKit, CircleCheck, Timer, Search, List, Warning,
  MagicStick, TrendCharts, ChatDotRound, Calendar, CopyDocument
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import {
  getInterventionRecords, createIntervention, updateIntervention,
  getInterventionStats, getWarningRecords, getWarningRecordsByStudent,
  searchStudents as searchStudentsApi, generateCounselorComment, getStoredComment
} from '@/api/counselor'

// 路由
const router = useRouter()
const route = useRoute()

// 状态
const loading = ref(false)
const submitting = ref(false)
const evaluating = ref(false)
const addDialogVisible = ref(false)
const detailDialogVisible = ref(false)
const evaluateDialogVisible = ref(false)
const viewMode = ref('table')
const selectedIntervention = ref(null)
const addFormRef = ref(null)

// 当前筛选的学生（从预警页面跳转）
const selectedStudentId = ref(null)
const selectedStudentInfo = ref(null)

// 新增弹窗中的学生预警信息
const selectedStudentForDialog = ref(null)
const dialogStudentWarnings = ref([])
const dialogHighestRisk = ref('normal')

// 弹窗中的AI评语
const dialogAIComment = reactive({
  summary: '',
  analysis: '',
  suggestions: [],
  action_plan: '',
  talking_points: '',
  generated_at: ''
})
const dialogAILoading = ref(false)

// 统计数据
const stats = reactive({
  total: 156,
  thisMonth: 23,
  effective: 98,
  effectivenessRate: 75,
  pending: 15
})

// 筛选表单
const filterForm = reactive({
  type: '',
  is_effective: undefined,
  search: ''
})

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

// 干预记录列表
const interventions = ref([])

// 新增表单
const addForm = reactive({
  student_id: null,
  warning_id: null,
  intervention_type: '',
  intervention_time: new Date(),
  content: '',
  follow_up_plan: ''
})

const addRules = {
  student_id: [{ required: true, message: '请选择学生', trigger: 'change' }],
  intervention_type: [{ required: true, message: '请选择干预类型', trigger: 'change' }],
  intervention_time: [{ required: true, message: '请选择干预时间', trigger: 'change' }],
  content: [{ required: true, message: '请输入干预内容', trigger: 'blur' }]
}

// 评估表单
const evaluateForm = reactive({
  is_effective: null,
  evaluation_note: ''
})

// 学生搜索
const studentLoading = ref(false)
const studentOptions = ref([])

// 预警选项
const warningOptions = ref([])

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    // 获取干预记录
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      ...filterForm
    }
    // 如果指定了学生，添加学生筛选
    if (selectedStudentId.value) {
      params.student_id = selectedStudentId.value
    }
    const res = await getInterventionRecords(params)
    if (res.code === 200) {
      interventions.value = res.data?.results || res.data || []
      pagination.total = res.data?.count || interventions.value.length
    }

    // 获取统计数据
    const statsRes = await getInterventionStats(selectedStudentId.value)
    if (statsRes.code === 200) {
      const data = statsRes.data || {}
      stats.total = data.total || 156
      stats.thisMonth = data.this_month || 23
      stats.effective = data.effective_count || 98
      stats.effectivenessRate = data.effectiveness_rate || 75
      stats.pending = data.pending_count || 15
    }
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败')
    interventions.value = []
    pagination.total = 0
  } finally {
    loading.value = false
  }
}

// 加载学生预警信息
const loadStudentWarningInfo = async (studentId) => {
  if (!studentId) return
  try {
    const res = await getWarningRecordsByStudent()
    if (res.code === 200) {
      const students = res.data?.students || []
      const studentData = students.find(s => s.student?.id === parseInt(studentId))
      if (studentData) {
        selectedStudentInfo.value = studentData
      }
    }
  } catch (error) {
    console.error('加载学生预警信息失败:', error)
  }
}

// 清除学生筛选
const clearStudentFilter = () => {
  selectedStudentId.value = null
  selectedStudentInfo.value = null
  router.replace({ path: '/counselor/interventions', query: {} })
  loadData()
}

// 跳转到预警页面
const goToWarnings = () => {
  router.push({
    path: '/counselor/warnings',
    query: selectedStudentId.value ? { student_id: selectedStudentId.value } : {}
  })
}


// 筛选
const handleFilter = () => {
  pagination.page = 1
  loadData()
}

const resetFilter = () => {
  filterForm.type = ''
  filterForm.is_effective = undefined
  filterForm.search = ''
  pagination.page = 1
  loadData()
}

// 分页
const handleSizeChange = (val) => {
  pagination.pageSize = val
  loadData()
}

const handleCurrentChange = (val) => {
  pagination.page = val
  loadData()
}

// 打开新增弹窗
const openAddDialog = async () => {
  addForm.student_id = null
  addForm.warning_id = null
  addForm.intervention_type = ''
  addForm.intervention_time = new Date()
  addForm.content = ''
  addForm.follow_up_plan = ''
  selectedStudentForDialog.value = null
  dialogStudentWarnings.value = []
  dialogHighestRisk.value = 'normal'

  // 清空AI评语
  dialogAIComment.summary = ''
  dialogAIComment.analysis = ''
  dialogAIComment.suggestions = []
  dialogAIComment.action_plan = ''
  dialogAIComment.talking_points = ''
  dialogAIComment.generated_at = ''

  addDialogVisible.value = true
}

// 学生选择变化时加载预警信息
const onStudentChange = async (studentId) => {
  if (!studentId) {
    selectedStudentForDialog.value = null
    dialogStudentWarnings.value = []
    // 清空AI评语
    dialogAIComment.summary = ''
    dialogAIComment.analysis = ''
    dialogAIComment.suggestions = []
    dialogAIComment.action_plan = ''
    dialogAIComment.talking_points = ''
    dialogAIComment.generated_at = ''
    return
  }

  // 获取学生信息
  const student = studentOptions.value.find(s => s.id === studentId)
  if (student) {
    selectedStudentForDialog.value = student
  }

  // 加载该学生的预警信息
  try {
    const res = await getWarningRecordsByStudent()
    if (res.code === 200) {
      const students = res.data?.students || []
      const studentData = students.find(s => s.student?.id === studentId)
      if (studentData) {
        dialogStudentWarnings.value = studentData.warnings || []
        dialogHighestRisk.value = studentData.highest_risk || 'normal'
        // 同时更新class_name
        if (studentData.student && selectedStudentForDialog.value) {
          selectedStudentForDialog.value.class_name = studentData.student.class_name
        }
      } else {
        dialogStudentWarnings.value = []
        dialogHighestRisk.value = 'normal'
      }
    }

    // 加载AI评语
    await loadDialogAIComment(studentId)
  } catch (error) {
    console.error('加载学生预警信息失败:', error)
  }
}

// 选择预警课程
const selectWarningCourse = (warningId) => {
  addForm.warning_id = addForm.warning_id === warningId ? null : warningId
}

// 加载弹窗中的AI评语
const loadDialogAIComment = async (studentId) => {
  if (!studentId) return

  dialogAILoading.value = true
  try {
    // 先尝试获取已存储的AI评语
    const warnings = dialogStudentWarnings.value
    if (warnings.length > 0) {
      const res = await getStoredComment(warnings[0].id)
      if (res.code === 200) {
        const data = res.data || {}
        const counselorComment = data.counselor_comment || {}

        dialogAIComment.summary = counselorComment.summary || ''
        dialogAIComment.analysis = counselorComment.analysis || ''
        dialogAIComment.suggestions = counselorComment.suggestions || []
        dialogAIComment.action_plan = counselorComment.action_plan || ''
        dialogAIComment.talking_points = counselorComment.talking_points || ''
        dialogAIComment.generated_at = data.generated_at || ''
        return
      }
    }

    // 如果没有存储的评语，清空
    dialogAIComment.summary = ''
    dialogAIComment.analysis = ''
    dialogAIComment.suggestions = []
    dialogAIComment.action_plan = ''
    dialogAIComment.talking_points = ''
    dialogAIComment.generated_at = ''
  } catch (error) {
    console.error('加载AI评语失败:', error)
    // 清空AI评语
    dialogAIComment.summary = ''
    dialogAIComment.analysis = ''
    dialogAIComment.suggestions = []
    dialogAIComment.action_plan = ''
    dialogAIComment.talking_points = ''
    dialogAIComment.generated_at = ''
  } finally {
    dialogAILoading.value = false
  }
}

// 生成弹窗中的AI评语
const generateDialogAIComment = async () => {
  if (!addForm.student_id || dialogStudentWarnings.value.length === 0) {
    ElMessage.warning('请先选择学生和预警课程')
    return
  }

  dialogAILoading.value = true
  try {
    const warningId = dialogStudentWarnings.value[0]?.id
    const res = await generateCounselorComment({
      student_id: addForm.student_id,
      warning_id: warningId
    })

    if (res.code === 200) {
      const data = res.data || {}
      dialogAIComment.summary = data.summary || ''
      dialogAIComment.analysis = data.analysis || ''
      dialogAIComment.suggestions = data.suggestions || []
      dialogAIComment.action_plan = data.action_plan || ''
      dialogAIComment.talking_points = data.talking_points || ''
      dialogAIComment.generated_at = new Date().toLocaleString('zh-CN')
      ElMessage.success('AI评语生成成功')
    }
  } catch (error) {
    console.error('生成AI评语失败:', error)
    ElMessage.error('生成AI评语失败，请稍后重试')
  } finally {
    dialogAILoading.value = false
  }
}

// 引用AI建议到干预内容
const applyAISuggestions = () => {
  if (!dialogAIComment.suggestions || dialogAIComment.suggestions.length === 0) return

  const suggestions = dialogAIComment.suggestions.map((s, i) => `${i + 1}. ${s}`).join('\n')
  if (addForm.content) {
    addForm.content += '\n\n【AI建议参考】\n' + suggestions
  } else {
    addForm.content = '【AI建议参考】\n' + suggestions
  }
  ElMessage.success('已引用AI建议到干预内容')
}

// 引用沟通话术到干预内容
const applyTalkingPoints = () => {
  if (!dialogAIComment.talking_points) return

  if (addForm.content) {
    addForm.content += '\n\n【沟通话术参考】\n' + dialogAIComment.talking_points
  } else {
    addForm.content = '【沟通话术参考】\n' + dialogAIComment.talking_points
  }
  ElMessage.success('已引用沟通话术到干预内容')
}

// 引用行动计划到后续计划
const applyActionPlan = () => {
  if (!dialogAIComment.action_plan) return

  if (addForm.follow_up_plan) {
    addForm.follow_up_plan += '\n\n【AI行动计划参考】\n' + dialogAIComment.action_plan
  } else {
    addForm.follow_up_plan = '【AI行动计划参考】\n' + dialogAIComment.action_plan
  }
  ElMessage.success('已引用行动计划到后续计划')
}

// 带学生信息打开新增弹窗（从预警页面跳转过来）
const openAddDialogWithStudent = async (studentId, warningId = null) => {
  // 重置表单
  addForm.student_id = studentId
  addForm.warning_id = warningId
  addForm.intervention_type = ''
  addForm.intervention_time = new Date()
  addForm.content = ''
  addForm.follow_up_plan = ''

  // 重置AI评语
  dialogAIComment.summary = ''
  dialogAIComment.analysis = ''
  dialogAIComment.suggestions = []
  dialogAIComment.action_plan = ''
  dialogAIComment.talking_points = ''
  dialogAIComment.generated_at = ''

  // 加载学生信息并填充到选项中
  if (studentId) {
    studentLoading.value = true
    try {
      // 获取学生信息
      const searchRes = await searchStudentsApi(studentId.toString())
      if (searchRes.code === 200) {
        const students = searchRes.data || []
        studentOptions.value = students.map(s => ({
          id: s.id,
          name: s.name,
          student_no: s.student_no,
          class_name: s.class_name
        }))
        // 设置当前学生
        const currentStudent = students.find(s => s.id === studentId)
        if (currentStudent) {
          selectedStudentForDialog.value = currentStudent
        }
      }

      // 加载该学生的预警信息
      const warningRes = await getWarningRecordsByStudent()
      if (warningRes.code === 200) {
        const allStudents = warningRes.data?.students || []
        const studentData = allStudents.find(s => s.student?.id === studentId)
        if (studentData) {
          dialogStudentWarnings.value = studentData.warnings || []
          dialogHighestRisk.value = studentData.highest_risk || 'normal'
          // 同时更新selectedStudentForDialog的class_name
          if (studentData.student && selectedStudentForDialog.value) {
            selectedStudentForDialog.value.class_name = studentData.student.class_name
          }
        }
      }

      // 加载AI评语
      await loadDialogAIComment(studentId)
    } catch (error) {
      console.error('加载学生信息失败:', error)
    } finally {
      studentLoading.value = false
    }
  }

  addDialogVisible.value = true

  // 清除URL参数
  router.replace({ path: '/counselor/interventions', query: {} })
}

// 搜索学生
const searchStudents = async (query) => {
  if (query.length < 2) return
  studentLoading.value = true
  try {
    const res = await searchStudentsApi(query)
    if (res.code === 200) {
      // 后端返回的数据格式: [{ id, student_no, name, class_id }]
      // 转换为前端需要的格式
      studentOptions.value = (res.data || []).map(s => ({
        id: s.id,
        name: s.name,
        student_no: s.student_no
      }))
    } else {
      studentOptions.value = []
      ElMessage.warning(res.message || '搜索失败')
    }
  } catch (error) {
    console.error('搜索学生失败:', error)
    ElMessage.error('搜索学生失败')
    studentOptions.value = []
  } finally {
    studentLoading.value = false
  }
}

// 提交新增
const submitAdd = async () => {
  const valid = await addFormRef.value?.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    const res = await createIntervention(addForm)
    if (res.code === 200 || res.code === 201) {
      ElMessage.success('干预记录创建成功')
      addDialogVisible.value = false
      loadData()
    }
  } catch (error) {
    console.error('创建失败:', error)
    ElMessage.error('创建失败')
  } finally {
    submitting.value = false
  }
}

// 查看详情
const viewDetail = (row) => {
  selectedIntervention.value = row
  detailDialogVisible.value = true
}

// 评估干预
const evaluateIntervention = (row) => {
  selectedIntervention.value = row
  evaluateForm.is_effective = row.is_effective
  evaluateForm.evaluation_note = row.evaluation_note || ''
  evaluateDialogVisible.value = true
}

// 提交评估
const submitEvaluate = async () => {
  if (selectedIntervention.value.is_effective === null && evaluateForm.is_effective === null) {
    ElMessage.warning('请选择评估结果')
    return
  }

  evaluating.value = true
  try {
    const res = await updateIntervention(selectedIntervention.value.id, {
      is_effective: evaluateForm.is_effective,
      evaluation_note: evaluateForm.evaluation_note
    })
    if (res.code === 200) {
      ElMessage.success('评估已保存')
      evaluateDialogVisible.value = false
      detailDialogVisible.value = false
      loadData()
    }
  } catch (error) {
    console.error('评估失败:', error)
    ElMessage.error('评估失败')
  } finally {
    evaluating.value = false
  }
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
  const labels = { high: '高危', medium: '中等', low: '低危', normal: '正常' }
  return labels[level] || level
}

const getScoreTagType = (score) => {
  if (score < 60) return 'danger'
  if (score < 75) return 'warning'
  return 'success'
}

const getScoreClass = (score) => {
  if (score < 60) return 'score-danger'
  if (score < 75) return 'score-warning'
  return 'score-success'
}

const getTypeTagType = (type) => {
  const types = { talk: 'primary', academic: 'success', psychological: 'warning', family: 'info', other: '' }
  return types[type] || ''
}

const getTypeLabel = (type) => {
  const labels = { talk: '谈话辅导', academic: '学业帮扶', psychological: '心理疏导', family: '家校联系', other: '其他' }
  return labels[type] || type
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN')
}

onMounted(() => {
  // 检查路由参数，如果有 student_id 则加载学生信息
  const { student_id, warning_id } = route.query
  if (student_id) {
    selectedStudentId.value = parseInt(student_id)
    // 加载学生预警信息和干预记录
    loadStudentWarningInfo(student_id).then(() => {
      loadData()
    })
    // 延迟打开新增弹窗
    setTimeout(() => {
      openAddDialogWithStudent(parseInt(student_id), warning_id ? parseInt(warning_id) : null)
    }, 800)
  } else {
    loadData()
  }
})
</script>

<style scoped>
.interventions-page {
  max-width: 1400px;
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
  margin-bottom: 24px;
}

.stat-card :deep(.el-card__body) {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.stat-icon.blue { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
.stat-icon.green { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }
.stat-icon.orange { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
}

.stat-label {
  font-size: 14px;
  color: #6b7280;
  margin-top: 4px;
}

.stat-change {
  font-size: 12px;
  margin-top: 4px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.stat-change.success { color: #10b981; }
.stat-change.warning { color: #f59e0b; }

.filter-card {
  margin-bottom: 24px;
  border-radius: 12px;
}

.interventions-card {
  border-radius: 12px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #374151;
}

.student-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

/* 时间线视图 */
.timeline-view {
  padding: 20px;
}

.timeline-card {
  border-radius: 12px;
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.student-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.info-text .name {
  font-weight: 600;
  color: #1f2937;
}

.info-text .no {
  font-size: 12px;
  color: #6b7280;
  margin-top: 2px;
}

.timeline-content {
  color: #4b5563;
  margin-bottom: 12px;
  line-height: 1.6;
}

.timeline-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 详情弹窗 */
.detail-content {
  padding: 0 10px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.detail-header .student-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.detail-header .info-text h3 {
  margin: 0 0 8px 0;
  font-size: 20px;
  color: #1f2937;
}

.detail-header .info-text p {
  margin: 0;
  color: #6b7280;
  font-size: 14px;
}

.detail-descriptions {
  margin: 20px 0;
}

.detail-actions {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}

/* 弹窗内容布局 */
.dialog-content {
  display: flex;
  gap: 20px;
  min-height: 500px;
}

.dialog-left {
  flex: 1;
  min-width: 0;
}

.dialog-right {
  width: 360px;
  flex-shrink: 0;
}

/* AI参考面板 */
.ai-reference-panel {
  background: #fafafa;
  border-radius: 12px;
  padding: 16px;
  height: 100%;
  max-height: 560px;
  overflow-y: auto;
}

.ai-reference-panel.empty {
  display: flex;
  align-items: center;
  justify-content: center;
}

.ai-panel-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 15px;
  color: #374151;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e5e7eb;
}

.ai-panel-content .ai-section {
  margin-bottom: 16px;
}

.ai-panel-content .ai-section:last-child {
  margin-bottom: 0;
}

.ai-panel-content .section-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 8px;
}

.ai-panel-content .section-content {
  color: #4b5563;
  line-height: 1.6;
  font-size: 12px;
  padding: 10px 12px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.ai-panel-content .suggestion-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.ai-panel-content .suggestion-list li {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 6px 0;
  border-bottom: 1px solid #f3f4f6;
  font-size: 12px;
  color: #4b5563;
}

.ai-panel-content .suggestion-list li:last-child {
  border-bottom: none;
}

.ai-panel-content .talking-points {
  background: #f0f9ff;
  border-radius: 8px;
  padding: 12px;
}

.ai-panel-content .talking-box {
  color: #0369a1;
  line-height: 1.6;
  font-size: 12px;
}

/* 学生信息展示（只读） */
.student-info-display {
  margin-bottom: 20px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 8px;
}

.student-profile-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.profile-details .name {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.profile-details .student-no {
  font-size: 13px;
  color: #6b7280;
  font-weight: normal;
  margin-left: 8px;
}

.profile-details .class-info {
  font-size: 13px;
  color: #6b7280;
  margin-top: 4px;
}

.profile-details .warning-count {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 6px;
}

.profile-details .count-text {
  font-size: 13px;
  color: #6b7280;
}

.profile-details .no-warning {
  margin-top: 6px;
}

.profile-details .class-info {
  font-size: 13px;
  color: #6b7280;
  margin-top: 4px;
}

.warning-courses-list {
  margin-top: 12px;
}

.warning-courses-list .section-title {
  font-size: 13px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 10px;
}

.course-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 10px;
}

.course-card {
  padding: 12px;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.course-card:hover {
  border-color: #3b82f6;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.1);
}

.course-card.active {
  border-color: #3b82f6;
  background: #eff6ff;
}

.course-card .course-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.course-card .course-name {
  font-weight: 500;
  color: #1f2937;
  font-size: 14px;
}

.course-card .course-scores {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #6b7280;
}

.course-card .score-item b {
  font-weight: 600;
}

.score-danger { color: #ef4444; }
.score-warning { color: #f59e0b; }
.score-success { color: #10b981; }

/* 学生信息卡片 */
.student-info-card {
  margin-bottom: 24px;
  border-radius: 12px;
}

.student-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.student-profile {
  display: flex;
  align-items: center;
  gap: 16px;
}

.profile-text h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  color: #1f2937;
}

.profile-text .student-no {
  font-size: 14px;
  color: #6b7280;
  font-weight: normal;
}

.student-tags {
  display: flex;
  gap: 8px;
}

.student-actions {
  display: flex;
  gap: 12px;
}

.warning-courses {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e5e7eb;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 12px;
}

.course-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.course-tag {
  font-size: 12px;
}
</style>
