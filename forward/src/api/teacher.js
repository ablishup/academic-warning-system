import request from './request'

/**
 * 教师端API模块
 */

// ==================== 教师课程相关 ====================

/**
 * 获取教师教授的课程列表
 */
export function getTeacherCourses() {
    return request({
        url: '/teacher/courses/',
        method: 'get'
    })
}

/**
 * 获取课程学生列表
 * @param {number} courseId - 课程ID
 */
export function getCourseStudents(courseId) {
    return request({
        url: `/teacher/courses/${courseId}/students/`,
        method: 'get'
    })
}

/**
 * 获取课程统计信息
 * @param {number} courseId - 课程ID
 */
export function getCourseStats(courseId) {
    return request({
        url: `/teacher/courses/${courseId}/stats/`,
        method: 'get'
    })
}

/**
 * 获取学生学情详情
 * @param {number} studentId - 学生ID
 * @param {Object} params - 查询参数 {course_id}
 */
export function getStudentSummary(studentId, params = {}) {
    return request({
        url: `/teacher/students/${studentId}/summary/`,
        method: 'get',
        params
    })
}

// ==================== 资源管理相关 ====================

/**
 * 上传课程资源
 * @param {FormData} formData - 包含文件和课程信息的表单数据
 */
export function uploadCourseResource(formData) {
    return request({
        url: '/courses/resources/',
        method: 'post',
        data: formData,
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    })
}

/**
 * 删除课程资源
 * @param {number} resourceId - 资源ID
 */
export function deleteCourseResource(resourceId) {
    return request({
        url: `/courses/resources/${resourceId}/`,
        method: 'delete'
    })
}

// ==================== 数据导入相关 ====================

/**
 * 导入学习活动数据
 * @param {FormData} formData - Excel文件
 */
export function importActivities(formData) {
    return request({
        url: '/import/activities/',
        method: 'post',
        data: formData,
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    })
}

/**
 * 导入作业数据
 * @param {FormData} formData - Excel文件
 */
export function importHomework(formData) {
    return request({
        url: '/import/homework/',
        method: 'post',
        data: formData,
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    })
}

/**
 * 导入考试数据
 * @param {FormData} formData - Excel文件
 */
export function importExams(formData) {
    return request({
        url: '/import/exams/',
        method: 'post',
        data: formData,
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    })
}

/**
 * 下载导入模板
 * @param {string} type - 模板类型 (activities/homework/exams/enrollments)
 */
export function getImportTemplate(type) {
    return request({
        url: '/import/template/',
        method: 'get',
        params: { type },
        responseType: 'blob'
    })
}

// ==================== 作业/考试管理 ====================

/**
 * 创建作业
 * @param {Object} data - 作业数据
 */
export function createHomework(data) {
    return request({
        url: '/learning/homework/assignments/',
        method: 'post',
        data
    })
}

/**
 * 创建考试
 * @param {Object} data - 考试数据
 */
export function createExam(data) {
    return request({
        url: '/learning/exams/assignments/',
        method: 'post',
        data
    })
}

// ==================== 综合接口 ====================

/**
 * 获取教师工作台数据汇总
 */
export async function getTeacherDashboard() {
    try {
        const coursesRes = await getTeacherCourses()
        const courses = coursesRes.data || []

        // 获取每个课程的统计
        const coursesWithStats = await Promise.all(
            courses.map(async (course) => {
                try {
                    const [studentsRes, statsRes] = await Promise.all([
                        getCourseStudents(course.id).catch(() => ({ data: { students: [] } })),
                        getCourseStats(course.id).catch(() => ({ data: {} }))
                    ])
                    return {
                        ...course,
                        studentCount: studentsRes.data?.students?.length || 0,
                        warningCount: statsRes.data?.warning_distribution?.high || 0,
                        avgScore: statsRes.data?.overview?.avg_homework_score || 0
                    }
                } catch (error) {
                    return { ...course, studentCount: 0, warningCount: 0, avgScore: 0 }
                }
            })
        )

        return {
            code: 200,
            data: {
                courses: coursesWithStats,
                totalCourses: courses.length,
                totalStudents: coursesWithStats.reduce((sum, c) => sum + c.studentCount, 0),
                totalWarnings: coursesWithStats.reduce((sum, c) => sum + c.warningCount, 0)
            }
        }
    } catch (error) {
        console.error('获取教师工作台数据失败:', error)
        throw error
    }
}
