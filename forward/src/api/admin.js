import request from './request'

/**
 * 管理员端API模块
 */

// ==================== 用户管理 ====================

/**
 * 获取用户列表
 * @param {Object} params - 查询参数 {role, is_active, search, page, page_size}
 */
export function getUserList(params = {}) {
    return request({
        url: '/auth/list/',
        method: 'get',
        params
    })
}

/**
 * 获取用户详情
 * @param {number} id - 用户ID
 */
export function getUserDetail(id) {
    return request({
        url: `/auth/${id}/`,
        method: 'get'
    })
}

/**
 * 创建用户
 * @param {Object} data - 用户数据
 */
export function createUser(data) {
    return request({
        url: '/auth/list/',
        method: 'post',
        data
    })
}

/**
 * 更新用户
 * @param {number} id - 用户ID
 * @param {Object} data - 更新数据
 */
export function updateUser(id, data) {
    return request({
        url: `/auth/${id}/`,
        method: 'put',
        data
    })
}

/**
 * 删除用户
 * @param {number} id - 用户ID
 */
export function deleteUser(id) {
    return request({
        url: `/auth/${id}/`,
        method: 'delete'
    })
}

/**
 * 重置用户密码
 * @param {number} id - 用户ID
 * @param {string} newPassword - 新密码
 */
export function resetUserPassword(id, newPassword) {
    return request({
        url: `/auth/${id}/reset-password/`,
        method: 'post',
        data: { new_password: newPassword }
    })
}

/**
 * 切换用户状态（启用/禁用）
 * @param {number} id - 用户ID
 * @param {boolean} isActive - 状态
 */
export function toggleUserStatus(id, isActive) {
    return request({
        url: `/auth/${id}/toggle-status/`,
        method: 'post',
        data: { is_active: isActive }
    })
}

/**
 * 获取当前登录教师信息
 */
export function getCurrentTeacherProfile() {
    return request({
        url: '/auth/profile/teacher/',
        method: 'get'
    })
}

/**
 * 获取当前登录辅导员信息
 */
export function getCurrentCounselorProfile() {
    return request({
        url: '/auth/profile/counselor/',
        method: 'get'
    })
}

/**
 * 获取教师列表
 * @param {Object} params - 查询参数 {department, search}
 */
export function getTeacherList(params = {}) {
    return request({
        url: '/auth/teachers/',
        method: 'get',
        params
    })
}

/**
 * 获取辅导员列表
 * @param {Object} params - 查询参数 {department, search}
 */
export function getCounselorList(params = {}) {
    return request({
        url: '/auth/counselors/',
        method: 'get',
        params
    })
}

/**
 * 获取指定教师详情
 * @param {number} id - 教师ID
 */
export function getTeacherDetail(id) {
    return request({
        url: `/auth/teachers/${id}/`,
        method: 'get'
    })
}

/**
 * 更新教师信息
 * @param {number} id - 教师ID
 * @param {Object} data - 更新数据
 */
export function updateTeacher(id, data) {
    return request({
        url: `/auth/teachers/${id}/`,
        method: 'put',
        data
    })
}

/**
 * 获取指定辅导员详情
 * @param {number} id - 辅导员ID
 */
export function getCounselorDetail(id) {
    return request({
        url: `/auth/counselors/${id}/`,
        method: 'get'
    })
}

/**
 * 更新辅导员信息
 * @param {number} id - 辅导员ID
 * @param {Object} data - 更新数据
 */
export function updateCounselor(id, data) {
    return request({
        url: `/auth/counselors/${id}/`,
        method: 'put',
        data
    })
}

/**
 * 获取辅导员管理的班级列表
 * @param {number} id - 辅导员ID
 */
export function getCounselorClasses(id) {
    return request({
        url: `/auth/counselors/${id}/classes/`,
        method: 'get'
    })
}

/**
 * 为辅导员分配班级
 * @param {number} id - 辅导员ID
 * @param {Array} classIds - 班级ID数组
 */
export function assignClassesToCounselor(id, classIds) {
    return request({
        url: `/auth/counselors/${id}/assign-classes/`,
        method: 'post',
        data: { class_ids: classIds }
    })
}

/**
 * 解除辅导员与班级的关联
 * @param {number} id - 辅导员ID
 * @param {number} classId - 班级ID
 */
export function removeClassFromCounselor(id, classId) {
    return request({
        url: `/auth/counselors/${id}/remove-class/`,
        method: 'post',
        data: { class_id: classId }
    })
}

/**
 * 获取可分配的班级列表（未被管理的班级）
 */
export function getAvailableClasses() {
    return request({
        url: '/auth/available-classes/',
        method: 'get'
    })
}

// ==================== 院系列表 ====================

/**
 * 获取院系列表
 */
export function getDepartmentList() {
    return request({
        url: '/auth/departments/',
        method: 'get'
    })
}

// ==================== 课程管理 ====================

/**
 * 获取课程列表
 * @param {Object} params - 查询参数
 */
export function getAdminCourses(params = {}) {
    return request({
        url: '/courses/',
        method: 'get',
        params
    })
}

/**
 * 创建课程
 * @param {Object} data - 课程数据
 */
export function createCourse(data) {
    return request({
        url: '/courses/',
        method: 'post',
        data
    })
}

/**
 * 更新课程
 * @param {number} id - 课程ID
 * @param {Object} data - 更新数据
 */
export function updateCourse(id, data) {
    return request({
        url: `/courses/${id}/`,
        method: 'put',
        data
    })
}

/**
 * 删除课程
 * @param {number} id - 课程ID
 */
export function deleteCourse(id) {
    return request({
        url: `/courses/${id}/`,
        method: 'delete'
    })
}

/**
 * 获取教师列表（用于下拉选择）
 */
export function getTeacherOptions() {
    return getUserList({ role: 'teacher', page_size: 100 })
}

/**
 * 获取课程学生列表
 * @param {number} courseId - 课程ID
 */
export function getCourseStudents(courseId) {
    return request({
        url: `/courses/${courseId}/students/`,
        method: 'get'
    })
}

/**
 * 批量添加学生到课程
 * @param {number} courseId - 课程ID
 * @param {Array} studentIds - 学生ID数组
 */
export function addStudentsToCourse(courseId, studentIds) {
    return request({
        url: `/courses/${courseId}/add-students/`,
        method: 'post',
        data: { student_ids: studentIds }
    })
}

/**
 * 从课程移除学生
 * @param {number} courseId - 课程ID
 * @param {number} studentId - 学生ID
 */
export function removeStudentFromCourse(courseId, studentId) {
    return request({
        url: `/courses/${courseId}/remove-student/`,
        method: 'post',
        data: { student_id: studentId }
    })
}

// ==================== 专业管理 ====================

/**
 * 获取专业列表
 */
export function getMajorList() {
    return request({
        url: '/classes/majors/',
        method: 'get'
    })
}

// ==================== 班级管理 ====================

/**
 * 获取班级列表
 * @param {Object} params - 查询参数
 */
export function getAdminClasses(params = {}) {
    return request({
        url: '/classes/',
        method: 'get',
        params
    })
}

/**
 * 创建班级
 * @param {Object} data - 班级数据
 */
export function createClass(data) {
    return request({
        url: '/classes/',
        method: 'post',
        data
    })
}

/**
 * 更新班级
 * @param {number} id - 班级ID
 * @param {Object} data - 更新数据
 */
export function updateClass(id, data) {
    return request({
        url: `/classes/${id}/`,
        method: 'put',
        data
    })
}

/**
 * 删除班级
 * @param {number} id - 班级ID
 */
export function deleteClass(id) {
    return request({
        url: `/classes/${id}/`,
        method: 'delete'
    })
}

/**
 * 获取辅导员列表（用于下拉选择）
 */
export function getCounselorOptions() {
    return getUserList({ role: 'counselor', page_size: 100 })
}

/**
 * 获取班级学生列表
 * @param {number} classId - 班级ID
 */
export function getClassStudents(classId) {
    return request({
        url: `/classes/${classId}/students/`,
        method: 'get'
    })
}

/**
 * 批量添加学生到班级
 * @param {number} classId - 班级ID
 * @param {Array} studentIds - 学生ID数组
 */
export function addStudentsToClass(classId, studentIds) {
    return request({
        url: `/classes/${classId}/add-students/`,
        method: 'post',
        data: { student_ids: studentIds }
    })
}

/**
 * 从班级移除学生
 * @param {number} classId - 班级ID
 * @param {number} studentId - 学生ID
 */
export function removeStudentFromClass(classId, studentId) {
    return request({
        url: `/classes/${classId}/remove-student/`,
        method: 'post',
        data: { student_id: studentId }
    })
}

/**
 * 获取学生列表（支持未分配班级筛选）
 * @param {Object} params - 查询参数 {unassigned, keyword}
 */
export function getStudentOptions(params = {}) {
    return request({
        url: '/classes/students/',
        method: 'get',
        params
    })
}

/**
 * 获取学生列表（分页）
 * @param {Object} params - 查询参数 {keyword, page, page_size}
 */
export function getStudentList(params = {}) {
    return request({
        url: '/classes/students/',
        method: 'get',
        params
    })
}

/**
 * 创建学生
 * @param {Object} data - 学生数据
 */
export function createStudent(data) {
    return request({
        url: '/classes/students/',
        method: 'post',
        data
    })
}

/**
 * 更新学生
 * @param {number} id - 学生ID
 * @param {Object} data - 更新数据
 */
export function updateStudent(id, data) {
    return request({
        url: `/classes/students/${id}/`,
        method: 'put',
        data
    })
}

/**
 * 删除学生
 * @param {number} id - 学生ID
 */
export function deleteStudent(id) {
    return request({
        url: `/classes/students/${id}/`,
        method: 'delete'
    })
}

/**
 * 为学生创建登录账号
 * @param {number} studentId - 学生ID
 * @param {string} password - 密码（可选，默认学号+123）
 */
export function createStudentAccount(studentId, password) {
    return request({
        url: '/auth/students/create-account/',
        method: 'post',
        data: { student_id: studentId, password }
    })
}

// ==================== 系统统计 ====================

/**
 * 获取管理员Dashboard统计数据
 */
export function getAdminDashboard() {
    return request({
        url: '/auth/admin/dashboard-stats/',
        method: 'get'
    })
}

/**
 * 获取系统概览数据
 */
export async function getAdminStats() {
    try {
        const [usersRes, coursesRes, warningsRes] = await Promise.all([
            getUserList({ page_size: 1 }).catch(() => ({ data: { count: 0 } })),
            getAdminCourses({ page_size: 1 }).catch(() => ({ data: { count: 0 } })),
            request({ url: '/warnings/stats/', method: 'get' }).catch(() => ({ data: {} }))
        ])

        return {
            code: 200,
            data: {
                totalUsers: usersRes.data?.count || 0,
                totalCourses: coursesRes.data?.count || 0,
                activeWarnings: warningsRes.data?.active_count || 0,
                userDistribution: {
                    students: 0,
                    teachers: 0,
                    counselors: 0,
                    admins: 0
                }
            }
        }
    } catch (error) {
        console.error('获取系统统计失败:', error)
        throw error
    }
}
