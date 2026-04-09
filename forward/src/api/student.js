/**
 * 学生端API模块
 * 包含学情分析、课程、资源等相关接口
 */

import request from './request'

// ==================== 学情分析相关 ====================

/**
 * 获取学生学习活动统计
 */
export function getLearningStats() {
    return request({
        url: '/learning/activities/summary/',
        method: 'get'
    })
}

/**
 * 获取学生学习活动列表
 * @param {Object} params - 查询参数
 */
export function getLearningActivities(params = {}) {
    return request({
        url: '/learning/activities/',
        method: 'get',
        params
    })
}

/**
 * 记录学习活动（视频观看等）
 * @param {Object} data - 活动数据
 */
export function recordLearningActivity(data) {
    return request({
        url: '/learning/record/',
        method: 'post',
        data
    })
}

/**
 * 批量记录学习活动
 * @param {Object} data - 批量活动数据
 */
export function batchRecordLearningActivity(data) {
    return request({
        url: '/learning/record/batch/',
        method: 'post',
        data
    })
}

// ==================== 作业相关 ====================

/**
 * 获取学生作业统计
 */
export function getHomeworkStats() {
    return request({
        url: '/learning/homework/stats/',
        method: 'get'
    })
}

/**
 * 获取作业提交记录
 */
export function getHomeworkSubmissions(params = {}) {
    return request({
        url: '/learning/homework/submissions/',
        method: 'get',
        params
    })
}

// ==================== 考试相关 ====================

/**
 * 获取学生考试统计
 */
export function getExamStats() {
    return request({
        url: '/learning/exams/stats/',
        method: 'get'
    })
}

/**
 * 获取考试结果列表
 */
export function getExamResults(params = {}) {
    return request({
        url: '/learning/exams/results/',
        method: 'get',
        params
    })
}

// ==================== 课程相关 ====================

/**
 * 获取学生的课程列表
 */
export function getStudentCourses() {
    return request({
        url: '/courses/student/',
        method: 'get'
    })
}

/**
 * 获取课程详情
 * @param {number} courseId - 课程ID
 */
export function getCourseDetail(courseId) {
    return request({
        url: `/courses/${courseId}/`,
        method: 'get'
    })
}

/**
 * 获取课程知识点
 * @param {number} courseId - 课程ID
 */
export function getCourseKnowledgePoints(courseId) {
    return request({
        url: `/courses/${courseId}/knowledge-points/`,
        method: 'get'
    })
}

// ==================== 课程资源相关 ====================

/**
 * 获取课程资源列表
 * @param {Object} params - 查询参数 {course_id, resource_type}
 */
export function getCourseResources(params = {}) {
    return request({
        url: '/courses/resources/',
        method: 'get',
        params
    })
}

/**
 * 下载课程资源
 * @param {number} resourceId - 资源ID
 */
export function downloadCourseResource(resourceId) {
    return request({
        url: `/courses/resources/${resourceId}/download/`,
        method: 'get',
        responseType: 'blob'
    })
}

// ==================== 预警相关 ====================

/**
 * 获取学生预警记录
 * @param {Object} params - 查询参数
 */
export function getStudentWarnings(params = {}) {
    return request({
        url: '/warnings/',
        method: 'get',
        params
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
 * 获取学生课程得分
 * @param {Object} params - 查询参数
 */
export function getStudentCourseScores(params = {}) {
    return request({
        url: '/warnings/scores/',
        method: 'get',
        params
    })
}

// ==================== 综合统计 ====================

/**
 * 获取课程学习统计
 * @param {Object} params - 查询参数 {course_id}
 */
export function getCourseLearningStats(params = {}) {
    return request({
        url: '/learning/course-stats/',
        method: 'get',
        params
    })
}

/**
 * 获取学生学情汇总（整合多个接口的数据）
 * 用于Analysis.vue页面
 */
export async function getStudentAnalysisSummary() {
    try {
        // 并行获取多个统计数据
        const [
            learningStats,
            homeworkStats,
            examStats,
            warnings,
            scores
        ] = await Promise.all([
            getLearningStats().catch(() => ({ data: {} })),
            getHomeworkStats().catch(() => ({ data: {} })),
            getExamStats().catch(() => ({ data: {} })),
            getStudentWarnings().catch(() => ({ data: { results: [] } })),
            getStudentCourseScores().catch(() => ({ data: { results: [] } }))
        ])

        return {
            code: 200,
            data: {
                learning: learningStats.data || {},
                homework: homeworkStats.data || {},
                exam: examStats.data || {},
                warnings: warnings.data?.results || [],
                scores: scores.data?.results || []
            }
        }
    } catch (error) {
        console.error('获取学情汇总失败:', error)
        throw error
    }
}
