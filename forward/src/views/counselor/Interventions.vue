<template>
  <div class="interventions-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <h1>干预记录</h1>
        <p>管理学生干预措施，跟踪干预效果</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="openAddDialog">
          <el-icon><Plus /></el-icon>
          新增干预
        </el-button>
      </div>
    </div>

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
    <el-dialog v-model="addDialogVisible" title="新增干预记录" width="600px">
      <el-form :model="addForm" label-width="100px" :rules="addRules" ref="addFormRef">
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
          >
            <el-option
              v-for="item in studentOptions"
              :key="item.id"
              :label="`${item.name} (${item.student_no})`"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="关联预警" prop="warning_id">
          <el-select v-model="addForm.warning_id" placeholder="选择关联的预警（可选）" clearable style="width: 100%">
            <el-option
              v-for="item in warningOptions"
              :key="item.id"
              :label="`${item.course_name} - ${getRiskLabel(item.risk_level)}`"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
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
import { ref, reactive, onMounted } from 'vue'
import {
  Plus, FirstAidKit, CircleCheck, Timer, Search
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import {
  getInterventionRecords, createIntervention, updateIntervention,
  getInterventionStats, getWarningRecords
} from '@/api/counselor'

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
    const res = await getInterventionRecords(params)
    if (res.code === 200) {
      interventions.value = res.data?.results || res.data || []
      pagination.total = res.data?.count || interventions.value.length
    }

    // 获取统计数据
    const statsRes = await getInterventionStats()
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
    // 使用模拟数据
    interventions.value = getMockInterventions()
  } finally {
    loading.value = false
  }
}

// 模拟数据
const getMockInterventions = () => [
  {
    id: 1,
    student_name: '张三',
    student_no: '2021001',
    intervention_type: 'talk',
    content: '与学生进行一对一谈话，了解学习困难原因，学生反映近期家庭有变故影响学习状态。已建议学生寻求心理咨询支持。',
    intervention_time: '2025-04-10T14:30:00',
    is_effective: true,
    follow_up_plan: '两周后复查学习状态',
    evaluation_note: '学生后续学习积极性有所提升'
  },
  {
    id: 2,
    student_name: '李四',
    student_no: '2021002',
    intervention_type: 'academic',
    content: '安排学业帮扶，指派优秀学生进行课后辅导，重点帮助数据结构课程。',
    intervention_time: '2025-04-09T10:00:00',
    is_effective: null,
    follow_up_plan: '持续关注作业完成情况'
  },
  {
    id: 3,
    student_name: '王五',
    student_no: '2021003',
    intervention_type: 'family',
    content: '与学生家长电话沟通，告知学生在校学习情况，建议家长关注学生学习状态，配合学校督促学生按时上课。',
    intervention_time: '2025-04-08T16:00:00',
    is_effective: false,
    evaluation_note: '家长反馈无力管教，效果不明显'
  },
  {
    id: 4,
    student_name: '赵六',
    student_no: '2021004',
    intervention_type: 'psychological',
    content: '转介学校心理咨询中心，专业心理咨询师介入。',
    intervention_time: '2025-04-07T09:30:00',
    is_effective: true,
    evaluation_note: '学生情绪状态明显改善'
  },
  {
    id: 5,
    student_name: '钱七',
    student_no: '2021005',
    intervention_type: 'other',
    content: '协调任课教师，适当调整作业提交截止日期，给予学生缓冲时间。',
    intervention_time: '2025-04-06T11:00:00',
    is_effective: true
  },
  {
    id: 6,
    student_name: '孙八',
    student_no: '2021006',
    intervention_type: 'talk',
    content: '了解学生缺课原因，学生表示对课程不感兴趣，已进行思想教育。',
    intervention_time: '2025-04-05T15:00:00',
    is_effective: null
  }
]

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

  // 加载预警选项
  try {
    const res = await getWarningRecords({ status: 'active', page_size: 100 })
    if (res.code === 200) {
      warningOptions.value = res.data?.results || res.data || []
    }
  } catch (error) {
    console.error('加载预警列表失败:', error)
  }

  addDialogVisible.value = true
}

// 搜索学生
const searchStudents = async (query) => {
  if (query.length < 2) return
  studentLoading.value = true
  try {
    // 实际应该调用搜索学生API
    // const res = await searchStudents(query)
    // studentOptions.value = res.data || []

    // 模拟数据
    studentOptions.value = [
      { id: 1, name: '张三', student_no: '2021001' },
      { id: 2, name: '李四', student_no: '2021002' },
      { id: 3, name: '王五', student_no: '2021003' },
      { id: 4, name: '赵六', student_no: '2021004' },
      { id: 5, name: '钱七', student_no: '2021005' }
    ].filter(s => s.name.includes(query) || s.student_no.includes(query))
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

const getTypeTagType = (type) => {
  const types = { talk: 'primary', academic: 'success', psychological: 'warning', family: 'info', other: '' }
  return types[type] || ''
}

const getTypeLabel = (type) => {
  const labels = { talk: '谈话辅导', academic: '学业帮扶', psychological: '心理疏导', family: '家校联系', other: '其他' }
  return labels[type] || type
}

const getRiskLabel = (level) => {
  const labels = { high: '高危', medium: '中等', low: '低危' }
  return labels[level] || level
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
  loadData()
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
</style>
