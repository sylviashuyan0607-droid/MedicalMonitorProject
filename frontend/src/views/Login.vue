<template>
  <div class="login-page" :style="{ backgroundImage: `url(${bgImage})` }">
    <div class="login-overlay"></div>
    <div class="glow-effect"></div>
    <div class="scan-line"></div>

    <div class="login-container">
      <!-- 系统标识区域 -->
      <div class="system-header">
        <h1 class="system-title">人体姿态智能监测系统</h1>
        <div class="sys-id">SYS_ID:MED-PRO-01</div>
        <div class="auth-label">用户身份验证</div>
      </div>

      <!-- 选项卡卡片 -->
      <el-card class="login-card cyber-card">
        <el-tabs v-model="activeName" type="card" class="cyber-tabs">
          <!-- 系统登录 -->
          <el-tab-pane label="系统登录" name="login">
            <el-form :model="loginForm" label-width="120px" label-position="right" class="cyber-form">
              <el-form-item label="实验人员ID：">
                <el-input v-model="loginForm.username" placeholder="请输入实验人员ID" />
              </el-form-item>
              <el-form-item label="访问密钥：">
                <el-input v-model="loginForm.password" type="password" placeholder="请输入访问密钥" />
              </el-form-item>
              <el-button type="primary" @click="handleLogin" class="cyber-btn">验证授权并登录</el-button>
            </el-form>
          </el-tab-pane>

          <!-- 用户注册 -->
          <el-tab-pane label="用户注册" name="register">
            <el-form :model="registerForm" label-width="120px" label-position="right" class="cyber-form">
              <el-form-item label="实验人员ID：">
                <el-input v-model="registerForm.username" placeholder="请输入实验人员ID" />
              </el-form-item>
              <el-form-item label="访问密钥：">
                <el-input v-model="registerForm.password" type="password" placeholder="请设置访问密钥" />
              </el-form-item>
              <el-form-item label="确认密钥：">
                <el-input v-model="registerForm.confirmPassword" type="password" placeholder="请再次输入访问密钥" />
              </el-form-item>
              <el-button type="primary" @click="handleRegister" class="cyber-btn">注册新账号</el-button>
            </el-form>
          </el-tab-pane>

          <!-- 找回密码 -->
          <el-tab-pane label="找回密码" name="forgot">
            <el-form :model="forgotForm" label-width="120px" label-position="right" class="cyber-form">
              <el-form-item label="实验人员ID：">
                <el-input v-model="forgotForm.username" placeholder="请输入您的实验人员ID" />
              </el-form-item>
              <el-form-item label="新访问密钥：">
                <el-input v-model="forgotForm.newPassword" type="password" placeholder="请设置新访问密钥" />
              </el-form-item>
              <el-form-item label="确认新密钥：">
                <el-input v-model="forgotForm.confirmNewPassword" type="password" placeholder="请再次输入新密钥" />
              </el-form-item>
              <el-button type="primary" @click="handleResetPassword" class="cyber-btn">重置密钥</el-button>
            </el-form>
          </el-tab-pane>
        </el-tabs>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'  // 使用 Element Plus 的消息提示（可选）
import bgImage from 'D:\\MedicalMonitorProject\\frontend\\src\\assets\\login_page_image.jpg'

const router = useRouter()
const activeName = ref('login')

// 登录表单
const loginForm = reactive({
  username: '',
  password: ''
})

// 注册表单
const registerForm = reactive({
  username: '',
  password: '',
  confirmPassword: ''
})

// 找回密码表单
const forgotForm = reactive({
  username: '',
  newPassword: '',
  confirmNewPassword: ''
})

// 修改 handleLogin 函数
const handleLogin = async () => {
  if (!loginForm.username || !loginForm.password) {
    ElMessage.error('请填写完整的实验人员ID和访问密钥');
    return;
  }

  ElMessage.success('身份验证通过，正在进入系统...');

  setTimeout(() => {
    router.replace('/dashboard').catch(err => {
      console.error("路由跳转异常:", err);
      window.location.href = '/dashboard';
    });
  }, 300);
}

// 注册处理
const handleRegister = () => {
  if (!registerForm.username || !registerForm.password) {
    ElMessage.error ('请填写完整的实验人员ID和访问密钥')
    return
  }
  if (registerForm.password !== registerForm.confirmPassword) {
    ElMessage.error('两次输入的访问密钥不一致')
    return
  }
  alert('注册成功！请使用新账号登录')
  activeName.value = 'login'
  registerForm.username = ''
  registerForm.password = ''
  registerForm.confirmPassword = ''
}

// 重置密码处理
const handleResetPassword = () => {
  if (!forgotForm.username || !forgotForm.newPassword) {
    alert('请填写实验人员ID和新访问密钥')
    return
  }
  if (forgotForm.newPassword !== forgotForm.confirmNewPassword) {
    alert('两次输入的新密钥不一致')
    return
  }
  alert('密码重置成功！请使用新密钥登录')
  activeName.value = 'login'
  forgotForm.username = ''
  forgotForm.newPassword = ''
  forgotForm.confirmNewPassword = ''
}
</script>

<style scoped>
/* ========== 全局样式 ========== */
.login-page {
  height: 100vh;
  width: 100vw;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  overflow: hidden;
  font-family: 'Share Tech Mono', 'Courier New', monospace;
}

/* 半透明遮罩 */
.login-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.65);
  backdrop-filter: blur(10px);
  z-index: 1;
}

/* 动态光晕 */
.glow-effect {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle at center, rgba(0, 193, 222, 0.2), transparent 70%);
  transform: translate(-50%, -50%);
  pointer-events: none;
  z-index: 1;
  animation: pulseGlow 4s infinite;
}

/* 扫描线 */
.scan-line {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background: linear-gradient(90deg, transparent, #0ff, #f0f, transparent);
  opacity: 0.6;
  animation: scanMove 6s infinite;
  z-index: 2;
}

/* 主容器 */
.login-container {
  width: 520px;
  z-index: 3;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 系统标识区域 */
.system-header {
  text-align: center;
  margin-bottom: 10px;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(8px);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid rgba(0, 193, 222, 0.4);
  box-shadow: 0 0 15px rgba(0, 193, 222, 0.2);
}

.system-title {
  font-size: 28px;
  font-weight: bold;
  color: #fff;
  text-shadow: 0 0 8px rgba(255, 255, 255, 0.3);
  margin: 0 0 8px 0;
  letter-spacing: 2px;
}

.sys-id {
  font-size: 14px;
  color: #0ff;
  letter-spacing: 1px;
  font-family: monospace;
  margin-bottom: 12px;
  text-shadow: 0 0 3px #0ff;
}

.auth-label {
  font-size: 16px;
  color: #ccf;
  border-top: 1px solid rgba(0, 193, 222, 0.3);
  padding-top: 12px;
  display: inline-block;
  width: auto;
  margin: 0 auto;
  font-weight: 500;
}

/* 卡片样式 */
.cyber-card {
  background: rgba(10, 20, 30, 0.85) !important;
  backdrop-filter: blur(12px);
  border: 1px solid rgba(0, 193, 222, 0.5);
  border-radius: 16px;
  box-shadow: 0 0 20px rgba(0, 193, 222, 0.3), inset 0 0 10px rgba(0, 193, 222, 0.1);
  transition: all 0.3s ease;
}

.cyber-card:hover {
  box-shadow: 0 0 30px rgba(0, 193, 222, 0.5);
  border-color: rgba(0, 193, 222, 0.8);
}

/* Tabs 赛博风格 - 彻底去除白线，居中显示 */
.cyber-tabs :deep(.el-tabs__header) {
  margin-bottom: 20px;
  border: none !important;           /* 移除所有边框 */
  background: transparent;
}

/* 移除 nav-wrap 的所有伪元素边框 */
.cyber-tabs :deep(.el-tabs__nav-wrap) {
  border: none !important;
  position: relative;
  display: flex;
  justify-content: center;
}

.cyber-tabs :deep(.el-tabs__nav-wrap::after) {
  display: none !important;
  content: none !important;
}

.cyber-tabs :deep(.el-tabs__nav-wrap::before) {
  display: none !important;
  content: none !important;
}

/* 让 nav 容器居中 */
.cyber-tabs :deep(.el-tabs__nav) {
  display: flex;
  justify-content: center;
  width: auto;
  float: none;
  border: none !important;
  background: transparent;
}

/* 标签项样式 */
.cyber-tabs :deep(.el-tabs__item) {
  font-size: 16px;
  font-weight: 600;
  color: #8aa0b0;
  letter-spacing: 1px;
  transition: all 0.3s;
  text-transform: uppercase;
  background: transparent !important;
  border: none !important;
  padding: 0 20px;
}

.cyber-tabs :deep(.el-tabs__item.is-active) {
  color: #0ff;
  text-shadow: 0 0 8px #0ff;
  background: transparent !important;
}

.cyber-tabs :deep(.el-tabs__item:hover) {
  color: #0ff;
  text-shadow: 0 0 5px #0ff;
}

/* 激活标签的下划线（如果需要保留） */
.cyber-tabs :deep(.el-tabs__active-bar) {
  background-color: #0ff;
  height: 2px;
  box-shadow: 0 0 8px #0ff;
  bottom: 0;  /* 确保位置正确 */
}

.cyber-tabs :deep(.el-tabs__item:hover) {
  color: #0ff;
  text-shadow: 0 0 5px #0ff;
}

.cyber-tabs :deep(.el-tabs__active-bar) {
  background-color: #0ff;
  height: 2px;
  box-shadow: 0 0 8px #0ff;
}

/* 表单样式 */
.cyber-form {
  margin-top: 10px;
}

.cyber-form :deep(.el-form-item__label) {
  color: #0ff;
  font-weight: 500;
  text-shadow: 0 0 3px rgba(0, 255, 255, 0.5);
  font-family: monospace;
  white-space: nowrap;
}

.cyber-form :deep(.el-input__wrapper) {
  background: rgba(0, 0, 0, 0.6) !important;
  border: 1px solid #0ff !important;
  box-shadow: 0 0 5px rgba(0, 255, 255, 0.3);
  transition: all 0.3s;
}

.cyber-form :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 10px rgba(0, 255, 255, 0.6);
  border-color: #0ff;
}

.cyber-form :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 12px #0ff;
  border-color: #0ff;
}

.cyber-form :deep(.el-input__inner) {
  color: #0ff;
  font-family: monospace;
}

.cyber-form :deep(.el-input__inner::placeholder) {
  color: #2f6f7a;
}

/* 按钮样式 */
.cyber-btn {
  width: 100%;
  background: transparent !important;
  border: 2px solid #0ff !important;
  color: #0ff !important;
  font-weight: bold;
  letter-spacing: 2px;
  text-transform: uppercase;
  transition: all 0.3s;
  box-shadow: 0 0 5px rgba(0, 255, 255, 0.3);
  margin-top: 10px;
  font-family: monospace;
}

.cyber-btn:hover {
  background: rgba(0, 255, 255, 0.2) !important;
  box-shadow: 0 0 20px #0ff !important;
  transform: translateY(-2px);
}

.cyber-btn:active {
  transform: translateY(0);
}

/* 动画 */
@keyframes pulseGlow {
  0%, 100% { opacity: 0.4; transform: translate(-50%, -50%) scale(1); }
  50% { opacity: 0.8; transform: translate(-50%, -50%) scale(1.05); }
}

@keyframes scanMove {
  0%, 100% { transform: translateX(0); opacity: 0.6; }
  20% { transform: translateX(5px); opacity: 0.8; }
  40% { transform: translateX(-5px); opacity: 0.4; }
  60% { transform: translateX(3px); opacity: 0.7; }
  80% { transform: translateX(-3px); opacity: 0.5; }
}
</style>