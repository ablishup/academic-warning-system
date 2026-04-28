<template>
  <div class="admin-dashboard">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <h1>管理控制台</h1>
        <p>系统数据概览与功能导航</p>
      </div>
    </div>

    <!-- 统计栏 -->
    <el-row :gutter="20" class="stats-row" v-loading="statsLoading">
      <el-col :xs="12" :sm="8" :lg="4">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-value">{{ stats.totalUsers || 0 }}</div>
          <div class="stat-label">总用户数</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="8" :lg="4">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-value">{{ stats.studentCount || 0 }}</div>
          <div class="stat-label">学生</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="8" :lg="4">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-value">{{ stats.teacherCount || 0 }}</div>
          <div class="stat-label">教师</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="8" :lg="4">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-value">{{ stats.counselorCount || 0 }}</div>
          <div class="stat-label">辅导员</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="8" :lg="4">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-value">{{ stats.totalCourses || 0 }}</div>
          <div class="stat-label">课程</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="8" :lg="4">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-value" style="color: #ef4444">{{ stats.activeWarnings || 0 }}</div>
          <div class="stat-label">活跃预警</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 功能模块卡片 -->
    <el-row :gutter="24" class="module-row">
      <el-col :xs="24" :sm="12" :lg="8">
        <el-card class="module-card" shadow="hover" @click="$router.push('/admin/courses')">
          <div class="module-icon" style="background: linear-gradient(135deg, #10b981 0%, #34d399 100%);">
            <el-icon :size="40"><Reading /></el-icon>
          </div>
          <div class="module-title">课程管理</div>
          <div class="module-desc">开设课程、分配任课教师、管理学生选课</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="8">
        <el-card class="module-card" shadow="hover" @click="$router.push('/admin/teachers')">
          <div class="module-icon" style="background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);">
            <el-icon :size="40"><User /></el-icon>
          </div>
          <div class="module-title">教师管理</div>
          <div class="module-desc">管理教师账号信息、查看任课情况</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="8">
        <el-card class="module-card" shadow="hover" @click="$router.push('/admin/students')">
          <div class="module-icon" style="background: linear-gradient(135deg, #06b6d4 0%, #22d3ee 100%);">
            <el-icon :size="40"><UserFilled /></el-icon>
          </div>
          <div class="module-title">学生管理</div>
          <div class="module-desc">管理学生账号信息、查看班级归属</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="8">
        <el-card class="module-card" shadow="hover" @click="$router.push('/admin/counselors')">
          <div class="module-icon" style="background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);">
            <el-icon :size="40"><FirstAidKit /></el-icon>
          </div>
          <div class="module-title">辅导员管理</div>
          <div class="module-desc">分配辅导员、管理负责班级</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="8">
        <el-card class="module-card" shadow="hover" @click="$router.push('/admin/passwords')">
          <div class="module-icon" style="background: linear-gradient(135deg, #ef4444 0%, #f87171 100%);">
            <el-icon :size="40"><Key /></el-icon>
          </div>
          <div class="module-title">密码管理</div>
          <div class="module-desc">管理所有账号的登录密码</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="8">
        <el-card class="module-card" shadow="hover" @click="$router.push('/admin/classes')">
          <div class="module-icon" style="background: linear-gradient(135deg, #8b5cf6 0%, #a78bfa 100%);">
            <el-icon :size="40"><School /></el-icon>
          </div>
          <div class="module-title">班级管理</div>
          <div class="module-desc">管理班级信息，分配学生和辅导员</div>
        </el-card>
      </el-col>
    </el-row>


  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Reading, User, UserFilled, FirstAidKit, Key, School } from '@element-plus/icons-vue'
import { getAdminDashboard } from '@/api/admin'

const statsLoading = ref(false)
const stats = reactive({
  totalUsers: 0,
  studentCount: 0,
  teacherCount: 0,
  counselorCount: 0,
  totalCourses: 0,
  activeWarnings: 0
})

const loadStats = async () => {
  statsLoading.value = true
  try {
    const res = await getAdminDashboard()
    if (res.code === 200 && res.data) {
      Object.assign(stats, res.data)
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
  } finally {
    statsLoading.value = false
  }
}

onMounted(() => { loadStats() })
</script>

<style scoped>
@import './common.css';

.admin-dashboard {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 32px;
}

.page-header h1 {
  font-size: 26px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 8px 0;
}

.page-header p {
  color: #9ca3af;
  margin: 0;
  font-size: 15px;
}

.stats-row {
  margin-bottom: 24px;
}

.stats-row .el-col {
  margin-bottom: 16px;
}

.stat-card {
  border-radius: 12px;
  text-align: center;
}

.stat-card :deep(.el-card__body) {
  padding: 20px 12px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: #9ca3af;
  margin-top: 6px;
}

.module-row {
  margin-bottom: 24px;
}

.module-row .el-col {
  margin-bottom: 24px;
}

.module-card {
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  height: 220px;
}

.module-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.12);
}

.module-card :deep(.el-card__body) {
  padding: 32px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 14px;
  height: 100%;
  justify-content: center;
}

.module-icon {
  width: 72px;
  height: 72px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.module-title {
  font-size: 20px;
  font-weight: 700;
  color: #1f2937;
}

.module-desc {
  font-size: 14px;
  color: #9ca3af;
  line-height: 1.5;
  max-width: 220px;
}
</style>
