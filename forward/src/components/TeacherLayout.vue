<template>
  <el-container class="layout">
    <el-aside width="240px" class="sidebar">
      <div class="logo">
        <el-icon :size="28"><School /></el-icon>
        <span>教师工作台</span>
      </div>

      <!-- 教师信息卡片 -->
      <div class="profile-card" v-if="teacherInfo">
        <div class="profile-info">
          <div class="profile-name">{{ teacherInfo.name || teacherInfo.username }}</div>
          <div class="profile-no">工号: {{ teacherInfo.teacher_no }}</div>
        </div>
        <div class="profile-meta">
          <el-tag size="small" type="info">{{ teacherInfo.title || '教师' }}</el-tag>
          <div class="profile-dept" :title="teacherInfo.department">
            <el-icon><OfficeBuilding /></el-icon>
            {{ teacherInfo.department || '暂无院系信息' }}
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
        <el-menu-item index="/teacher/dashboard">
          <el-icon><DataBoard /></el-icon>
          <span>课程概览</span>
        </el-menu-item>
        <el-menu-item index="/teacher/upload">
          <el-icon><Upload /></el-icon>
          <span>数据上传</span>
        </el-menu-item>
        <el-menu-item index="/teacher/resources">
          <el-icon><FolderOpened /></el-icon>
          <span>教学资源</span>
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
              <span>{{ teacherInfo?.name || '教师' }}</span>
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
      <el-descriptions :column="1" border v-if="teacherInfo">
        <el-descriptions-item label="姓名">{{ teacherInfo.name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="用户名">{{ teacherInfo.username }}</el-descriptions-item>
        <el-descriptions-item label="工号">{{ teacherInfo.teacher_no }}</el-descriptions-item>
        <el-descriptions-item label="职称">{{ teacherInfo.title || '-' }}</el-descriptions-item>
        <el-descriptions-item label="院系">{{ teacherInfo.department || '-' }}</el-descriptions-item>
        <el-descriptions-item label="办公电话">{{ teacherInfo.phone || '-' }}</el-descriptions-item>
        <el-descriptions-item label="办公室">{{ teacherInfo.office || '-' }}</el-descriptions-item>
        <el-descriptions-item label="邮箱">{{ teacherInfo.email || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </el-container>
</template>

<script setup>
import { School, DataBoard, Upload, UserFilled, ArrowDown, FolderOpened, OfficeBuilding } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { getCurrentTeacherProfile } from '@/api/admin'
import { ElMessage } from 'element-plus'

const router = useRouter()
const teacherInfo = ref(null)
const profileDialogVisible = ref(false)

// 获取教师信息
const loadTeacherInfo = async () => {
  try {
    const res = await getCurrentTeacherProfile()
    if (res.code === 200) {
      teacherInfo.value = res.data
    }
  } catch (error) {
    console.error('获取教师信息失败:', error)
    // 如果API失败，使用 auth store 中的登录用户信息
    const authStore = useAuthStore()
    const user = authStore.userInfo
    if (user && user.role === 'teacher') {
      teacherInfo.value = {
        username: user.username,
        name: user.name || user.username,
        teacher_no: '未设置',
        title: '教师',
        department: '未设置'
      }
    }
  }
}

const showProfile = () => {
  profileDialogVisible.value = true
}

const logout = () => {
  const authStore = useAuthStore()
  authStore.logout()
  router.push('/login')
}

onMounted(() => {
  loadTeacherInfo()
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

/* 教师信息卡片 */
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
