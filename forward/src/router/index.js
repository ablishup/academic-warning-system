import { createRouter, createWebHistory } from 'vue-router'

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

export default router
