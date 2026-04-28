import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/index.vue')
  },
  {
    path: '/student',
    name: 'StudentLayout',
    component: () => import('@/components/Layout.vue'),
    children: [
      {
        path: '',
        redirect: '/student/analysis'
      },
      {
        path: 'analysis',
        name: 'StudentAnalysis',
        component: () => import('@/views/student/Analysis.vue')
      },
      {
        path: 'courses',
        name: 'StudentCourses',
        component: () => import('@/views/student/Courses.vue')
      },
      {
        path: 'course-resources',
        name: 'StudentCourseResources',
        component: () => import('@/views/student/CourseResources.vue')
      }
    ]
  },
  {
    path: '/teacher',
    name: 'TeacherLayout',
    component: () => import('@/components/TeacherLayout.vue'),
    children: [
      {
        path: '',
        redirect: '/teacher/dashboard'
      },
      {
        path: 'dashboard',
        name: 'TeacherDashboard',
        component: () => import('@/views/teacher/Dashboard.vue')
      },
      {
        path: 'courses/:courseId/students',
        name: 'TeacherCourseStudents',
        component: () => import('@/views/teacher/CourseStudents.vue')
      },
      {
        path: 'upload',
        name: 'TeacherUpload',
        component: () => import('@/views/teacher/UploadData.vue')
      },
      {
        path: 'resources',
        name: 'TeacherResources',
        component: () => import('@/views/teacher/Resources.vue')
      }
    ]
  },
  {
    path: '/counselor',
    name: 'CounselorLayout',
    component: () => import('@/components/CounselorLayout.vue'),
    children: [
      {
        path: '',
        redirect: '/counselor/dashboard'
      },
      {
        path: 'dashboard',
        name: 'CounselorDashboard',
        component: () => import('@/views/counselor/Dashboard.vue')
      },
      {
        path: 'warnings',
        name: 'CounselorWarnings',
        component: () => import('@/views/counselor/Warnings.vue')
      },
      {
        path: 'interventions',
        name: 'CounselorInterventions',
        component: () => import('@/views/counselor/Interventions.vue')
      }
    ]
  },
  {
    path: '/admin',
    name: 'AdminLayout',
    component: () => import('@/components/AdminLayout.vue'),
    children: [
      {
        path: '',
        redirect: '/admin/dashboard'
      },
      {
        path: 'dashboard',
        name: 'AdminDashboard',
        component: () => import('@/views/admin/Dashboard.vue')
      },
      {
        path: 'teachers',
        name: 'AdminTeachers',
        component: () => import('@/views/admin/TeacherManagement.vue')
      },
      {
        path: 'students',
        name: 'AdminStudents',
        component: () => import('@/views/admin/StudentManagement.vue')
      },
      {
        path: 'counselors',
        name: 'AdminCounselors',
        component: () => import('@/views/admin/Counselors.vue')
      },
      {
        path: 'courses',
        name: 'AdminCourses',
        component: () => import('@/views/admin/Courses.vue')
      },
      {
        path: 'classes',
        name: 'AdminClasses',
        component: () => import('@/views/admin/Classes.vue')
      },
      {
        path: 'passwords',
        name: 'AdminPasswords',
        component: () => import('@/views/admin/PasswordManagement.vue')
      }
    ]
  },
  {
    path: '/',
    redirect: '/login'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 角色→路径前缀映射
const rolePrefixMap = {
  student: '/student',
  teacher: '/teacher',
  counselor: '/counselor',
  admin: '/admin'
}

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  // 登录页直接放行
  if (to.path === '/login') {
    // 已登录则跳转对应首页
    if (authStore.isLoggedIn && authStore.role) {
      return next(authStore.getHomePath(authStore.role))
    }
    return next()
  }

  // 未登录 → 跳转登录页
  if (!authStore.isLoggedIn) {
    return next('/login')
  }

  // 角色越权拦截：检查路径前缀
  const expectedPrefix = rolePrefixMap[authStore.role]
  if (expectedPrefix && !to.path.startsWith(expectedPrefix)) {
    return next(authStore.getHomePath(authStore.role))
  }

  next()
})

export default router
