import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const refreshToken = ref(localStorage.getItem('refreshToken') || '')
  const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || 'null'))

  const isLoggedIn = computed(() => !!token.value || !!userInfo.value)
  const role = computed(() => userInfo.value?.role || '')
  const isStudent = computed(() => role.value === 'student')
  const isTeacher = computed(() => role.value === 'teacher')
  const isCounselor = computed(() => role.value === 'counselor')
  const isAdmin = computed(() => role.value === 'admin')

  function login(data) {
    // JWT: data = { user: {...}, access: '...', refresh: '...' }
    // 兼容旧格式: data = { role:..., username:... }
    const user = data.user || data
    userInfo.value = user
    localStorage.setItem('userInfo', JSON.stringify(user))

    if (data.access) {
      token.value = data.access
      localStorage.setItem('token', data.access)
    }
    if (data.refresh) {
      refreshToken.value = data.refresh
      localStorage.setItem('refreshToken', data.refresh)
    }
  }

  function logout() {
    token.value = ''
    refreshToken.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
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
