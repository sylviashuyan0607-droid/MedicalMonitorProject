<template>
  <div class="admin-wrapper">
    <div class="scanline"></div>
    
    <div class="admin-container">
      <header class="admin-header">
        <h1 class="title-text-glow">⚙️ 系统后台管理中心</h1>
        <p class="sub-hint">科研参数精调模式 (Real-time Config Mode)</p>
      </header>

      <main class="admin-content">
        <section class="glass-card admin-card">
          <h3 class="card-title-glow">核心算法阈值设置</h3>
          
          <div class="setting-form">
            <div class="form-item">
              <div class="label-group">
                <span class="label">压力判定阈值 (Pressure Threshold):</span>
                <span class="desc">触发“有人坐下”及载荷波动的最小克重</span>
              </div>
              <div class="input-group">
                <input type="number" v-model="settings.threshold" class="c-input-glow" step="10">
                <span class="unit cyan-glow">g</span>
              </div>
            </div>

            <div class="form-item margin-top-md">
              <div class="label-group">
                <span class="label">姿态预警判定时限 (Time Limit):</span>
                <span class="desc">重心持续偏离超过此时间则触发红框警告</span>
              </div>
              <div class="input-group">
                <input type="number" v-model="settings.timeLimit" class="c-input-glow" step="60">
                <span class="unit cyan-glow">s</span>
              </div>
            </div>
            <div class="form-item margin-top-md">
              <div class="label-group">
                <span class="label">压力异常比例阈值 (Pressure Ratio):</span>
                <span class="desc">压力超过标准姿态多少倍算异常</span>
              </div>
              <div class="input-group">
                <input type="number" v-model="settings.pressureRatioThreshold" class="c-input-glow" step="0.05" min="1.0">
                <span class="unit cyan-glow">倍</span>
              </div>
            </div>
            <div class="form-item margin-top-md">
              <div class="label-group">
                <span class="label">重心偏移阈值 (COP Distance):</span>
                <span class="desc">单位：厘米，超过则判定重心偏移</span>
              </div>
              <div class="input-group">
                <input type="number" v-model="settings.copDistanceThreshold" class="c-input-glow" step="0.2" min="0">
                <span class="unit cyan-glow">cm</span>
              </div>
            </div>
          </div>
        </section>

        <section class="glass-card admin-card margin-top-sm">
          <h3 class="card-title-glow">设备通讯状态</h3>
          <div class="status-grid">
            <div class="status-box">
              <span class="s-l">后端 API 地址</span>
              <span class="s-v">{{ backendApiUrl }}</span>
            </div>
            <div class="status-box">
              <span class="s-l">后端连接状态</span>
              <span class="s-v" :class="backendReachable ? 'green-glow' : 'danger-text'">
                {{ backendReachable ? '已连接' : '未连接' }}
              </span>
            </div>
            <div class="status-box" style="flex: 1 1 100%;">
              <button class="check-btn" @click="checkBackendConnection" :disabled="isCheckingBackend">
                {{ isCheckingBackend ? '检测中...' : '后台连接测试 / 刷新' }}
              </button>
              <span class="status-desc">{{ backendStatusMessage }}</span>
            </div>
          </div>
          <div v-if="!backendReachable" class="error-tip">
            {{ backendErrorMessage }}
          </div>
        </section>

        <footer class="admin-footer">
          <button class="nav-btn ghost-cyan-glow btn-large" @click="saveSettings">
            同步设置到后端算法
          </button>
          <button class="nav-btn return-btn" @click="goBackToDashboard">
            返回实时监测大屏
          </button>
        </footer>
      </main>
    </div>

    <div class="bottom-signal-tip">
      <span class="pulse-dot"></span> 管理模式已激活
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const backendApiUrl = 'http://localhost:5000'
const backendReachable = ref(true)
const backendErrorMessage = ref('')
const backendStatusMessage = ref('正在检测后端连接...')
const isCheckingBackend = ref(false)

// 响应式配置数据
const settings = reactive({
  threshold: 30, // 默认值，加载后会覆盖
  timeLimit: 120,
  pressureRatioThreshold: 1.2,
  copDistanceThreshold: 1.2
})

const router = useRouter()   // ✅ 修复2：声明 router 实例

// 加载时从后端获取配置
const setBackendError = (message, error) => {
  backendReachable.value = false
  backendErrorMessage.value = message
  backendStatusMessage.value = '后端连接异常'
  if (error) console.error(message, error)
}

const setBackendOk = (message) => {
  backendReachable.value = true
  backendErrorMessage.value = ''
  backendStatusMessage.value = message
}

const loadBackendConfig = async () => {
  try {
    const response = await fetch(`${backendApiUrl}/api/get_settings`, { cache: 'no-cache' })
    if (!response.ok) {
      throw new Error(`后端返回 ${response.status}`)
    }
    const data = await response.json()
    setBackendOk('后端连接正常，配置已加载')
    settings.threshold = data.threshold
    settings.timeLimit = data.timeLimit
    settings.pressureRatioThreshold = data.pressureRatioThreshold ?? settings.pressureRatioThreshold
    settings.copDistanceThreshold = data.copDistanceThreshold ?? settings.copDistanceThreshold
  } catch (error) {
    setBackendError('无法连接到后端 app.py，请确保后端程序正在运行。', error)
  }
}

onMounted(async () => {
  await loadBackendConfig()
})

// 在 <script setup> 中修改 goBackToDashboard 函数
const goBackToDashboard = () => {
  router.replace('/dashboard').catch(err => {
    console.error("路由跳转异常:", err);
    window.location.href = '/dashboard'; // 保底方案
  });
}

// 保存并同步设置至 Python 后端
const checkBackendConnection = async (showAlert = false) => {
  isCheckingBackend.value = true
  try {
    const response = await fetch(`${backendApiUrl}/api/get_settings`, { cache: 'no-cache' })
    if (!response.ok) {
      throw new Error(`后端返回 ${response.status}`)
    }
    const data = await response.json()
    setBackendOk('后端连接正常，配置已刷新。')
    settings.threshold = data.threshold
    settings.timeLimit = data.timeLimit
    settings.pressureRatioThreshold = data.pressureRatioThreshold ?? settings.pressureRatioThreshold
    settings.copDistanceThreshold = data.copDistanceThreshold ?? settings.copDistanceThreshold
    if (showAlert) alert('✅ 后端连接正常，配置已刷新。')
  } catch (error) {
    setBackendError(`后端连接失败：${error.message}`, error)
    if (showAlert) alert(`❌ 后端连接失败：${error.message}`)
  } finally {
    isCheckingBackend.value = false
  }
}

const saveSettings = async () => {
  try {
    const response = await fetch(`${backendApiUrl}/api/update_settings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        threshold: settings.threshold,
        timeLimit: settings.timeLimit,
        pressureRatioThreshold: settings.pressureRatioThreshold,
        copDistanceThreshold: settings.copDistanceThreshold
      })
    })
    
    if (!response.ok) {
      throw new Error(`后端返回 ${response.status}`)
    }
    const result = await response.json()
    if (result.status === 'success') {
      setBackendOk('后端已保存设置并连接正常。')
      alert("✅ 同步成功！后端算法标准已即时更新。")
      window.dispatchEvent(new Event('backend-settings-updated'))
    }
  } catch (error) {
    setBackendError(`后端保存失败：${error.message}`, error)
    alert(`❌ 后端保存失败：${error.message}`)
  }
}
</script>

<style scoped>
/* 样式保持不变，与原来相同 */
.admin-wrapper {
  min-height: 100vh; width: 100vw; background: #000d1a; color: #fff;
  display: flex; justify-content: center; align-items: flex-start;
  position: fixed; top: 0; left: 0; overflow: auto; padding: 20px;
  font-family: 'Segoe UI', sans-serif;
}
.scanline {
  position: absolute; top: 0; left: 0; width: 100%; height: 2px;
  background: rgba(0, 193, 222, 0.1);
  animation: scan 8s linear infinite; z-index: 1;
}
.admin-container {
  width: min(860px, calc(100vw - 40px)); z-index: 10; padding: 40px;
  background: rgba(0, 13, 26, 0.8);
  border: 1px solid rgba(0, 193, 222, 0.2);
  border-radius: 20px; box-shadow: 0 0 50px rgba(0,0,0,0.5);
  max-height: calc(100vh - 60px); overflow-y: auto;
}
.admin-header { text-align: center; margin-bottom: 40px; }
.sub-hint { color: #888; font-size: 14px; margin-top: 10px; letter-spacing: 1px; }
.glass-card {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(0, 193, 222, 0.15);
  border-radius: 15px; padding: 25px;
}
.form-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: 15px 0; border-bottom: 1px solid rgba(255,255,255,0.05);
}
.label-group { display: flex; flex-direction: column; }
.label { font-size: 16px; font-weight: bold; color: #fff; }
.desc { font-size: 12px; color: #666; margin-top: 4px; }
.input-group { display: flex; align-items: center; gap: 10px; }
.c-input-glow {
  background: #000; border: 1px solid #1a3a4a; color: #00c1de;
  width: 100px; height: 35px; text-align: right;
  padding-right: 10px; border-radius: 6px; font-weight: bold;
  font-family: 'Courier New', monospace; font-size: 18px;
}
.c-input-glow:focus { border-color: #00c1de; outline: none; box-shadow: 0 0 10px #00c1de; }
.admin-footer { margin-top: 40px; display: flex; flex-direction: column; gap: 15px; align-items: center; }
.btn-large { width: 100%; height: 50px; font-size: 18px; letter-spacing: 2px; }
.return-btn { background: transparent; border: none; color: #666; cursor: pointer; text-decoration: underline; }
.return-btn:hover { color: #00c1de; }
.status-grid { display: flex; flex-wrap: wrap; gap: 20px; margin-top: 10px; }
.status-box {
  flex: 1; background: rgba(0,0,0,0.3); padding: 15px; border-radius: 10px;
  display: flex; flex-direction: column; align-items: center; gap: 10px;
}
.check-btn {
  width: 100%; background: #081b29; border: 1px solid #00c1de; color: #00c1de;
  padding: 10px 0; border-radius: 10px; cursor: pointer; transition: background 0.2s;
}
.check-btn:hover:not(:disabled) {
  background: rgba(0, 193, 222, 0.1);
}
.check-btn:disabled {
  opacity: 0.6; cursor: not-allowed;
}
.status-desc { font-size: 12px; color: #9cd9e8; text-align: center; }
.s-l { font-size: 11px; color: #555; }
.s-v { font-size: 14px; font-family: monospace; }
.error-tip { margin-top: 12px; color: #ff7c7e; font-size: 13px; border: 1px solid rgba(255,124,126,0.3); padding: 10px 12px; border-radius: 10px; background: rgba(255,124,126,0.08); }
.title-text-glow { font-size: 32px; font-weight: 900; color: #fff; text-shadow: 0 0 15px #00c1de; }
.card-title-glow { font-size: 16px; font-weight: bold; color: #00c1de; border-left: 4px solid #00c1de; padding-left: 12px; margin-bottom: 20px; }
.cyan-glow { color: #00c1de; text-shadow: 0 0 8px rgba(0,193,222,0.6); }
.green-glow { color: #52c41a; text-shadow: 0 0 8px #52c41a; }
.ghost-cyan-glow {
  background: transparent; border: 1px solid #00c1de; color: #00c1de;
  border-radius: 6px; cursor: pointer; transition: 0.3s;
  box-shadow: 0 0 10px rgba(0, 193, 222, 0.3);
}
.ghost-cyan-glow:hover { background: rgba(0, 193, 222, 0.15); box-shadow: 0 0 20px #00c1de; }
.bottom-signal-tip { position: absolute; bottom: 20px; right: 30px; font-size: 12px; color: #00c1de; display: flex; align-items: center; gap: 8px; font-style: italic; }
.pulse-dot { width: 8px; height: 8px; background: #52c41a; border-radius: 50%; box-shadow: 0 0 10px #52c41a; animation: pulse 2s infinite; }
@keyframes scan { from { top: -10%; } to { top: 110%; } }
@keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
.margin-top-md { margin-top: 20px; }
.margin-top-sm { margin-top: 15px; }
</style>