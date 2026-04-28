/**
 * 管理员端公共工具函数
 */

/** 格式化日期 */
export function formatDate(dateStr) {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  if (isNaN(d.getTime())) return '-'
  return d.toLocaleDateString('zh-CN')
}

/** 格式化日期时间 */
export function formatDateTime(dateStr) {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  if (isNaN(d.getTime())) return '-'
  return d.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

/** 获取角色标签类型 */
export function getRoleTagType(role) {
  const types = { student: '', teacher: 'success', counselor: 'warning', admin: 'danger' }
  return types[role] || ''
}

/** 获取角色显示文本 */
export function getRoleLabel(role) {
  const labels = { student: '学生', teacher: '教师', counselor: '辅导员', admin: '管理员' }
  return labels[role] || role
}

/** 获取课程状态标签类型 */
export function getStatusTagType(status) {
  const types = { active: 'success', pending: 'info', ended: '' }
  return types[status] || ''
}

/** 获取课程状态显示文本 */
export function getStatusLabel(status) {
  const labels = { active: '进行中', pending: '未开始', ended: '已结束' }
  return labels[status] || status
}

/** 获取预警风险等级标签类型 */
export function getRiskTagType(level) {
  const types = { high: 'danger', medium: 'warning', low: 'info', normal: 'success' }
  return types[level] || ''
}

/** 获取预警风险等级显示文本 */
export function getRiskLabel(level) {
  const labels = { high: '高危', medium: '中等', low: '低危', normal: '正常' }
  return labels[level] || level
}
