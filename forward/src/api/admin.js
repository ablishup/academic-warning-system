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
 * 获取指定辅导员详情
 * @param {number} id - 辅导员ID
 */
export function getCounselorDetail(id) {
    return request({
        url: `/auth/counselors/${id}/`,
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

// ==================== 系统统计 ====================

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
