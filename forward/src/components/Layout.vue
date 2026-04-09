<template>
  <el-container class="layout">
    <el-aside width="200px">
      <div class="logo">学业预警系统</div>
      <el-menu :default-active="$route.path" router>
        <el-menu-item index="/student/analysis">
          <el-icon><DataAnalysis /></el-icon>
          <span>学情分析</span>
        </el-menu-item>
        <el-menu-item index="/student/courses">
          <el-icon><Reading /></el-icon>
          <span>我的课程</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header>
        <span>学生端</span>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { DataAnalysis, Reading } from '@element-plus/icons-vue'
</script>

<style scoped>
.layout {
  height: 100vh;
}
.logo {
  height: 60px;
  line-height: 60px;
  text-align: center;
  font-size: 18px;
  font-weight: bold;
  color: #3b82f6;
  border-bottom: 1px solid #e2e8f0;
}
.el-aside {
  background: white;
  box-shadow: 2px 0 8px rgba(0,0,0,0.1);
}
.el-header {
  background: white;
  line-height: 60px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
.el-main {
  background: #f5f7fa;
}
</style>
