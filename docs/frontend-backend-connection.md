# 学业预警系统 - 前后端连接说明

## 一、通信架构概览

```
┌─────────────────┐         HTTP/REST          ┌─────────────────┐
│   Vue 3 前端     │  ◄────────────────────►   │  Django 后端     │
│  (localhost:8080)│    JWT + CSRF 双认证       │ (localhost:8000)│
└─────────────────┘                          └─────────────────┘
```

---

## 二、API封装层 (request.js)

### 2.1 基础配置

**文件位置**：`forward/src/api/request.js`

```javascript
const request = axios.create({
    baseURL: 'http://localhost:8000/api',
    timeout: 10000,
    withCredentials: true,  // 允许携带cookie
    headers: {
        'Content-Type': 'application/json'
    }
})
```

### 2.2 双认证机制

前端同时支持 **JWT Token** 和 **Django Session** 两种认证方式：

#### JWT 认证（主要方式）

```javascript
// 请求拦截器 - 自动附加JWT Token
const token = localStorage.getItem('token')
if (token) {
    config.headers.Authorization = `Bearer ${token}`
}
```

**登录流程**：
1. 用户提交用户名密码 → `/auth/login/`
2. 后端验证成功返回 `token`
3. 前端将 `token` 存入 `localStorage`
4. 后续请求自动携带 `Authorization: Bearer <token>`

#### Session 认证（备用方式）

```javascript
// 从cookie获取CSRF Token
const csrfToken = getCSRFToken()
if (csrfToken) {
    config.headers['X-CSRFToken'] = csrfToken
}
```

**用途**：主要用于文件上传等需要 Django 表单验证的场景。

### 2.3 响应格式统一处理

后端返回两种格式，前端统一封装：

| 后端格式 | 前端处理 | 适用场景 |
|---------|---------|---------|
| `{code, data, message}` | 直接返回 | 自定义API |
| `{count, results, next, previous}` | 包装为 `{code: 200, data: {results, count, ...}}` | DRF分页 |

```javascript
// 响应拦截器处理逻辑
if (data.code !== undefined) {
    // 自定义格式
    if (data.code !== 200) {
        ElMessage.error(data.message || '请求失败')
        return Promise.reject(new Error(data.message))
    }
    return data
}
// DRF分页格式
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
```

### 2.4 错误处理

| HTTP状态码 | 处理方式 |
|-----------|---------|
| 401 | 清除token，跳转登录页 |
| 403 | 显示"没有权限访问" |
| 404 | 显示"请求的资源不存在" |
| 500 | 显示"服务器错误" |
| 网络错误 | 显示"网络连接失败" |

---

## 三、前端API模块

### 3.1 API目录结构

```
forward/src/api/
├── request.js          # Axios实例封装（基础配置）
├── teacher.js          # 教师端API
├── counselor.js        # 辅导员端API
├── student.js          # 学生端API
└── (common.js)         # 公共API（如搜索）
```

### 3.2 教师端API封装

**文件位置**：`forward/src/api/teacher.js`

```javascript
import request from './request'

export function getTeacherCourses() {
  return request({ url: '/teacher/courses/', method: 'get' })
}

export function getCourseStudents(courseId, params) {
  return request({
    url: `/teacher/courses/${courseId}/students/`,
    method: 'get',
    params
  })
}

export function uploadCourseResource(data) {
  return request({
    url: '/courses/resources/',
    method: 'post',
    data,
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}
```

### 3.3 辅导员端API封装

**文件位置**：`forward/src/api/counselor.js`

```javascript
import request from './request'

export function getWarningRecordsByStudent(params) {
  return request({ url: '/warnings/by-student/', method: 'get', params })
}

export function getInterventionRecords(params) {
  return request({ url: '/interventions/', method: 'get', params })
}

export function createIntervention(data) {
  return request({ url: '/interventions/create/', method: 'post', data })
}
```

---

## 四、路由与布局

### 4.1 路由配置

**文件位置**：`forward/src/router/index.js`

```javascript
const routes = [
  { path: '/login', component: () => import('@/views/login/index.vue') },
  {
    path: '/teacher',
    component: () => import('@/components/TeacherLayout.vue'),
    children: [
      { path: 'dashboard', component: () => import('@/views/teacher/Dashboard.vue') },
      { path: 'courses/:courseId/students', component: () => import('@/views/teacher/CourseStudents.vue') },
      { path: 'upload', component: () => import('@/views/teacher/UploadData.vue') },
      { path: 'resources', component: () => import('@/views/teacher/Resources.vue') }
    ]
  },
  {
    path: '/counselor',
    component: () => import('@/components/CounselorLayout.vue'),
    children: [
      { path: 'dashboard', component: () => import('@/views/counselor/Dashboard.vue') },
      { path: 'warnings', component: () => import('@/views/counselor/Warnings.vue') },
      { path: 'interventions', component: () => import('@/views/counselor/Interventions.vue') }
    ]
  }
]
```

### 4.2 布局组件

| 布局组件 | 用途 | 侧边栏导航 |
|---------|------|-----------|
| Layout.vue | 学生端 | 学情分析、课程列表、课程资源 |
| TeacherLayout.vue | 教师端 | 课程概览、数据上传、教学资源 |
| CounselorLayout.vue | 辅导员端 | 学情总览、预警管理、干预记录 |
| AdminLayout.vue | 管理员端 | 用户管理、课程管理、班级管理 |

### 4.3 布局组件的数据获取

**示例**：CounselorLayout.vue

```javascript
// 挂载时获取辅导员信息
onMounted(async () => {
  try {
    const res = await request({ url: '/auth/profile/counselor/', method: 'get' })
    if (res.code === 200) {
      counselorInfo.value = res.data
    }
  } catch (error) {
    // 失败时从localStorage读取
    const userInfo = localStorage.getItem('userInfo')
    if (userInfo) {
      counselorInfo.value = JSON.parse(userInfo)
    }
  }
})
```

---

## 五、数据流模式

### 5.1 典型页面数据流

以辅导员端 Dashboard 为例：

```
1. 页面加载 (onMounted)
   │
   ├──► getCounselorDashboardStats()  [API调用]
   │      │
   │      ├──► GET /auth/counselor/dashboard-stats/
   │      │
   │      └──► 返回 {totalStudents, classList, highRiskCount...}
   │
   ├──► getWarningRecordsByStudent()  [API调用]
   │      │
   │      ├──► GET /warnings/by-student/
   │      │
   │      └──► 返回学生预警列表
   │
   └──► 数据绑定到响应式ref
          │
          ├──► stats.value = { ... }
          ├──► recentWarnings.value = [ ... ]
          │
          └──► 模板渲染 (ECharts图表 + 表格)
```

### 5.2 代码示例

```vue
<template>
  <div>
    <!-- 统计卡片 -->
    <el-row :gutter="20">
      <el-col :span="6" v-for="item in statsCards" :key="item.title">
        <stat-card :title="item.title" :value="item.value" />
      </el-col>
    </el-row>

    <!-- 预警列表 -->
    <el-table :data="warningList">
      <el-table-column prop="student.name" label="姓名" />
      <el-table-column prop="highest_risk" label="风险等级" />
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getCounselorDashboardStats, getWarningRecordsByStudent } from '@/api/counselor'

const stats = ref({})
const warningList = ref([])

onMounted(async () => {
  // 并行加载数据
  const [statsRes, warningsRes] = await Promise.all([
    getCounselorDashboardStats(),
    getWarningRecordsByStudent()
  ])

  if (statsRes.code === 200) {
    stats.value = statsRes.data
  }

  if (warningsRes.code === 200) {
    warningList.value = warningsRes.data.students || []
  }
})
</script>
```

---

## 六、登录与认证流程

### 6.1 完整登录流程

```
用户输入账号密码
    │
    ▼
POST /auth/login/  (axios)
    │
    ▼
后端验证 → 生成JWT Token
    │
    ▼
返回 {token, user: {id, username, role, name}}
    │
    ▼
前端存储:
  - localStorage.setItem('token', token)
  - localStorage.setItem('userInfo', JSON.stringify(user))
    │
    ▼
根据 role 跳转:
  - teacher → /teacher/dashboard
  - counselor → /counselor/dashboard
  - student → /student/analysis
  - admin → /admin/dashboard
```

### 6.2 认证状态维持

```javascript
// 每次请求自动携带token（request.js拦截器）
config.headers.Authorization = `Bearer ${localStorage.getItem('token')}`

// 401处理（response拦截器）
case 401:
    ElMessage.error('未登录或登录已过期')
    localStorage.removeItem('token')
    window.location.href = '/login'
```

---

## 七、文件上传的特殊处理

### 7.1 文件上传流程

```javascript
// 1. 构建FormData
const formData = new FormData()
formData.append('file', file)           // File对象
formData.append('course', courseId)     // 课程ID
formData.append('resource_type', type)  // 资源类型
formData.append('description', desc)    // 描述

// 2. 发送请求（自动删除Content-Type头，让浏览器设置boundary）
request({
  url: '/courses/resources/',
  method: 'post',
  data: formData
  // request.js会自动删除Content-Type，浏览器自动设置 multipart/form-data; boundary=...
})
```

### 7.2 文件下载

```javascript
// 直接打开下载链接
window.open(`http://localhost:8000/api/courses/resources/${id}/download/`)
```

---

## 八、错误处理与降级策略

### 8.1 API失败时的降级

```javascript
// 示例：Dashboard组件
const loadData = async () => {
  loading.value = true
  try {
    const res = await getWarningRecordsByStudent()
    if (res.code === 200) {
      warningList.value = res.data
    }
  } catch (error) {
    // API失败时使用模拟数据
    console.warn('API调用失败，使用模拟数据')
    warningList.value = getMockStudentWarnings()
  } finally {
    loading.value = false
  }
}
```

### 8.2 常见错误场景

| 场景 | 前端表现 | 处理方式 |
|------|---------|---------|
| 后端未启动 | "网络连接失败" | 检查后端服务状态 |
| Token过期 | 自动跳转登录页 | 重新登录获取新token |
| 跨域错误 | 浏览器控制台CORS报错 | 配置Django CORS中间件 |
| 权限不足 | "没有权限访问" | 确认用户角色是否正确 |

---

## 九、前后端字段映射对照表

### 9.1 教师端

| 前端字段 | 后端字段 | 说明 |
|---------|---------|------|
| courseId | id | 课程ID |
| courseName | name | 课程名称 |
| studentCount | student_count | 学生数量 |
| warningCount | warning_count | 预警数量 |
| avgScore | composite_score | 平均综合得分 |
| riskLevel | risk_level | 风险等级 |

### 9.2 辅导员端

| 前端字段 | 后端字段 | 说明 |
|---------|---------|------|
| studentId | id | 学生ID |
| studentNo | student_no | 学号 |
| highestRisk | highest_risk | 最高风险等级 |
| riskCount | risk_count | 各等级计数 |
| avgScore | avg_score | 平均得分 |
| interventionType | intervention_type | 干预类型 |
| isEffective | is_effective | 干预效果 |

---

## 十、开发调试技巧

### 10.1 查看请求

浏览器开发者工具 → Network → 筛选XHR/Fetch：
- 检查请求URL、Method、Headers
- 检查请求参数（Payload）
- 检查响应数据（Response）

### 10.2 常见问题排查

```
问题：前端提示"未登录或登录已过期"
排查：
  1. 检查localStorage中是否有token
  2. 检查请求头是否携带Authorization
  3. 检查后端是否验证通过

问题：API返回数据但页面不显示
排查：
  1. 检查响应格式是否为 {code: 200, data: ...}
  2. 检查data字段结构是否与前端期望一致
  3. 检查Vue组件中是否正确绑定ref

问题：文件上传失败
排查：
  1. 确认Content-Type是否被正确删除（让浏览器自动设置）
  2. 确认文件对象是否正确放入FormData
  3. 检查后端是否配置multipart解析
```
