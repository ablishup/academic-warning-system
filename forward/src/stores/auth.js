import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || 'null'))

  const isLoggedIn = computed(() => !!token.value || !!userInfo.value)
  const role = computed(() => userInfo.value?.role || '')
  const isStudent = computed(() => role.value === 'student')
  const isTeacher = computed(() => role.value === 'teacher')
  const isCounselor = computed(() => role.value === 'counselor')
  const isAdmin = computed(() => role.value === 'admin')

  function login(data) {
    // data 来自后端 login 响应: { user: {...}, token?: '...' }
    const user = data.user || data
    userInfo.value = user
    localStorage.setItem('userInfo', JSON.stringify(user))

    // 后端可能返回 token (JWT) 也可能不返回 (纯 Session)
    // 若返回则单独存储供 request.js 拦截器使用
    if (data.token) {
      token.value = data.token
      localStorage.setItem('token', data.token)
    }
  }

  function logout() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
    localStorage.removeItem('rememberedUsername')
  }

  /** 角色路由映射 */
  function getHomePath(roleName) {
    const map = {
      student: '/student/analysis',
      teacher: '/teacher/dashboard',
      counselor: '/counselor/dashboard',
      admin: '/admin/dashboard'
    }
    return map[roleName] || '/login'
  }

  return {
    token, userInfo, isLoggedIn, role,
    isStudent, isTeacher, isCounselor, isAdmin,
    login, logout, getHomePath
  }
})
