<template>
  <div class="login-page">
    <div class="login-container">
      <!-- 左侧品牌展示区 -->
      <div class="login-left">
        <div class="brand-section">
          <div class="logo">
            <el-icon :size="48" color="#fff"><School /></el-icon>
          </div>
          <h1 class="brand-title">学业预警系统</h1>
          <p class="brand-subtitle">Academic Early Warning System</p>
        </div>

        <div class="features-section">
          <div class="feature-item">
            <el-icon :size="24" color="#60a5fa"><DataAnalysis /></el-icon>
            <span>智能数据分析</span>
          </div>
          <div class="feature-item">
            <el-icon :size="24" color="#34d399"><Warning /></el-icon>
            <span>学业风险预警</span>
          </div>
          <div class="feature-item">
            <el-icon :size="24" color="#fbbf24"><User /></el-icon>
            <span>个性化学习建议</span>
          </div>
        </div>

        <div class="brand-footer">
          <p>毕业设计项目 | 2026</p>
        </div>
      </div>

      <!-- 右侧登录表单区 -->
      <div class="login-right">
        <div class="login-box">
          <div class="login-header">
            <h2>欢迎登录</h2>
            <p>请选择您的账号类型登录系统</p>
          </div>

          <el-form
            ref="loginFormRef"
            :model="form"
            :rules="rules"
            @submit.prevent="handleLogin"
            class="login-form"
          >
            <el-form-item prop="username">
              <el-input
                v-model="form.username"
                placeholder="请输入用户名"
                :prefix-icon="User"
                size="large"
                clearable
              />
            </el-form-item>

            <el-form-item prop="password">
              <el-input
                v-model="form.password"
                type="password"
                placeholder="请输入密码"
                :prefix-icon="Lock"
                size="large"
                show-password
                clearable
                @keyup.enter="handleLogin"
              />
            </el-form-item>

            <div class="login-options">
              <el-checkbox v-model="rememberMe">记住用户名</el-checkbox>
            </div>

            <el-form-item>
              <el-button
                type="primary"
                size="large"
                class="login-button"
                @click="handleLogin"
                :loading="loading"
              >
                登 录
              </el-button>
            </el-form-item>

            <div class="role-hint">
              <el-tag size="small" effect="plain">学生</el-tag>
              <el-tag size="small" effect="plain" type="success">教师</el-tag>
              <el-tag size="small" effect="plain" type="warning">辅导员</el-tag>
              <el-tag size="small" effect="plain" type="danger">管理员</el-tag>
              <span class="hint-text">四端共用</span>
            </div>
          </el-form>

          <div class="login-divider">
            <span>测试账号</span>
          </div>

          <div class="test-accounts">
            <div class="account-item" @click="fillAccount('admin', 'admin123')">
              <el-tag type="danger" size="small">管理员</el-tag>
              <span>admin / admin123</span>
            </div>
            <div class="account-item" @click="fillAccount('counselor', '123456')">
              <el-tag type="warning" size="small">辅导员</el-tag>
              <span>counselor / 123456</span>
            </div>
            <div class="account-item" @click="fillAccount('teacher', '123456')">
              <el-tag type="success" size="small">教师</el-tag>
              <span>teacher / 123456</span>
            </div>
            <div class="account-item" @click="fillAccount('student', '123456')">
              <el-tag type="primary" size="small">学生</el-tag>
              <span>student / 123456</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 背景装饰 -->
    <div class="bg-decoration bg-1"></div>
    <div class="bg-decoration bg-2"></div>
    <div class="bg-decoration bg-3"></div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { School, User, Lock, DataAnalysis, Warning } from '@element-plus/icons-vue'
import request from '@/api/request'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const loginFormRef = ref(null)
const loading = ref(false)
const rememberMe = ref(false)

// 表单数据
const form = reactive({
  username: '',
  password: ''
})

// 表单验证规则
const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, message: '用户名至少2个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6个字符', trigger: 'blur' }
  ]
}

// 角色跳转映射
const roleRedirects = {
  'student': '/student',
  'teacher': '/teacher',
  'counselor': '/counselor',
  'admin': '/admin'
}

// 登录处理
const handleLogin = async () => {
  if (!loginFormRef.value) return

  await loginFormRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true
    try {
      const res = await request({
        url: '/auth/login/',
        method: 'post',
        data: form
      })

      if (res.code === 200) {
        // 保存用户信息到 auth store
        authStore.login(res.data)

        // 记住用户名
        if (rememberMe.value) {
          localStorage.setItem('rememberedUsername', form.username)
        } else {
          localStorage.removeItem('rememberedUsername')
        }

        ElMessage.success('登录成功')

        // 根据角色跳转
        const role = res.data.role || 'student'
        const redirectPath = roleRedirects[role] || '/student'
        router.push(redirectPath)
      } else {
        ElMessage.error(res.message || '登录失败')
      }
    } catch (error) {
      ElMessage.error('登录失败，请检查用户名和密码')
    } finally {
      loading.value = false
    }
  })
}

// 填充测试账号
const fillAccount = (username, password) => {
  form.username = username
  form.password = password
}

// 页面加载时检查是否有记住的用户名
onMounted(() => {
  const remembered = localStorage.getItem('rememberedUsername')
  if (remembered) {
    form.username = remembered
    rememberMe.value = true
  }
})
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow: hidden;
}

/* 背景装饰 */
.bg-decoration {
  position: absolute;
  border-radius: 50%;
  opacity: 0.1;
  background: white;
}

.bg-1 {
  width: 400px;
  height: 400px;
  top: -100px;
  left: -100px;
}

.bg-2 {
  width: 300px;
  height: 300px;
  bottom: -50px;
  right: 10%;
}

.bg-3 {
  width: 200px;
  height: 200px;
  top: 20%;
  right: 5%;
}

/* 登录容器 */
.login-container {
  display: flex;
  width: 900px;
  min-height: 560px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 25px 80px rgba(0, 0, 0, 0.3);
  overflow: hidden;
  z-index: 1;
}

/* 左侧品牌区 */
.login-left {
  flex: 1;
  background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
  padding: 60px 50px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  color: white;
}

.brand-section {
  text-align: center;
}

.logo {
  width: 80px;
  height: 80px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 24px;
  backdrop-filter: blur(10px);
}

.brand-title {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 8px;
  letter-spacing: 2px;
}

.brand-subtitle {
  font-size: 14px;
  opacity: 0.8;
  font-weight: 300;
  letter-spacing: 1px;
}

.features-section {
  margin: 40px 0;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  margin-bottom: 16px;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.feature-item:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateX(8px);
}

.feature-item span {
  font-size: 15px;
  font-weight: 500;
}

.brand-footer {
  text-align: center;
  font-size: 12px;
  opacity: 0.6;
}

/* 右侧登录区 */
.login-right {
  flex: 1;
  padding: 60px 50px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-box {
  width: 100%;
  max-width: 340px;
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.login-header h2 {
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 8px;
}

.login-header p {
  font-size: 14px;
  color: #6b7280;
}

.login-form {
  margin-bottom: 24px;
}

.login-form :deep(.el-input__wrapper) {
  border-radius: 10px;
  padding: 4px 15px;
}

.login-options {
  display: flex;
  justify-content: flex-start;
  margin-bottom: 20px;
}

.login-button {
  width: 100%;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 500;
  height: 44px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

.login-button:hover {
  background: linear-gradient(135deg, #5a6fd6 0%, #6a4190 100%);
}

.role-hint {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 16px;
}

.hint-text {
  font-size: 12px;
  color: #9ca3af;
  margin-left: 8px;
}

.login-divider {
  position: relative;
  text-align: center;
  margin: 20px 0;
}

.login-divider::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background: #e5e7eb;
}

.login-divider span {
  position: relative;
  background: white;
  padding: 0 12px;
  font-size: 12px;
  color: #9ca3af;
}

.test-accounts {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.account-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  background: #f9fafb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 13px;
  color: #4b5563;
}

.account-item:hover {
  background: #f3f4f6;
  transform: translateX(4px);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-container {
    width: 90%;
    flex-direction: column;
  }

  .login-left {
    padding: 40px 30px;
    min-height: auto;
  }

  .features-section {
    display: none;
  }

  .login-right {
    padding: 40px 30px;
  }
}
</style>
