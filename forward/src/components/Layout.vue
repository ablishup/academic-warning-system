<template>
  <el-container class="layout">
    <el-aside width="220px" class="sidebar">
      <div class="logo">
        <el-icon :size="28"><School /></el-icon>
        <span>学业预警系统</span>
      </div>
      <el-menu
        :default-active="$route.path"
        router
        class="sidebar-menu"
        background-color="#1e293b"
        text-color="#94a3b8"
        active-text-color="#ffffff"
      >
        <el-menu-item index="/student/analysis">
          <el-icon><DataAnalysis /></el-icon>
          <span>学情分析</span>
        </el-menu-item>
        <el-menu-item index="/student/courses">
          <el-icon><Collection /></el-icon>
          <span>我的课程</span>
        </el-menu-item>
        <el-menu-item index="/student/course-resources">
          <el-icon><FolderOpened /></el-icon>
          <span>课程资源</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <breadcrumb />
        </div>
        <div class="header-right">
          <el-dropdown>
            <span class="user-info">
              <span>学生</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { School, DataAnalysis, Collection, FolderOpened, UserFilled, ArrowDown } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const logout = () => {
  localStorage.removeItem('userInfo')
  router.push('/login')
}
</script>

<style scoped>
.layout {
  height: 100vh;
}

.sidebar {
  background: #1e293b;
  box-shadow: 2px 0 8px rgba(0,0,0,0.15);
}

.logo {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: white;
  font-size: 18px;
  font-weight: 600;
  border-bottom: 1px solid #334155;
}

.sidebar-menu {
  border-right: none;
  margin-top: 16px;
}

.sidebar-menu :deep(.el-menu-item) {
  height: 50px;
  line-height: 50px;
  margin: 4px 12px;
  border-radius: 8px;
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background: #3b82f6;
}

.sidebar-menu :deep(.el-menu-item:hover) {
  background: #334155;
}

.header {
  background: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 1px 4px rgba(0,0,0,0.1);
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: center;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 12px;
  border-radius: 8px;
  transition: background 0.2s;
}

.user-info:hover {
  background: #f1f5f9;
}

.main-content {
  background: #f8fafc;
  padding: 24px;
  overflow-y: auto;
}
</style>
