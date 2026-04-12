import request from './request'

/**
 * 辅导员端API模块
 */

// ==================== 预警管理 ====================

/**
 * 获取预警记录列表
 * @param {Object} params - 查询参数 {risk_level, status, student_id, course_id, search, ordering}
 */
export function getWarningRecords(params = {}) {
    return request({
        url: '/warnings/',
        method: 'get',
        params
    })
}

/**
 * 获取预警详情
 * @param {number} id - 预警ID
 */
export function getWarningDetail(id) {
    return request({
        url: `/warnings/${id}/`,
        method: 'get'
    })
}

/**
 * 解决预警
 * @param {number} id - 预警ID
 * @param {Object} data - {resolve_note}
 */
export function resolveWarning(id, data) {
    return request({
        url: `/warnings/${id}/resolve/`,
        method: 'post',
        data
    })
}

/**
 * 获取预警统计
 */
export function getWarningStats() {
    return request({
        url: '/warnings/stats/',
        method: 'get'
    })
}

/**
 * 触发预警计算
 * @param {Object} data - {student_id, course_id} 可选，不传则计算全部
 */
export function calculateWarnings(data = {}) {
    return request({
        url: '/warnings/calculate/',
        method: 'post',
        data
    })
}

// ==================== 干预记录 ====================

/**
 * 获取干预记录列表
 * @param {Object} params - 查询参数 {student_id, warning_id, type, is_effective, search}
 */
export function getInterventionRecords(params = {}) {
    return request({
        url: '/interventions/',
        method: 'get',
        params
    })
}

/**
 * 获取干预记录详情
 * @param {number} id - 干预记录ID
 */
export function getInterventionDetail(id) {
    return request({
        url: `/interventions/${id}/`,
        method: 'get'
    })
}

/**
 * 创建干预记录
 * @param {Object} data - 干预记录数据
 */
export function createIntervention(data) {
    return request({
        url: '/interventions/create/',
        method: 'post',
        data
    })
}

/**
 * 更新干预记录
 * @param {number} id - 干预记录ID
 * @param {Object} data - 更新数据
 */
export function updateIntervention(id, data) {
    return request({
        url: `/interventions/${id}/update/`,
        method: 'put',
        data
    })
}

/**
 * 删除干预记录
 * @param {number} id - 干预记录ID
 */
export function deleteIntervention(id) {
    return request({
        url: `/interventions/${id}/delete/`,
        method: 'delete'
    })
}

/**
 * 评估干预效果
 * @param {number} id - 干预记录ID
 * @param {Object} data - {effectiveness, evaluation_notes}
 */
export function evaluateIntervention(id, data) {
    return request({
        url: `/interventions/${id}/evaluate/`,
        method: 'post',
        data
    })
}

/**
 * 获取干预统计
 * @param {number} student_id - 可选，指定学生
 */
export function getInterventionStats(student_id) {
    const params = student_id ? { student_id } : {}
    return request({
        url: '/interventions/stats/',
        method: 'get',
        params
    })
}

/**
 * 获取学生干预汇总
 * @param {number} student_id - 学生ID
 */
export function getStudentInterventionSummary(student_id) {
    return request({
        url: `/interventions/student/${student_id}/summary/`,
        method: 'get'
    })
}

// ==================== 数据同步 ====================

/**
 * 同步学生课程得分数据
 * @param {Object} data - {sync_all: true} 或 {student_id, course_id}
 */
export function syncStudentScores(data = { sync_all: true }) {
    return request({
        url: '/warnings/sync-scores/',
        method: 'post',
        data
    })
}

/**
 * 获取数据同步状态
 */
export function getSyncStatus() {
    return request({
        url: '/warnings/sync-status/',
        method: 'get'
    })
}

// ==================== 全校概览 ====================

/**
 * 获取全校学情概览（整合多个API）
 */
export async function getSchoolOverview() {
    try {
        // 并行获取多个统计数据
        const [warningStatsRes, interventionStatsRes] = await Promise.all([
            getWarningStats(),
            getInterventionStats().catch(() => ({ data: {} }))
        ])

        const warningStats = warningStatsRes.data || {}

        return {
            code: 200,
            data: {
                // 预警统计
                warningStats: {
                    total: warningStats.total_warnings || 0,
                    high: warningStats.high_risk_count || 0,
                    medium: warningStats.medium_risk_count || 0,
                    low: warningStats.low_risk_count || 0,
                    active: warningStats.active_count || 0,
                    resolved: warningStats.resolved_count || 0
                },
                // 干预统计
                interventionStats: interventionStatsRes.data || {}
            }
        }
    } catch (error) {
        console.error('获取全校概览失败:', error)
        throw error
    }
}

/**
 * 获取班级统计（模拟数据，实际需后端支持）
 */
export function getClassStats() {
    // 返回模拟数据，后续对接真实API
    return Promise.resolve({
        code: 200,
        data: [
            { class_name: '计算机2101', student_count: 45, warning_count: 8, avg_score: 78.5 },
            { class_name: '计算机2102', student_count: 42, warning_count: 5, avg_score: 82.3 },
            { class_name: '软件工程2101', student_count: 48, warning_count: 12, avg_score: 75.2 },
            { class_name: '软件工程2102', student_count: 44, warning_count: 6, avg_score: 80.1 },
            { class_name: '网络工程2101', student_count: 40, warning_count: 4, avg_score: 83.6 }
        ]
    })
}

// ==================== 学生详情 ====================

/**
 * 获取学生学情详情（整合多个API）
 * @param {number} student_id - 学生ID
 */
export async function getStudentDetail(student_id) {
    try {
        const [interventionSummaryRes] = await Promise.all([
            getStudentInterventionSummary(student_id).catch(() => ({ data: null }))
        ])

        return {
            code: 200,
            data: {
                interventionSummary: interventionSummaryRes.data
            }
        }
    } catch (error) {
        console.error('获取学生详情失败:', error)
        throw error
    }
}
