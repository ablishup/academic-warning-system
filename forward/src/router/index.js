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
    path: '/',
    redirect: '/login'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
