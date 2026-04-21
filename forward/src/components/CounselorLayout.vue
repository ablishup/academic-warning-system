<template>
  <el-container class="layout">
    <el-aside width="240px" class="sidebar">
      <div class="logo">
        <el-icon :size="28"><School /></el-icon>
        <span>辅导员工作台</span>
      </div>

      <!-- 辅导员信息卡片 -->
      <div class="profile-card" v-if="counselorInfo">
        <el-avatar :size="48" :style="{ background: '#10b981' }">
          {{ counselorInfo.name?.charAt(0) || 'C' }}
        </el-avatar>
        <div class="profile-info">
          <div class="profile-name">{{ counselorInfo.name || counselorInfo.username }}</div>
          <div class="profile-no">工号: {{ counselorInfo.employee_no }}</div>
        </div>
        <div class="profile-meta">
          <el-tag size="small" type="success">辅导员</el-tag>
          <div class="profile-dept" :title="counselorInfo.department">
            <el-icon><OfficeBuilding /></el-icon>
            {{ counselorInfo.department || '暂无院系信息' }}
          </div>
        </div>
      </div>

      <el-menu
        :default-active="$route.path"
        router
        class="sidebar-menu"
        background-color="#1e293b"
        text-color="#94a3b8"
        active-text-color="#ffffff"
      >
        <el-menu-item index="/counselor/dashboard">
          <el-icon><DataBoard /></el-icon>
          <span>学情总览</span>
        </el-menu-item>
        <el-menu-item index="/counselor/warnings">
          <el-icon><Warning /></el-icon>
          <span>预警管理</span>
        </el-menu-item>
        <el-menu-item index="/counselor/interventions">
          <el-icon><FirstAidKit /></el-icon>
          <span>干预记录</span>
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
              <el-avatar :size="32" :style="{ background: '#10b981' }">
                {{ counselorInfo?.name?.charAt(0) || 'C' }}
              </el-avatar>
              <span>{{ counselorInfo?.name || '辅导员' }}</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="showProfile">个人信息</el-dropdown-item>
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

    <!-- 个人信息详情弹窗 -->
    <el-dialog v-model="profileDialogVisible" title="个人信息" width="500px">
      <el-descriptions :column="1" border v-if="counselorInfo">
        <el-descriptions-item label="姓名">{{ counselorInfo.name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="用户名">{{ counselorInfo.username }}</el-descriptions-item>
        <el-descriptions-item label="工号">{{ counselorInfo.employee_no }}</el-descriptions-item>
        <el-descriptions-item label="院系">{{ counselorInfo.department || '-' }}</el-descriptions-item>
        <el-descriptions-item label="联系电话">{{ counselorInfo.phone || '-' }}</el-descriptions-item>
        <el-descriptions-item label="办公地点">{{ counselorInfo.office || '-' }}</el-descriptions-item>
        <el-descriptions-item label="邮箱">{{ counselorInfo.email || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </el-container>
</template>

<script setup>
import { School, DataBoard, Warning, FirstAidKit, UserFilled, ArrowDown, OfficeBuilding, ChatDotRound } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { ref, onMounted } from 'vue'
import { getCurrentCounselorProfile } from '@/api/admin'
import { ElMessage } from 'element-plus'

const router = useRouter()
const counselorInfo = ref(null)
const profileDialogVisible = ref(false)

// 获取辅导员信息
const loadCounselorInfo = async () => {
  try {
    const res = await getCurrentCounselorProfile()
    if (res.code === 200) {
      counselorInfo.value = res.data
    }
  } catch (error) {
    console.error('获取辅导员信息失败:', error)
    // 如果API失败，使用本地存储的用户信息
    const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
    if (userInfo.role === 'counselor') {
      counselorInfo.value = {
        username: userInfo.username,
        name: userInfo.name || userInfo.username,
        employee_no: '未设置',
        department: '未设置'
      }
    }
  }
}

const showProfile = () => {
  profileDialogVisible.value = true
}

const logout = () => {
  localStorage.removeItem('userInfo')
  router.push('/login')
}

onMounted(() => {
  loadCounselorInfo()
})
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

/* 辅导员信息卡片 */
.profile-card {
  padding: 20px 16px;
  margin: 12px;
  background: linear-gradient(135deg, #334155 0%, #1e293b 100%);
  border-radius: 12px;
  border: 1px solid #475569;
  text-align: center;
}

.profile-info {
  margin-top: 12px;
}

.profile-name {
  color: white;
  font-size: 16px;
  font-weight: 600;
}

.profile-no {
  color: #94a3b8;
  font-size: 12px;
  margin-top: 4px;
}

.profile-meta {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #475569;
}

.profile-dept {
  color: #94a3b8;
  font-size: 12px;
  margin-top: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.sidebar-menu {
  border-right: none;
  margin-top: 8px;
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
