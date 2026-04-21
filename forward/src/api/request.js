import axios from 'axios'
import { ElMessage } from 'element-plus'

// 获取CSRF Token（从cookie中）
function getCSRFToken() {
    const name = 'csrftoken'
    const value = `; ${document.cookie}`
    const parts = value.split(`; ${name}=`)
    if (parts.length === 2) return parts.pop().split(';').shift()
    return null
}

// 创建axios实例
const request = axios.create({
    baseURL: 'http://localhost:8000/api',
    timeout: 10000,
    withCredentials: true,  // 允许携带cookie（Session认证）
    headers: {
        'Content-Type': 'application/json'
    }
})

// 请求拦截器
request.interceptors.request.use(
    (config) => {
        // 从localStorage获取token（JWT认证）
        const token = localStorage.getItem('token')
        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }

        // 添加CSRF Token（用于Django Session认证）
        const csrfToken = getCSRFToken()
        if (csrfToken) {
            config.headers['X-CSRFToken'] = csrfToken
        }

        // 对于FormData（文件上传），不设置Content-Type，让浏览器自动设置
        if (config.data instanceof FormData) {
            delete config.headers['Content-Type']
        }

        return config
    },
    (error) => {
        return Promise.reject(error)
    }
)

// 响应拦截器
request.interceptors.response.use(
    (response) => {
        const { data } = response
        // 如果返回的是blob类型，直接返回
        if (response.config.responseType === 'blob') {
            return response
        }
        // 统一处理返回格式
        // 兼容两种格式：
        // 1. {code: 200, data: ..., message: ...} - 自定义格式
        // 2. {count, results, next, previous} - DRF分页格式
        if (data.code !== undefined) {
            // 自定义格式
            if (data.code !== 200) {
                ElMessage.error(data.message || '请求失败')
                return Promise.reject(new Error(data.message))
            }
            return data
        }
        // DRF分页格式，包装成统一格式
        if (data.results !== undefined) {
            return {
                code: 200,
                data: {
                    results: data.results,
                    count: data.count,
                    next: data.next,
                    previous: data.previous
                }
            }
        }
        // 其他格式，包装成统一格式
        return {
            code: 200,
            data: data
        }
    },
    (error) => {
        const { response } = error
        if (response) {
            switch (response.status) {
                case 401:
                    ElMessage.error('未登录或登录已过期')
                    localStorage.removeItem('token')
                    window.location.href = '/login'
                    break
                case 403:
                    ElMessage.error('没有权限访问')
                    break
                case 404:
                    ElMessage.error('请求的资源不存在')
                    break
                case 500:
                    ElMessage.error('服务器错误')
                    break
                default:
                    ElMessage.error(response.data?.message || '网络错误')
            }
        } else {
            ElMessage.error('网络连接失败')
        }
        return Promise.reject(error)
    }
)

export default request
