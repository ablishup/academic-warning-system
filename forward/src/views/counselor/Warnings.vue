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
      <el-col :span="8">
        <el-card class="stat-card danger" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon"><el-icon :size="32"><Warning /></el-icon></div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.activeHigh }}</div>
              <div class="stat-label">待处理高危预警</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="stat-card warning" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon"><el-icon :size="32"><Bell /></el-icon></div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.activeMedium }}</div>
              <div class="stat-label">待处理中等预警</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="stat-card success" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon"><el-icon :size="32"><CircleCheck /></el-icon></div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.resolvedThisMonth }}</div>
              <div class="stat-label">本月已解决</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 筛选栏 -->
    <el-card class="filter-card" shadow="never">
      <div class="filter-row">
        <div class="filter-item">
          <span class="filter-label">风险等级：</span>
          <el-select v-model="filters.risk_level" placeholder="全部等级" clearable @change="handleFilterChange">
            <el-option label="高危" value="high" />
            <el-option label="中等" value="medium" />
            <el-option label="低危" value="low" />
          </el-select>
        </div>
        <div class="filter-item">
          <span class="filter-label">状态：</span>
          <el-select v-model="filters.status" placeholder="全部状态" clearable @change="handleFilterChange">
            <el-option label="待处理" value="active" />
            <el-option label="已解决" value="resolved" />
          </el-select>
        </div>
        <div class="filter-item">
          <span class="filter-label">搜索：</span>
          <el-input v-model="filters.search" placeholder="姓名/学号/课程" clearable style="width: 200px" @change="handleFilterChange">
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
        </div>
        <el-button @click="resetFilters">重置</el-button>
      </div>
    </el-card>

    <!-- 预警列表 -->
    <el-card class="warnings-table-card" shadow="never" v-loading="loading">
      <template #header>
        <div class="table-header">
          <span class="table-title">预警学生列表</span>
          <el-button-group v-if="selectedRows.length > 0">
            <el-button type="primary" size="small" @click="batchIntervention">批量干预</el-button>
            <el-button type="success" size="small" @click="batchResolve">批量解决</el-button>
          </el-button-group>
        </div>
      </template>

      <el-table :data="warnings" stripe @selection-change="handleSelectionChange" v-loading="loading">
        <el-table-column type="selection" width="55" />
        <el-table-column prop="student_name" label="学生姓名" width="100">
          <template #default="{ row }">
            <div class="student-name">
              <el-avatar :size="32" :style="{ background: getAvatarColor(row.student_name) }">{{ row.student_name?.charAt(0) }}</el-avatar>
              <span>{{ row.student_name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="student_no" label="学号" width="120" />
        <el-table-column prop="course_name" label="课程" min-width="150" />
        <el-table-column prop="risk_level" label="风险等级" width="100">
          <template #default="{ row }">
            <el-tag :type="getRiskTagType(row.risk_level)" effect="dark" size="small">{{ getRiskLabel(row.risk_level) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="composite_score" label="综合得分" width="100" sortable>
          <template #default="{ row }">
            <span :class="getScoreClass(row.composite_score)">{{ row.composite_score }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'danger' : 'success'" size="small">{{ row.status === 'active' ? '待处理' : '已解决' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="calculation_time" label="预警时间" width="150" sortable>
          <template #default="{ row }">{{ formatDate(row.calculation_time) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewDetail(row)"><el-icon><View /></el-icon>详情</el-button>
            <el-button type="success" link size="small" @click="addIntervention(row)"><el-icon><FirstAidKit /></el-icon>干预</el-button>
            <el-button v-if="row.status === 'active'" type="info" link size="small" @click="resolveWarning(row)"><el-icon><CircleCheck /></el-icon>解决</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination v-model:current-page="pagination.page" v-model:page-size="pagination.pageSize" :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]" layout="total, sizes, prev, pager, next" @size-change="handleSizeChange"
          @current-change="handleCurrentChange" />
      </div>
    </el-card>

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailDialogVisible" title="预警详情" width="750px">
      <div v-if="selectedWarning" class="warning-detail">
        <div class="detail-header">
          <el-avatar :size="64" :style="{ background: getAvatarColor(selectedWarning.student_name) }">{{ selectedWarning.student_name?.charAt(0) }}</el-avatar>
          <div class="detail-info">
            <h3>{{ selectedWarning.student_name }}</h3>
            <p>学号：{{ selectedWarning.student_no }} | 班级：{{ selectedWarning.class_name || '计算机2101' }}</p>
          </div>
          <div class="detail-tags">
            <el-tag :type="getRiskTagType(selectedWarning.risk_level)" effect="dark" size="large">{{ getRiskLabel(selectedWarning.risk_level) }}</el-tag>
            <el-tag :type="selectedWarning.status === 'active' ? 'danger' : 'success'" size="large">{{ selectedWarning.status === 'active' ? '待处理' : '已解决' }}</el-tag>
          </div>
        </div>

        <el-divider />

        <div class="detail-scores">
          <h4><el-icon><TrendCharts /></el-icon> 得分详情</h4>
          <el-row :gutter="20">
            <el-col :span="6">
              <div class="score-item">
                <div class="score-label">综合得分</div>
                <div class="score-value" :class="getScoreClass(selectedWarning.composite_score)">{{ selectedWarning.composite_score }}</div>
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
          <h4><el-icon><MagicStick /></el-icon> 系统建议</h4>
          <p>{{ selectedWarning.suggestion }}</p>
        </div>

        <div class="detail-actions">
          <el-button type="primary" @click="addIntervention(selectedWarning)"><el-icon><FirstAidKit /></el-icon>添加干预</el-button>
          <el-button v-if="selectedWarning.status === 'active'" type="success" @click="resolveWarning(selectedWarning)"
          ><el-icon><CircleCheck /></el-icon>标记解决</el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import {
  Warning, Bell, CircleCheck, Refresh, Download, Search,
  View, FirstAidKit, TrendCharts, MagicStick
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getWarningRecords, resolveWarning as apiResolveWarning } from '@/api/counselor'

// 状态
const loading = ref(false)
const detailDialogVisible = ref(false)
const selectedWarning = ref(null)
const selectedRows = ref([])

// 统计数据
const stats = reactive({
  activeHigh: 12,
  activeMedium: 28,
  resolvedThisMonth: 45
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

// 预警列表
const warnings = ref([])

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      ...filters
    }
    const res = await getWarningRecords(params)
    if (res.code === 200) {
      warnings.value = res.data?.results || res.data || []
      pagination.total = res.data?.count || warnings.value.length
    }
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败')
    warnings.value = getMockWarnings()
    pagination.total = warnings.value.length
  } finally {
    loading.value = false
  }
}

// 模拟数据
const getMockWarnings = () => [
  { id: 1, student_name: '张三', student_no: '2021001', class_name: '计算机2101', course_name: '数据结构', risk_level: 'high', composite_score: 45.5, attendance_score: 60, progress_score: 40, homework_score: 50, exam_score: 42, calculation_time: '2025-04-10', status: 'active', suggestion: '建议增加课堂出勤率，及时完成作业，多参与视频学习。' },
  { id: 2, student_name: '李四', student_no: '2021002', class_name: '计算机2101', course_name: '数据结构', risk_level: 'medium', composite_score: 65.2, attendance_score: 75, progress_score: 60, homework_score: 68, exam_score: 62, calculation_time: '2025-04-09', status: 'active', suggestion: '学习态度较好，需要提高作业质量和视频学习进度。' },
  { id: 3, student_name: '王五', student_no: '2021003', class_name: '软件2101', course_name: '算法设计', risk_level: 'high', composite_score: 38.7, attendance_score: 55, progress_score: 35, homework_score: 40, exam_score: 38, calculation_time: '2025-04-09', status: 'active', suggestion: '学业风险较高，建议辅导员尽快约谈，制定学习计划。' },
  { id: 4, student_name: '赵六', student_no: '2021004', class_name: '软件2102', course_name: '操作系统', risk_level: 'low', composite_score: 72.3, attendance_score: 80, progress_score: 75, homework_score: 70, exam_score: 68, calculation_time: '2025-04-08', status: 'active', suggestion: '总体学习情况良好，继续保持。' },
  { id: 5, student_name: '钱七', student_no: '2021005', class_name: '网络2101', course_name: '计算机网络', risk_level: 'medium', composite_score: 58.9, attendance_score: 70, progress_score: 55, homework_score: 60, exam_score: 52, calculation_time: '2025-04-08', status: 'resolved', suggestion: '已进行约谈并制定改进计划。' },
  { id: 6, student_name: '孙八', student_no: '2021006', class_name: '计算机2102', course_name: '数据库', risk_level: 'high', composite_score: 42.1, attendance_score: 50, progress_score: 45, homework_score: 40, exam_score: 45, calculation_time: '2025-04-07', status: 'active', suggestion: '建议联系家长，加强学习监督。' },
  { id: 7, student_name: '周九', student_no: '2021007', class_name: '软件2101', course_name: '数据结构', risk_level: 'low', composite_score: 75.6, attendance_score: 85, progress_score: 80, homework_score: 72, exam_score: 70, calculation_time: '2025-04-07', status: 'active', suggestion: '学习稳定，注意保持。' },
  { id: 8, student_name: '吴十', student_no: '2021008', class_name: '计算机2101', course_name: '算法设计', risk_level: 'medium', composite_score: 62.3, attendance_score: 78, progress_score: 58, homework_score: 65, exam_score: 60, calculation_time: '2025-04-06', status: 'active', suggestion: '建议加强算法练习，参加辅导答疑。' }
]

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

const handleCurrentChange = (val) => {
  pagination.page = val
  loadData()
}

// 选择变化
const handleSelectionChange = (val) => {
  selectedRows.value = val
}

// 查看详情
const viewDetail = (row) => {
  selectedWarning.value = row
  detailDialogVisible.value = true
}

// 添加干预
const addIntervention = (row) => {
  // 跳转到干预页面
  ElMessage.info('跳转到干预记录页面')
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

// 批量干预
const batchIntervention = () => {
  ElMessage.info(`对 ${selectedRows.value.length} 名学生进行批量干预`)
}

// 批量解决
const batchResolve = async () => {
  try {
    await ElMessageBox.confirm(`确定要批量解决选中的 ${selectedRows.value.length} 条预警吗？`, '确认', { type: 'warning' })
    ElMessage.success('批量解决成功')
    loadData()
  } catch {
    // 取消
  }
}

// 刷新数据
const refreshData = () => {
  loadData()
  ElMessage.success('数据已刷新')
}

// 导出数据
const exportData = () => {
  ElMessage.success('数据导出成功')
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

const getScoreClass = (score) => {
  if (score < 60) return 'score-danger'
  if (score < 75) return 'score-warning'
  return 'score-success'
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.warnings-page {
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
  padding: 0;
}

.stat-content {
  display: flex;
  align-items: center;
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
  margin-right: 16px;
}

.stat-card.danger .stat-icon { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
.stat-card.warning .stat-icon { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }
.stat-card.success .stat-icon { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }

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

.warnings-table-card {
  border-radius: 12px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.table-title {
  font-weight: 600;
  font-size: 16px;
  color: #374151;
}

.student-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.score-danger { color: #ef4444; font-weight: 600; }
.score-warning { color: #f59e0b; font-weight: 600; }
.score-success { color: #10b981; font-weight: 600; }

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e5e7eb;
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
  padding: 16px;
  background: #f9fafb;
  border-radius: 8px;
}

.score-label {
  font-size: 13px;
  color: #6b7280;
  margin-bottom: 8px;
}

.score-value {
  font-size: 24px;
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
