<template>
  <div class="dashboard-wrapper">
    <div class="grid-bg"></div>

    <header class="custom-header">
      <div class="header-content-wrapper">
        <h1 class="title-text-glow">柔性传感器人体姿态智能监测系统</h1>
        <div class="center-status-wrapper">
          <div class="floating-status-pill" :class="statusClass">
            {{ postureStatus }}
          </div>
        </div>
        <div class="header-right">
          <div class="time-box">{{ currentTime }}</div>
          <button v-if="!isReading" class="nav-btn ghost-cyan-glow" @click="connectSerial" :disabled="!isWebSerialSupported">
            连接串口
          </button>
          <button v-else class="nav-btn ghost-cyan-glow" @click="disconnectSerial">
            断开串口
          </button>
          <button class="nav-btn ghost-cyan-glow" @click="$router.push('/admin')">后台管理</button>
          <button class="nav-btn ghost-cyan-glow logout-btn" @click="logout">退出登录</button>
        </div>
      </div>
    </header>

    <main class="main-content">
      <!-- 左侧面板：添加 ref 用于同步滚动 -->
      <section class="grid-cell left-panel scroll-y" ref="leftScrollRef">
        <div class="glass-card">
          <h3 class="card-title-glow">实时载荷数值 (A0-A3)</h3>
          <div class="sensor-values-v3">
            <div v-for="(v, i) in pressures" :key="i" class="val-row-v3">
              <span class="s-label">SENSOR-0{{i+1}}</span>
              <div class="s-bar-bg">
                <div class="s-bar-fill" :style="{ width: Math.min(v/500 * 100, 100) + '%' }"></div>
              </div>
              <span class="s-num cyan-glow">{{ v.toFixed(1) }} g</span>
            </div>
          </div>
          <div class="footer-stats-bar">
            <div class="f-stat">总载荷 <span class="cyan-glow">{{ totalLoad.toFixed(1) }} g</span></div>
            <div class="f-stat">系统采样率 <span class="green-glow">40 Hz</span></div>
          </div>
        </div>

        <div class="glass-card margin-top-sm">
          <h3 class="card-title-glow">标准姿态定标</h3>
          <div class="aligned-setting-list">
            <div class="calib-baseline-row">
              <span class="label-sm">1. 硬件归零：</span>
              <button class="m-btn-glow" @click="calibrateBaseline" :disabled="calibrating">
                {{ calibrating ? '归零中...' : '一键归零' }}
              </button>
              <p class="desc">请保持传感器空载，点击后等待5秒</p>
            </div>
            
            <div class="calib-baseline-row margin-top-sm">
              <span class="label-sm">2. 录入标准坐姿：</span>
              <p class="desc">端正坐好后点击，系统将以此为基准监测</p>
              <button class="m-btn-glow primary-border" @click="captureStandardPosture" :disabled="calibrating || !isCalibrated">
                录入当前姿态为标准
              </button>
              <div v-if="calibrating" class="hint-text">
                ⚠️ 硬件归零中，请等待“归零中...”状态结束后再录入标准姿态。
              </div>
              <div v-else-if="!isCalibrated" class="hint-text">
                ⚠️ 请先点击“一键归零”，等待归零完成后再录入标准姿态。
              </div>
              <div v-else-if="standardTotalLoad === 0" class="hint-text">
                ⚠️ 当前尚未录入标准压力值，请端正坐姿后点击“录入当前姿态为标准”
              </div>
              <div v-else class="ref-info-box">
                🎯 标准总载荷: {{ standardTotalLoad.toFixed(1) }}g &nbsp;| 
                重心: ({{ standardCop.x.toFixed(1) }}, {{ standardCop.y.toFixed(1) }})
              </div>
            </div>

            <div class="aligned-row margin-top-sm">
              <span>压力超限比例：</span>
              <div class="r-group">
                <input type="number" class="c-input-glow" v-model.number="pressureRatioThreshold" step="0.05" min="1.0">
                <span class="unit cyan-glow">倍</span>
              </div>
            </div>
            <div class="aligned-row margin-top-sm">
              <span>重心偏移容忍：</span>
              <div class="r-group">
                <input type="number" class="c-input-glow" v-model.number="copDistanceThreshold" step="0.2" min="0">
                <span class="unit cyan-glow">cm</span>
              </div>
            </div>

            <div class="aligned-row margin-top-sm">
              <span>死区阈值：</span>
              <div class="r-group">
                <input type="number" class="c-input-glow" v-model.number="deadzoneThreshold" step="0.1" min="0" max="5">
                <span class="unit cyan-glow">g</span>
              </div>
            </div>
          </div>
        </div>

        <div class="glass-card margin-top-sm">
          <h3 class="card-title-glow">后台判定参数</h3>
          <div class="aligned-row">
            <span>离座最小载荷：</span>
            <span class="cyan-glow">{{ backendPressureThreshold.toFixed(1) }} g</span>
          </div>
          <div class="aligned-row margin-top-sm">
            <span>异常触发时长：</span>
            <span class="cyan-glow">{{ backendTimeLimit }} s</span>
          </div>
          <div class="aligned-row margin-top-sm">
            <span>压力异常比例阈值：</span>
            <span class="cyan-glow">{{ backendPressureRatioThreshold.toFixed(2) }}x</span>
          </div>
          <div class="aligned-row margin-top-sm">
            <span>重心偏移判定阈值：</span>
            <span class="cyan-glow">{{ backendCopDistanceThreshold.toFixed(2) }} cm</span>
          </div>
          <p class="desc">后台管理中设置变化时，此处会立即刷新并影响当前判定逻辑。</p>
        </div>

        <div class="glass-card margin-top-sm flex-fill-card">
          <h3 class="card-title-glow">分力向量分布</h3>
          <div class="radar-dom-container"><div ref="polarChartRef" class="echarts-dom"></div></div>
        </div>
      </section>

      <!-- 中央面板（不参与同步滚动） -->
      <section class="grid-cell center-stage">
        <div class="display-flex-column full-height">
          <div class="main-chart-outer flex-fill-main-v2">
            <div class="inline-card-header-v2">
              <h3 class="card-title-glow">重心偏离监测 (Toe 朝右)</h3>
            </div>
            <div class="main-chart-canvas-box">
              <div ref="mainChartRef" class="echarts-dom"></div>
            </div>
          </div>
          <div class="wave-chart-wrapper-v2 flex-shrink-0">
            <h4 class="sub-title-glow text-center">四路实时波形监控 (A0-A3)</h4>
            <div ref="multiWaveRef" style="width: 100%; height: 210px;"></div>
          </div>
        </div>
      </section>

      <!-- 右侧面板：添加 ref 用于同步滚动 -->
      <section class="grid-cell right-panel scroll-y" ref="rightScrollRef">
        <div class="glass-card">
          <h3 class="card-title-glow">重心详细参数</h3>
          <div class="stats-dark-row">
            <div class="stat-dark-item"><span class="stat-l">当前 X</span><span class="stat-v cyan-glow">{{ currentCop.x.toFixed(2) }}</span></div>
            <div class="stat-dark-item"><span class="stat-l">当前 Y</span><span class="stat-v green-glow">{{ currentCop.y.toFixed(2) }}</span></div>
          </div>
          <div class="stats-dark-row margin-top-sm">
            <div class="stat-dark-item"><span class="stat-l">压力比例</span><span class="stat-v" :class="pressureRatio >= pressureRatioThreshold ? 'danger-text' : 'safe-text'">{{ pressureRatio.toFixed(2) }}x</span></div>
            <div class="stat-dark-item"><span class="stat-l">重心偏移</span><span class="stat-v" :class="copDistance >= copDistanceThreshold ? 'danger-text' : 'safe-text'">{{ copDistance.toFixed(2) }} cm</span></div>
          </div>
        </div>

        <div class="glass-card margin-top-sm">
          <h3 class="card-title-glow">姿态时间分布 (H)</h3>
          <div class="pie-dom-container"><div ref="pieChartRef" class="echarts-dom"></div></div>
        </div>

        <!-- 自动滚动开关区域 -->
        <div class="glass-card margin-top-sm">
          <div class="auto-scroll-switch">
            <span class="label">📜 自动滚动模式</span>
            <label class="switch">
              <input type="checkbox" v-model="autoScrollEnabled" @change="toggleAutoScroll">
              <span class="slider round"></span>
            </label>
            <span class="hint">{{ autoScrollEnabled ? '开启中' : '已关闭' }}</span>
          </div>
        </div>

        <div class="glass-card margin-top-sm flex-fill-card">
          <h3 class="card-title-glow card-header-fixed">实时行为快讯</h3>
          <div class="alert-scroll-window">
            <ul class="alert-list-dynamic scrolling">
              <li v-for="(alert, index) in alertHistory" :key="index" :class="['modern-capsule', alert.type]">
                <span class="t">{{ alert.time }}</span><span class="m">{{ alert.msg }}</span>
              </li>
            </ul>
          </div>
        </div>

        <div class="bottom-signal-tip-fixed-v2">
          <span class="pulse-dot"></span> 后端数据流正常获取中...
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'

// ---------- Web Serial API 相关 ----------
// 检查浏览器支持
const isWebSerialSupported = 'serial' in navigator
let port = null
let reader = null
const isReading = ref(false)

// 串口配置（与后端保持一致）
const SERIAL_BAUD_RATE = 115200
const CALIB_FACTOR = 500.0 / 1023.0
const DEFAULT_DEADZONE = 0.1  // 默认死区阈值

const backendApiUrl = 'http://localhost:5000'

// 后端同步阈值
const backendPressureThreshold = ref(20)
const backendTimeLimit = ref(120)
const backendPressureRatioThreshold = ref(1.2)
const backendCopDistanceThreshold = ref(1.2)

// 可配置参数
const deadzoneThreshold = ref(DEFAULT_DEADZONE)

// 信号处理变量（与后端保持一致）
let baselines = [0.0, 0.0, 0.0, 0.0]
const isCalibrated = ref(false)
let calibrationCounter = 0
const CALIBRATION_SAMPLES = 50
// 归零期间的原始 ADC 上限。空载基线可能较高，过低会误判。
const CALIBRATION_RAW_PRESSURE_LIMIT = 150
let baselinePressureMax = 0
let baselineInvalidPressure = false
let calibrationNoiseG = 0
let calibrationTimer = null
const filterQueues = [[], [], [], []]
const rawPressures = ref([0, 0, 0, 0])
let serialInputAlreadyGram = null // 用于自动检测串口数据是否已为克单位

// ---------- Web Serial API 函数 ----------
// 请求用户选择串口
const connectSerial = async () => {
  if (!isWebSerialSupported) {
    alert('您的浏览器不支持 Web Serial API。请使用 Chrome 或 Edge 浏览器，并在 localhost 或 HTTPS 环境下运行。')
    return
  }

  try {
    // 如果之前有一个打开的端口，先断开它，避免重复打开
    if (port) {
      await disconnectSerial()
    }

    // 请求用户选择串口
    port = await navigator.serial.requestPort()
    
    // 打开串口
    await port.open({ 
      baudRate: SERIAL_BAUD_RATE,
      dataBits: 8,
      stopBits: 1,
      parity: 'none'
    })
    
    console.log('✅ 串口已连接')
    postureStatus.value = '✅ 串口已连接，正在读取数据...'
    addAlertMessage('串口已连接', 'info')
    
    // 开始读取数据（不await，在后台运行）
    startReading()

    if (standardTotalLoad.value === 0) {
      postureStatus.value = '请录入压力标准值'
      alert('请录入压力标准值：点击“录入当前姿态为标准”')
      addAlertMessage('请录入压力标准值', 'warning')
    }
  } catch (error) {
    console.error('❌ 串口连接失败:', error)
    postureStatus.value = '❌ 串口连接失败：' + (error.message || error)
    addAlertMessage('串口连接失败: ' + (error.message || error), 'error')
  }
}

// 开始读取串口数据
const startReading = async () => {
  if (!port || isReading.value) return
  
  isReading.value = true
  reader = port.readable.getReader()
  
  try {
    console.log('📡 开始读取串口数据...')
    while (true) {
      const { value, done } = await reader.read()
      if (done) break
      
      // 处理接收到的数据
      const line = new TextDecoder().decode(value).trim()
      if (line) {
        processSerialData(line)
      }
    }
  } catch (error) {
    console.error('❌ 读取串口数据出错:', error)
    postureStatus.value = '❌ 串口读取中断：' + (error.message || error)
    addAlertMessage('串口读取出错: ' + (error.message || error), 'error')
  } finally {
    isReading.value = false
    if (reader) {
      reader.releaseLock()
      reader = null
    }
  }
}

// 处理串口数据（与后端逻辑保持一致）
// const processSerialData = (line) => {
//   const parts = line.replace(/\s/g, '').split(',')
//   if (parts.length === 4) {
//     try {
//       const rawVals = parts.map(p => parseFloat(p))
//       const pressures = processSignals(rawVals)
      
//       if (isCalibrated) {
//         // 更新前端状态
//         updateSensorData(pressures)
//       }
//     } catch (e) {
//       console.warn('数据解析失败:', line)
//     }
//   }
// }
const processSerialData = (line) => {
  const parts = line.trim().split(/[\s,;]+/).filter(Boolean)
  if (parts.length === 4) {
    try {
      const rawVals = parts.map(p => parseFloat(p))
      if (rawVals.some(v => Number.isNaN(v))) {
        console.warn('串口数据包含非数值项:', line)
        return
      }

      if (serialInputAlreadyGram === null) {
        const hasDecimal = parts.some(p => p.includes('.') || p.toLowerCase().includes('e'))
        const maxRaw = Math.max(...rawVals)
        // 如果串口数据本身带有小数且数值较小，则极有可能已经是克单位
        if (hasDecimal && maxRaw <= 50) {
          serialInputAlreadyGram = true
          console.info('自动检测到串口输入为克单位，前端将跳过 CALIB_FACTOR 转换。')
        } else if (Number.isInteger(rawVals[0]) && Number.isInteger(rawVals[1]) && Number.isInteger(rawVals[2]) && Number.isInteger(rawVals[3]) && maxRaw > 50) {
          serialInputAlreadyGram = false
          console.info('自动检测到串口输入为 ADC 原始值，将使用 CALIB_FACTOR 转换。')
        } else {
          serialInputAlreadyGram = false
        }
      }

      rawPressures.value = serialInputAlreadyGram ? rawVals : rawVals.map(v => v * CALIB_FACTOR)
      const pressuresResult = processSignals(rawVals, serialInputAlreadyGram)
      updateSensorData(pressuresResult)
    } catch (e) {
      console.warn('数据解析失败:', line, e)
    }
  } else {
    console.warn('串口数据长度不符，已忽略:', line)
  }
}

// 信号处理（复制后端逻辑）
const processSignals = (rawVals, alreadyGram = false) => {
  // 1. 硬件归零阶段
  if (!isCalibrated.value) {
    for (let i = 0; i < 4; i++) {
      baselines[i] += rawVals[i]
    }
    calibrationCounter++
    baselinePressureMax = Math.max(baselinePressureMax, ...rawVals)
    if (rawVals.some(v => v > CALIBRATION_RAW_PRESSURE_LIMIT)) {
      baselineInvalidPressure = true
    }

    const rawConverted = alreadyGram ? rawVals : rawVals.map(v => v * CALIB_FACTOR)
    calibrationNoiseG = Math.max(calibrationNoiseG, ...rawConverted)
    const previewPressures = rawConverted.map(p => p > deadzoneThreshold.value ? p : 0)

    if (calibrationCounter >= CALIBRATION_SAMPLES) {
      if (baselineInvalidPressure) {
        addAlertMessage('归零期间检测到压力，请保持传感器空载后重新执行归零。', 'warning')
        baselines = [0, 0, 0, 0]
        calibrationCounter = 0
        baselinePressureMax = 0
        calibrationNoiseG = 0
        baselineInvalidPressure = false
        calibrating.value = false
        if (calibrationTimer) {
          clearTimeout(calibrationTimer)
          calibrationTimer = null
        }
        return previewPressures
      }

      baselines = baselines.map(b => b / CALIBRATION_SAMPLES)
      isCalibrated.value = true
      calibrating.value = false
      if (calibrationTimer) {
        clearTimeout(calibrationTimer)
        calibrationTimer = null
      }
      console.log('硬件环境归零完成！基准值:', baselines, '基线噪声:', calibrationNoiseG)
      addAlertMessage('硬件归零完成', 'info')
      filterQueues.forEach(q => q.length = 0)
    }
    return previewPressures
  }
  
  // 2. 减去基准并滤波
  const calibratedVals = rawVals.map((raw, i) => Math.max(0, raw - baselines[i]))
  
  const filteredVals = []
  for (let i = 0; i < 4; i++) {
    filterQueues[i].push(calibratedVals[i])
    if (filterQueues[i].length > 10) filterQueues[i].shift()
    const avg = filterQueues[i].reduce((a, b) => a + b, 0) / filterQueues[i].length
    filteredVals.push(avg)
  }
  
  // 3. 转换单位并应用死区
  const pressures = alreadyGram ? filteredVals : filteredVals.map(v => v * CALIB_FACTOR)
  const dynamicDeadzone = Math.max(deadzoneThreshold.value, Math.min(calibrationNoiseG * 0.6 + 0.02, 0.12))
  return pressures.map(p => p > dynamicDeadzone ? p : 0)
}

// 更新传感器数据
const updateSensorData = (newPressures) => {
  pressures.value = newPressures
  currentCop.value = computeCop(pressures.value)

  // 追踪每个通道是否持续无信号
  pressures.value.forEach((value, index) => {
    if (value <= deadzoneThreshold.value) {
      sensorNoSignalCount[index] += 1
    } else {
      sensorNoSignalCount[index] = 0
    }
    if (sensorNoSignalCount[index] === SENSOR_NO_SIGNAL_WARN) {
      addAlertMessage(`A${index} 长时间无信号，请检查线路或传感器连接。`, 'warning')
    }
  })

  if (calibrating.value) {
    postureStatus.value = '硬件归零中，请保持传感器空载...'
    updateAllCharts()
    return
  }

  const isGood = evaluatePosture()
  updatePieChart(isGood)
  updateAllCharts() // <--- 确保这一行存在且没被注释
}

// 断开串口连接
const disconnectSerial = async () => {
  if (reader) {
    await reader.cancel()
    reader.releaseLock()
    reader = null
  }
  if (port) {
    await port.close()
    port = null
  }
  if (calibrationTimer) {
    clearTimeout(calibrationTimer)
    calibrationTimer = null
  }
  isReading.value = false
  isCalibrated.value = false
  calibrationCounter = 0
  baselines = [0, 0, 0, 0]
  calibrationNoiseG = 0
  serialInputAlreadyGram = null
  postureStatus.value = '串口已断开'
  addAlertMessage('串口已断开', 'info')
}

// ---------- 响应式状态 ----------
const pressures = ref([0, 0, 0, 0])
const currentCop = ref({ x: 0, y: 0 })
const postureStatus = ref('正在连接系统...')
const currentTime = ref(new Date().toLocaleTimeString())
const alertHistory = ref([{ time: '系统', msg: '传感器通信已就绪', type: 'info' }])

// 标准坐姿数据
const standardTotalLoad = ref(0)
const standardCop = ref({ x: 0, y: 0 })
const standardPressures = ref([0, 0, 0, 0])

// 用户可调阈值（前端本地存储）
const pressureRatioThreshold = ref(1.2)
const copDistanceThreshold = ref(1.2)

// UI 状态
const calibrating = ref(false)
const hasValidData = ref(false)

// 滚动同步相关
const leftScrollRef = ref(null)
const rightScrollRef = ref(null)
let isSyncing = false  // 防止循环触发

// ---------- 自动滚动相关 ----------
const autoScrollEnabled = ref(false)
let autoScrollTimer = null
let autoScrollPaused = false       // 用户手动滚动时临时暂停
let pauseTimeout = null

// 波形缓冲区
const WAVE_LEN = 100
const waveData = ref({
  A0: new Array(WAVE_LEN).fill(0),
  A1: new Array(WAVE_LEN).fill(0),
  A2: new Array(WAVE_LEN).fill(0),
  A3: new Array(WAVE_LEN).fill(0)
})
let waveIndex = 0
const xAxisData = ref(Array.from({ length: WAVE_LEN }, (_, i) => i))

// 饼图累计时间
let goodTime = 0, badTime = 0
let lastTimestamp = 0
let currentGood = true

// 传感器通道无信号计数，用于检测长期失效或短路
const sensorNoSignalCount = [0, 0, 0, 0]
const SENSOR_NO_SIGNAL_WARN = 100

// ECharts 实例
let waveChart = null
let footChart = null
let pieChart = null
let radarChart = null

const multiWaveRef = ref(null)
const mainChartRef = ref(null)
const pieChartRef = ref(null)
const polarChartRef = ref(null)

const router = useRouter()

// 重新设计的左脚形状坐标：增强脚趾波浪感和足弓深度
// 重新设计的左脚形状坐标：完全模拟图一的 5 个圆弧脚趾和饱满轮廓
// 重新设计的左脚形状坐标 (Toe朝右)
// 特点：右侧脚趾从小到大排列，下方足弓大弯曲，上方外缘小弯曲
// 重新设计的左脚形状坐标 (Toe朝右)
// 1. 脚趾圆润化：通过增加过渡点消除尖刺。
// 2. 掌部加宽：增加大脚趾和小脚趾附近的 Y 轴间距。
// 3. 足弓左移：将下方大弯曲的波谷向左侧（负 X 方向）偏移。
// 重新设计的左脚形状坐标 (Toe朝右)
// 1. 撑开掌部：显著增加右侧脚趾区域的 Y 轴跨度（从 4.5 到 -7.5）
// 2. 模拟图二：五个圆滑弧线脚趾，下方内弯大圆弧左移并加宽右侧连接处
// 重新设计的左脚形状坐标 (Toe朝右) 
// 特点：下方内弯右侧有向外大弯曲，上方内弯右侧有向外小弯曲，掌部宽厚
// 重新设计的左脚形状坐标 (Toe朝右)
// 核心改动：显著增强了下方足弓（内弯）右侧的向外凸起（外弯），使掌部看起来非常饱满
// 重新设计的左脚形状坐标 (Toe朝右)  
// ==================== 精确的右脚轮廓（Toe 朝右，5个圆弧脚趾，不粘连） ====================
const footOutline = [
  // --- 右侧 5 个脚趾 (特点：头部/根部均加宽，小趾上移，趾缝清晰不粘连) ---
  // 小脚趾 (上移并加宽，头部圆润)
  [7.2, 5.0], [8.5, 5.4], [9.2, 5.8], [9.4, 5.0], [9.2, 4.2], [8.5, 4.0], [7.2, 4.2], 
  // 第四趾 (增加根部宽度，拉开与小趾的垂直距离)
  [7.4, 2.6], [8.6, 3.0], [9.6, 3.6], [9.8, 2.8], [9.6, 2.0], [8.6, 1.6], [7.4, 2.0],
  // 第三趾
  [7.7, 0.2], [8.9, 0.5], [10.0, 1.3], [10.2, 0.3], [10.0, -0.7], [8.9, -1.1], [7.7, -0.7],
  // 第二趾 (明显加宽，头部极圆)
  [8.0, -2.6], [9.2, -1.9], [10.6, -1.2], [11.0, -2.7], [10.6, -4.2], [9.2, -4.7], [8.0, -4.0],
  // 大脚趾 (极其宽大饱满，体现根部与头部同步变宽)
  [8.2, -5.9], [9.7, -6.2], [11.2, -6.9], [11.7, -8.4], [11.2, -10.2], [9.7, -10.9], [8.2, -9.9],

  // --- 下方：足弓及右侧扩张 (对应图三红线饱满弧度) ---
  [4.5, -11.6], [1.5, -12.4], [-2.5, -6.5], [-6.5, -9.5], [-9.5, -9.0], 

  // --- 左侧：脚后跟 (圆润饱满) ---
  [-11.5, -5.0], [-12.5, 0], [-11.5, 5.0], 

  // --- 上方：足外侧及右侧扩张 ---
  [-8.0, 8.2], [-3.0, 6.8], [1.5, 8.8], [5.5, 8.2], 

  [7.2, 5.0] // 回到起始点闭合
]

// ==================== 传感器坐标（与脚形匹配，重心计算合理） ====================
// 传感器坐标
const sensorPos = [
  { x: 4.5, y: 5.5 },
  { x: -4.5, y: 5.5 },
  { x: 3.5, y: -4.5 },
  { x: -3.5, y: -4.5 }
]

// 计算属性
const totalLoad = computed(() => pressures.value.reduce((a, b) => a + b, 0))

const pressureRatio = computed(() => {
  if (standardTotalLoad.value === 0) return 0
  return totalLoad.value / standardTotalLoad.value
})

const copDistance = computed(() => {
  if (standardTotalLoad.value === 0) return 0
  const dx = currentCop.value.x - standardCop.value.x
  const dy = currentCop.value.y - standardCop.value.y
  return Math.sqrt(dx*dx + dy*dy)
})

const statusClass = computed(() => {
  if (postureStatus.value.includes('警告') || postureStatus.value.includes('预警')) return 'danger-bg'
  if (postureStatus.value.includes('良好')) return 'safe-bg'
  return 'idle-bg'
})

// 姿态判定逻辑
let warningStartAt = null

const evaluatePosture = () => {
  const load = totalLoad.value
  const minLoad = backendPressureThreshold.value ?? 5
  const maxSensor = Math.max(...pressures.value)
  const timeLimitMs = Math.max(0, backendTimeLimit.value || 0) * 1000

  // 噪声阈值：如果总载荷很小，视为离座 / 空闲，避免空气噪声误判为坐姿
  const idleThreshold = Math.max(1.0, deadzoneThreshold.value * 4, Math.min(2.0, (backendPressureThreshold.value ?? 5) * 0.05))
  const standardContactThreshold = standardTotalLoad.value > 0
    ? Math.max(0.15, standardTotalLoad.value * 0.3, deadzoneThreshold.value * 2)
    : idleThreshold
  const hasContactPressure = maxSensor >= 1.2 || load >= standardContactThreshold
  if (!hasContactPressure) {
    warningStartAt = null
    postureStatus.value = '离座 / 空闲'
    return false
  }

  hasValidData.value = true
  if (standardTotalLoad.value === 0) {
    warningStartAt = null
    postureStatus.value = '请先录入标准姿态'
    return false
  }

  const pressureLimit = backendPressureRatioThreshold.value || pressureRatioThreshold.value
  const copLimit = backendCopDistanceThreshold.value || copDistanceThreshold.value
  const isSmallStandard = standardTotalLoad.value < 1.0

  let isPressureOver = false
  if (isSmallStandard) {
    const absoluteTolerance = Math.max(0.1, standardTotalLoad.value * 0.5)
    isPressureOver = load > standardTotalLoad.value + absoluteTolerance
  } else {
    isPressureOver = pressureRatio.value > pressureLimit
  }

  const isCopOver = copDistance.value > copLimit

  if (!isPressureOver && !isCopOver) {
    warningStartAt = null
    postureStatus.value = '✅ 坐姿保持良好'
    return true
  }

  const issues = []
  if (isPressureOver) issues.push(`压力异常 ${pressureRatio.value.toFixed(2)}x`)
  if (isCopOver) issues.push(`重心偏移 ${copDistance.value.toFixed(1)}cm`)
  const issueText = issues.join(' & ')

  if (!warningStartAt) {
    warningStartAt = Date.now()
  }
  const elapsed = Date.now() - warningStartAt

  if (elapsed < timeLimitMs) {
    postureStatus.value = `⚠️ 预警：${issueText}，持续 ${backendTimeLimit.value}s 后确认`
    return false
  }

  postureStatus.value = `⚠️ 警告：${issueText}`
  return false
}

// 饼图更新
const updatePieChart = (isGood) => {
  const now = Date.now()
  if (lastTimestamp === 0) {
    lastTimestamp = now
    currentGood = isGood
    return
  }
  const delta = (now - lastTimestamp) / 1000
  if (currentGood) goodTime += delta
  else badTime += delta
  currentGood = isGood
  lastTimestamp = now
  if (pieChart) {
    pieChart.setOption({
      series: [{
        data: [
          { value: goodTime, name: '良好姿态' },
          { value: badTime, name: '异常姿态' }
        ]
      }]
    })
  }
}

// 图表更新函数
// const updateWaveform = () => {
//   if (!waveChart) return
//   waveData.value.A0.push(pressures.value[0])
//   waveData.value.A1.push(pressures.value[1])
//   waveData.value.A2.push(pressures.value[2])
//   waveData.value.A3.push(pressures.value[3])
//   if (waveData.value.A0.length > WAVE_LEN) waveData.value.A0.shift()
//   if (waveData.value.A1.length > WAVE_LEN) waveData.value.A1.shift()
//   if (waveData.value.A2.length > WAVE_LEN) waveData.value.A2.shift()
//   if (waveData.value.A3.length > WAVE_LEN) waveData.value.A3.shift()
//   waveIndex++
//   xAxisData.value.push(waveIndex)
//   if (xAxisData.value.length > WAVE_LEN) xAxisData.value.shift()
//   waveChart.setOption({
//     xAxis: { data: [...xAxisData.value] },
//     series: [
//       { data: [...waveData.value.A0] },
//       { data: [...waveData.value.A1] },
//       { data: [...waveData.value.A2] },
//       { data: [...waveData.value.A3] }
//     ]
//   })
// }

const updateWaveform = () => {
  if (!waveChart) return
  
  // 推入新数据
  waveData.value.A0.push(pressures.value[0])
  waveData.value.A1.push(pressures.value[1])
  waveData.value.A2.push(pressures.value[2])
  waveData.value.A3.push(pressures.value[3])
  
  // 保持窗口长度
  if (waveData.value.A0.length > WAVE_LEN) {
    waveData.value.A0.shift(); waveData.value.A1.shift();
    waveData.value.A2.shift(); waveData.value.A3.shift();
  }

  waveIndex++
  xAxisData.value.push(waveIndex)
  if (xAxisData.value.length > WAVE_LEN) xAxisData.value.shift()

  // 关键：确保 setOption 的数据源是响应式的最新值
  waveChart.setOption({
    xAxis: { data: [...xAxisData.value] },
    series: [
      { data: [...waveData.value.A0] },
      { data: [...waveData.value.A1] },
      { data: [...waveData.value.A2] },
      { data: [...waveData.value.A3] }
    ]
  })
}

const updateFootChart = () => {
  if (!footChart) return
  const currentPoint = [[currentCop.value.x, currentCop.value.y]]
  const standardPoint = standardTotalLoad.value > 0 ? [[standardCop.value.x, standardCop.value.y]] : []
  footChart.setOption({
    series: [
      { name: '当前重心', data: currentPoint },
      { name: '标准重心', data: standardPoint }
    ]
  })
}

const updateRadar = () => {
  if (!radarChart) return
  const maxPressure = Math.max(...pressures.value)
  const radarMax = Math.max(5, Math.ceil(maxPressure * 4))
  radarChart.setOption({
    radar: {
      indicator: [
        { name: 'A0', max: radarMax },
        { name: 'A1', max: radarMax },
        { name: 'A2', max: radarMax },
        { name: 'A3', max: radarMax }
      ]
    },
    series: [{ data: [{ value: pressures.value, name: '实时载荷' }] }]
  })
}

const updateAllCharts = () => {
  updateWaveform()
  updateFootChart()
  updateRadar()
}

// 计算重心
const computeCop = (press) => {
  const total = press.reduce((a, b) => a + b, 0)
  if (total < 5) return { x: 0, y: 0 }
  let cx = 0, cy = 0
  for (let i = 0; i < 4; i++) {
    cx += press[i] * sensorPos[i].x
    cy += press[i] * sensorPos[i].y
  }
  return { x: cx / total, y: cy / total }
}

// 保存标准数据到 localStorage
const saveStandardToLocal = () => {
  localStorage.setItem('standardTotalLoad', standardTotalLoad.value)
  localStorage.setItem('standardCopX', standardCop.value.x)
  localStorage.setItem('standardCopY', standardCop.value.y)
  localStorage.setItem('standardPressures', JSON.stringify(standardPressures.value))
}

// 从 localStorage 加载标准数据
const loadStandardFromLocal = () => {
  const total = localStorage.getItem('standardTotalLoad')
  const copX = localStorage.getItem('standardCopX')
  const copY = localStorage.getItem('standardCopY')
  const pressuresStr = localStorage.getItem('standardPressures')
  if (total && copX && copY && pressuresStr) {
    standardTotalLoad.value = parseFloat(total)
    standardCop.value = { x: parseFloat(copX), y: parseFloat(copY) }
    standardPressures.value = JSON.parse(pressuresStr)
    return true
  }
  return false
}

// 前端硬件归零（直接操作前端状态）
const calibrateBaseline = () => {
  if (!isReading.value) {
    alert('请先连接串口并开始读取传感器数据后，再执行“一键归零”。')
    addAlertMessage('归零失败：串口未连接或未开始读取数据。', 'warning')
    return
  }

  calibrating.value = true
  postureStatus.value = '硬件归零中，请保持传感器空载...'
  pressures.value = [0, 0, 0, 0]
  currentCop.value = { x: 0, y: 0 }
  addAlertMessage("正在执行硬件归零，请保持传感器空载...", "info")
  
  // 重置前端校准状态
  baselines = [0.0, 0.0, 0.0, 0.0]
  calibrationCounter = 0
  baselinePressureMax = 0
  calibrationNoiseG = 0
  baselineInvalidPressure = false
  isCalibrated.value = false
  filterQueues.forEach(q => q.length = 0)
  
  // 重置标准数据
  standardTotalLoad.value = 0
  standardCop.value = { x: 0, y: 0 }
  standardPressures.value = [0, 0, 0, 0]
  saveStandardToLocal()

  if (calibrationTimer) {
    clearTimeout(calibrationTimer)
    calibrationTimer = null
  }
  calibrationTimer = setTimeout(() => {
    if (!isCalibrated.value) {
      if (baselineInvalidPressure) {
        addAlertMessage("归零失败：检测到传感器受力，请保持传感器空载后重新执行归零。", "warning")
      } else if (calibrationCounter > 0) {
        baselines = baselines.map(b => b / Math.max(calibrationCounter, 1))
        isCalibrated.value = true
        calibrating.value = false
        addAlertMessage('硬件归零完成', 'info')
        filterQueues.forEach(q => q.length = 0)
      } else {
        calibrating.value = false
        addAlertMessage('归零失败：未检测到任何传感器数据，请检查串口连接。', 'error')
      }
      calibrationTimer = null
    }
  }, 5000)
}

// 前端录入标准坐姿
const captureStandardPosture = () => {
  if (calibrating.value) {
    alert('归零正在进行中，请等待归零完成后再录入标准坐姿。')
    return
  }
  if (!isCalibrated.value) {
    alert('请先点击“一键归零”，等待归零完成后再录入标准坐姿。')
    return
  }

  // 修改点：将阈值降至极低，只要不是绝对的 0 即可录入
  const minLoad = 0.1 
  const currentLoad = totalLoad.value
  
  if (currentLoad < minLoad) {
    // 只有在完全没有传感器信号时才提示
    addAlertMessage(`未感应到任何压力，录入失败`, 'error')
    return
  }
  
  // 直接保存当前数据，不再弹出拦截警告
  standardTotalLoad.value = currentLoad
  standardPressures.value = [...pressures.value]
  standardCop.value = computeCop(standardPressures.value)
  saveStandardToLocal()
  
  alert(`✅ 标准姿态已录入！\n总载荷：${standardTotalLoad.value.toFixed(1)}g\n重心：(${standardCop.value.x.toFixed(1)}, ${standardCop.value.y.toFixed(1)})`)
  addAlertMessage(`标准姿态已录入 (总载荷 ${standardTotalLoad.value.toFixed(1)}g)`, "info")
}

const addAlertMessage = (msg, type = 'info') => {
  const timeStr = new Date().toLocaleTimeString().slice(0,5)
  alertHistory.value.unshift({ time: timeStr, msg, type })
  if (alertHistory.value.length > 12) alertHistory.value.pop()
}

// 从后端加载标准数据
const loadStandardFromBackend = async () => {
  try {
    const res = await fetch('http://localhost:5000/api/get_settings')
    const data = await res.json()
    if (data.refTotal && data.refTotal > 0 && data.refCop && data.refCop.length === 2) {
      standardTotalLoad.value = data.refTotal
      standardCop.value = { x: data.refCop[0], y: data.refCop[1] }
      standardPressures.value = [0, 0, 0, 0]
      saveStandardToLocal()
      addAlertMessage(`已从后端恢复标准数据：总载荷 ${standardTotalLoad.value.toFixed(1)}g，重心(${standardCop.value.x.toFixed(1)}, ${standardCop.value.y.toFixed(1)})`, "info")
      return true
    }
  } catch (err) {
    console.error("从后端加载标准数据失败", err)
  }
  return false
}

// 本地存储阈值
watch([pressureRatioThreshold, copDistanceThreshold, deadzoneThreshold], () => {
  localStorage.setItem('pressureRatioThreshold', pressureRatioThreshold.value)
  localStorage.setItem('copDistanceThreshold', copDistanceThreshold.value)
  localStorage.setItem('deadzoneThreshold', deadzoneThreshold.value)
})

const loadThresholds = () => {
  const savedRatio = localStorage.getItem('pressureRatioThreshold')
  const savedDist = localStorage.getItem('copDistanceThreshold')
  const savedDeadzone = localStorage.getItem('deadzoneThreshold')
  if (savedRatio) pressureRatioThreshold.value = parseFloat(savedRatio)
  if (savedDist) copDistanceThreshold.value = parseFloat(savedDist)
  if (savedDeadzone) deadzoneThreshold.value = parseFloat(savedDeadzone)
}

// 从后端加载核心算法阈值
const loadBackendSettings = async () => {
  try {
    const res = await fetch(`${backendApiUrl}/api/get_settings`)
    if (!res.ok) throw new Error('后端返回异常')
    const data = await res.json()

    let changed = false
    const oldThreshold = backendPressureThreshold.value
    const oldTimeLimit = backendTimeLimit.value

    if (typeof data.threshold === 'number' && data.threshold !== oldThreshold) {
      backendPressureThreshold.value = data.threshold
      changed = true
    }
    if (typeof data.timeLimit === 'number' && data.timeLimit !== oldTimeLimit) {
      backendTimeLimit.value = data.timeLimit
      changed = true
    }
    if (typeof data.pressureRatioThreshold === 'number' && data.pressureRatioThreshold !== backendPressureRatioThreshold.value) {
      backendPressureRatioThreshold.value = data.pressureRatioThreshold
      changed = true
    }
    if (typeof data.copDistanceThreshold === 'number' && data.copDistanceThreshold !== backendCopDistanceThreshold.value) {
      backendCopDistanceThreshold.value = data.copDistanceThreshold
      changed = true
    }

    if (changed) {
      addAlertMessage(`已同步后端设置：离座阈值 ${backendPressureThreshold.value.toFixed(1)}g，警告时长 ${backendTimeLimit.value}s，压力比例 ${backendPressureRatioThreshold.value.toFixed(2)}x，偏移阈值 ${backendCopDistanceThreshold.value.toFixed(2)}cm`, 'info')
    }
  } catch (err) {
    console.warn('无法加载后端阈值:', err)
  }
}

// 滚动同步处理函数
const syncScroll = (sourceRef, targetRef) => {
  if (!sourceRef.value || !targetRef.value) return
  const source = sourceRef.value
  const target = targetRef.value
  const scrollHeight = source.scrollHeight - source.clientHeight
  if (scrollHeight <= 0) return
  const ratio = source.scrollTop / scrollHeight
  const targetScrollHeight = target.scrollHeight - target.clientHeight
  target.scrollTop = ratio * targetScrollHeight
}

// 自动滚动：缓慢向上滚动左右面板，到达底部后回到顶部
const startAutoScroll = () => {
  if (autoScrollTimer) clearInterval(autoScrollTimer)
  if (!leftScrollRef.value || !rightScrollRef.value) return

  const STEP = 8.0          // 每帧移动像素
  const INTERVAL = 15       // 毫秒

  autoScrollTimer = setInterval(() => {
    if (!autoScrollEnabled.value || autoScrollPaused) return
    const left = leftScrollRef.value
    const right = rightScrollRef.value
    if (!left || !right) return

    const leftMax = left.scrollHeight - left.clientHeight
    const rightMax = right.scrollHeight - right.clientHeight
    if (leftMax <= 0 && rightMax <= 0) return

    let newLeft = left.scrollTop + STEP
    let newRight = right.scrollTop + STEP
    if (newLeft >= leftMax) newLeft = 0
    if (newRight >= rightMax) newRight = 0

    left.scrollTop = newLeft
    right.scrollTop = newRight
  }, INTERVAL)
}

const stopAutoScroll = () => {
  if (autoScrollTimer) {
    clearInterval(autoScrollTimer)
    autoScrollTimer = null
  }
}

// 临时暂停自动滚动（用户手动滚动时调用）
const pauseAutoScroll = () => {
  if (!autoScrollEnabled.value) return
  autoScrollPaused = true
  if (pauseTimeout) clearTimeout(pauseTimeout)
  pauseTimeout = setTimeout(() => {
    autoScrollPaused = false
  }, 5000)   // 5秒后恢复自动滚动
}

// 开关切换
const toggleAutoScroll = () => {
  if (autoScrollEnabled.value) {
    startAutoScroll()
  } else {
    stopAutoScroll()
    autoScrollPaused = false
    if (pauseTimeout) clearTimeout(pauseTimeout)
  }
  localStorage.setItem('autoScrollEnabled', autoScrollEnabled.value)
}

const handleLeftScroll = () => {
  if (isSyncing) return
  isSyncing = true
  syncScroll(leftScrollRef, rightScrollRef)
  isSyncing = false
  // 用户手动滚动时，临时暂停自动滚动
  if (autoScrollEnabled.value) {
    pauseAutoScroll()
  }
}

const handleRightScroll = () => {
  if (isSyncing) return
  isSyncing = true
  syncScroll(rightScrollRef, leftScrollRef)
  isSyncing = false
  if (autoScrollEnabled.value) {
    pauseAutoScroll()
  }
}

const initCharts = () => {
  footChart = echarts.init(mainChartRef.value)
  footChart.setOption({
  xAxis: { 
    min: -16, 
    max: 16, 
    show: false,
    type: 'value'
  },
  yAxis: { 
    // 锁定范围：设置为 -15 到 15。
    // 这能确保最上方上移到 5.8 的小脚趾不被切边，并拉开整体掌部的视觉间距。
    min: -15, 
    max: 15, 
    show: false,
    type: 'value'
  },
  grid: {
    left: '2%', right: '2%', top: '5%', bottom: '5%',
    containLabel: false
  },
  series: [
    { 
      name: '足底轮廓', 
      type: 'line', 
      // 关键：平滑度保持在 0.36。
      // 较低的平滑度能确保脚趾之间定义的“凹陷间隙”不被算法自动磨平融合，从而防止粘连。
      smooth: 0.36, 
      data: footOutline, 
      lineStyle: { 
        color: '#00c1de', 
        width: 5,
        shadowBlur: 20,
        shadowColor: 'rgba(0,193,222,0.8)' 
      }, 
      areaStyle: { 
        color: 'rgba(0,193,222,0.15)' 
      }, 
      symbol: 'none' 
    },
    { 
      name: '当前重心', 
      type: 'scatter', 
      data: [[currentCop.value.x, currentCop.value.y]], 
      symbolSize: 28, 
      itemStyle: { color: '#ff4d4f', shadowBlur: 15, borderColor: '#fff', borderWidth: 2 }, 
      label: { show: true, formatter: 'CoP', color: '#fff', fontSize: 10, offset: [0, -15] },
      zIndex: 10 
    },
    { name: '标准重心', type: 'scatter', data: [], symbol: 'circle', symbolSize: 20, itemStyle: { color: 'transparent', borderColor: '#00c1de', borderType: 'dashed', borderWidth: 2 }, label: { show: true, formatter: '标准', color: '#00c1de', fontSize: 10, offset: [0, -12] } }
  ]
})

  radarChart = echarts.init(polarChartRef.value)
  radarChart.setOption({
    radar: {
      indicator: [{ name: 'A0', max: 10 }, { name: 'A1', max: 10 }, { name: 'A2', max: 10 }, { name: 'A3', max: 10 }],
      center: ['50%', '50%'], radius: '70%', axisName: { color: '#00c1de' }, splitNumber: 5,
      axisLine: { lineStyle: { color: 'rgba(0,193,222,0.3)' } },
      splitLine: { lineStyle: { color: 'rgba(0,193,222,0.2)' } }
    },
    series: [{ type: 'radar', data: [{ value: [0,0,0,0], name: '实时载荷' }], areaStyle: { color: 'rgba(0,193,222,0.3)' }, lineStyle: { color: '#0cf', width: 2 } }]
  })

  waveChart = echarts.init(multiWaveRef.value)
  waveChart.setOption({
    grid: { left: '45', right: '15', top: '35', bottom: '30', containLabel: true },
    legend: { data: ['A0', 'A1', 'A2', 'A3'], textStyle: { color: '#9cd9e8' }, top: 0 },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: xAxisData.value, axisLabel: { color: '#8aaec0' } },
    yAxis: { type: 'value', min: 0, name: '载荷 (g)', nameTextStyle: { color: '#00c1de' }, splitLine: { lineStyle: { color: 'rgba(0,193,222,0.2)' } } },
    series: [
      { name: 'A0', type: 'line', data: waveData.value.A0, symbol: 'none', lineStyle: { color: '#00c1de', width: 2 } },
      { name: 'A1', type: 'line', data: waveData.value.A1, symbol: 'none', lineStyle: { color: '#52c41a', width: 2 } },
      { name: 'A2', type: 'line', data: waveData.value.A2, symbol: 'none', lineStyle: { color: '#fadb14', width: 2 } },
      { name: 'A3', type: 'line', data: waveData.value.A3, symbol: 'none', lineStyle: { color: '#ff7c7e', width: 2 } }
    ]
  })

  pieChart = echarts.init(pieChartRef.value)
  pieChart.setOption({
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie', radius: ['55%', '78%'], label: { show: true, color: '#fff', formatter: '{b}', position: 'outside' },
      data: [{ value: 0, name: '良好姿态' }, { value: 0, name: '异常姿态' }],
      itemStyle: { borderRadius: 10, borderColor: '#000d1a', borderWidth: 2, color: params => params.dataIndex === 0 ? '#00c1de' : '#ff4d4f' }
    }]
  })
}

  // radarChart = echarts.init(polarChartRef.value)
  // radarChart.setOption({
  //   radar: {
  //     indicator: [{ name: 'A0', max: 500 }, { name: 'A1', max: 500 }, { name: 'A2', max: 500 }, { name: 'A3', max: 500 }],
  //     center: ['50%', '50%'], radius: '70%', axisName: { color: '#00c1de' }
  //   },
  //   series: [{ type: 'radar', data: [{ value: [0,0,0,0], name: '实时载荷' }], areaStyle: { color: 'rgba(0,193,222,0.3)' }, lineStyle: { color: '#0cf', width: 2 } }]
  // })
  // waveChart = echarts.init(multiWaveRef.value)
  // waveChart.setOption({
  //   grid: { left: '45', right: '15', top: '35', bottom: '30', containLabel: true },
  //   legend: { data: ['A0', 'A1', 'A2', 'A3'], textStyle: { color: '#9cd9e8' }, top: 0 },
  //   tooltip: { trigger: 'axis' },
  //   xAxis: { type: 'category', data: xAxisData.value, axisLabel: { color: '#8aaec0' } },
  //   yAxis: { type: 'value', min: 0, name: '载荷 (g)', nameTextStyle: { color: '#00c1de' }, splitLine: { lineStyle: { color: 'rgba(0,193,222,0.2)' } } },
  //   series: [
  //     { name: 'A0', type: 'line', data: waveData.value.A0, symbol: 'none', lineStyle: { color: '#00c1de', width: 2 } },
  //     { name: 'A1', type: 'line', data: waveData.value.A1, symbol: 'none', lineStyle: { color: '#52c41a', width: 2 } },
  //     { name: 'A2', type: 'line', data: waveData.value.A2, symbol: 'none', lineStyle: { color: '#fadb14', width: 2 } },
  //     { name: 'A3', type: 'line', data: waveData.value.A3, symbol: 'none', lineStyle: { color: '#ff7c7e', width: 2 } }
  //   ]
  // })
  // pieChart = echarts.init(pieChartRef.value)
  // pieChart.setOption({
  //   tooltip: { trigger: 'item' },
  //   series: [{
  //     type: 'pie', radius: ['55%', '78%'], label: { show: true, color: '#fff', formatter: '{b}', position: 'outside' },
  //     data: [{ value: 0, name: '良好姿态' }, { value: 0, name: '异常姿态' }],
  //     itemStyle: { borderRadius: 10, borderColor: '#000d1a', borderWidth: 2, color: params => params.dataIndex === 0 ? '#00c1de' : '#ff4d4f' }
  //   }]
  // })


// 生命周期
onMounted(async() => {
  // socket.on('calibration_done', (data) => {
  // isCalibrating.value = false; // 关键：这里才会关闭“归零中”状态
  // alert("环境归零成功！");
  // });
// 监听后端发出的归零完成信号
  if (typeof socket !== 'undefined' && socket) {
    socket.on('calibration_done', (data) => {
      // 这里的 calibrating 是你一键归零按钮绑定的 loading 状态变量
      calibrating.value = false
      isCalibrated.value = true
      addAlertMessage("环境归零成功！", "info")
      console.log("硬件基准已重置:", data.baselines)
    })
  }

  loadThresholds();
  await loadBackendSettings();
  
  window.addEventListener('backend-settings-updated', loadBackendSettings)

  // 检查Web Serial API支持
  if (!isWebSerialSupported) {
    postureStatus.value = '浏览器不支持 Web Serial API'
    addAlertMessage('浏览器不支持 Web Serial API，请使用 Chrome 或 Edge', 'error')
  } else {
    postureStatus.value = '请点击"连接串口"开始监测'
    addAlertMessage('Web Serial API 支持，准备连接串口', 'info')
  }
  
  // 加载本地标准数据（后端不可用时）
  loadStandardFromLocal();
  
  // 关键：使用 nextTick 确保所有 DOM 节点 (ref) 已经渲染完成
  await nextTick();
  // 增加一个小延迟，确保 CSS 动画（如全屏过渡）不影响 ECharts 获取宽高
  setTimeout(() => {
      initCharts(); // 确保 DOM 稳定后再初始化
      // 强制触发一次 resize 确保图表填满容器
      if (waveChart) waveChart.resize(); 
    }, 200);

  setInterval(() => { currentTime.value = new Date().toLocaleTimeString() }, 1000)
  window.addEventListener('resize', () => {
    [waveChart, footChart, radarChart, pieChart].forEach(ch => ch && ch.resize())
  })
  addAlertMessage("系统已启动，请连接串口", "info")

  // 加载自动滚动开关状态
  const savedAutoScroll = localStorage.getItem('autoScrollEnabled')
  if (savedAutoScroll !== null) {
    autoScrollEnabled.value = savedAutoScroll === 'true'
  }
  // 等待 DOM 完全渲染后，如果开关为 true，启动自动滚动
  await nextTick()
  if (autoScrollEnabled.value) {
    startAutoScroll()
  }

  // 添加滚动同步监听
  if (leftScrollRef.value && rightScrollRef.value) {
    leftScrollRef.value.addEventListener('scroll', handleLeftScroll)
    rightScrollRef.value.addEventListener('scroll', handleRightScroll)
  }
})

// onUnmounted(() => {
//   socket.disconnect()
//   [waveChart, footChart, radarChart, pieChart].forEach(ch => ch && ch.dispose())
//   // 移除滚动监听
//   if (leftScrollRef.value) leftScrollRef.value.removeEventListener('scroll', handleLeftScroll)
//   if (rightScrollRef.value) rightScrollRef.value.removeEventListener('scroll', handleRightScroll)

//     // ---------- 自动滚动清理 ----------
//   stopAutoScroll()
//   if (pauseTimeout) clearTimeout(pauseTimeout)
// })

onUnmounted(async () => {
  // 清理串口连接
  await disconnectSerial()
  
  // 清理图表
  [waveChart, footChart, radarChart, pieChart].forEach(ch => ch && ch.dispose())
  
  // 移除滚动监听
  if (leftScrollRef.value) leftScrollRef.value.removeEventListener('scroll', handleLeftScroll)
  if (rightScrollRef.value) rightScrollRef.value.removeEventListener('scroll', handleRightScroll)

  // 清理后端设置刷新事件
  window.removeEventListener('backend-settings-updated', loadBackendSettings)

  // 清理自动滚动
  stopAutoScroll()
  if (pauseTimeout) clearTimeout(pauseTimeout)
})

// 【修改点2】退出登录 - 主动清理资源后跳转，避免状态残留
const logout = () => {
  // 清理定时器
  if (autoScrollTimer) {
    clearInterval(autoScrollTimer);
    autoScrollTimer = null;
  }
  if (pauseTimeout) {
    clearTimeout(pauseTimeout);
    pauseTimeout = null;
  }

  // 销毁图表实例
  [waveChart, footChart, radarChart, pieChart].forEach(ch => {
    if (ch && ch.dispose) ch.dispose();
  });
  
  // 使用 replace 跳转登录页
  router.replace('/').catch(err => {
    console.error("退出登录跳转失败:", err);
    window.location.href = '/';
  });
}
</script>

<style scoped>
/* 此处完整保留您原来的样式，因篇幅限制不再重复，请确保复制原 Dashboard.vue 的 style 内容 */
/* 以下为补充的必要样式（如果原样式中已存在可忽略） */
.dashboard-wrapper {
  height: 100vh; width: 100vw; background: #00040a; color: #eef5ff;
  display: flex; flex-direction: column; overflow: hidden; position: fixed;
  font-family: 'Inter', 'Segoe UI', monospace;
}
.grid-bg {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background-image: linear-gradient(rgba(0, 193, 222, 0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(0, 193, 222, 0.05) 1px, transparent 1px);
  background-size: 30px 30px; pointer-events: none; z-index: 0;
}
.custom-header {
  height: 60px; background: rgba(2, 18, 28, 0.9); backdrop-filter: blur(12px);
  border-bottom: 1px solid #00c1de; padding: 0 24px; z-index: 10; display: flex; align-items: center;
}
.header-content-wrapper { width: 100%; display: flex; justify-content: space-between; align-items: center; position: relative; }
.center-status-wrapper { position: absolute; left: 50%; transform: translateX(-50%); }
.floating-status-pill { padding: 5px 40px; border-radius: 40px; font-weight: bold; border: 2px solid; backdrop-filter: blur(4px); }
.safe-bg { border-color: #52c41a; color: #a0ff7a; background: rgba(82,196,26,0.2); text-shadow: 0 0 5px #52c41a; }
.danger-bg { border-color: #ff4d4f; color: #ff9a9c; background: rgba(255,77,79,0.2); text-shadow: 0 0 5px #ff4d4f; }
.idle-bg { border-color: #888; color: #ccc; background: rgba(100,100,100,0.2); }
.main-content { flex: 1; padding: 15px; display: grid; grid-template-columns: 350px 1fr 350px; gap: 15px; z-index: 2; overflow: hidden; }
.grid-cell { display: flex; flex-direction: column; height: 100%; overflow-y: auto; scrollbar-width: thin; }
.glass-card { background: rgba(6, 18, 28, 0.7); backdrop-filter: blur(14px); border: 1px solid rgba(0,193,222,0.3); border-radius: 20px; padding: 16px; }
.card-title-glow { font-size: 15px; font-weight: 800; color: #9ef0ff; border-left: 4px solid #00c1de; padding-left: 12px; margin-bottom: 16px; text-transform: uppercase; }
.sensor-values-v3 .val-row-v3 { display: flex; align-items: center; margin: 12px 0; }
.s-label { width: 90px; font-size: 12px; color: #bbd9ff; }
.s-bar-bg { flex: 1; height: 8px; background: #102b38; margin: 0 12px; border-radius: 10px; overflow: hidden; }
.s-bar-fill { height: 100%; background: linear-gradient(90deg, #00c1de, #3ae0a0); box-shadow: 0 0 6px #00c1de; border-radius: 10px; }
.s-num { font-family: monospace; min-width: 55px; text-align: right; }
.footer-stats-bar { display: flex; justify-content: space-between; margin-top: 16px; padding-top: 12px; border-top: 1px solid rgba(0,193,222,0.3); font-size: 12px; }
.stats-dark-row { display: flex; gap: 12px; margin-bottom: 8px; }
.stat-dark-item { flex: 1; background: rgba(0,15,25,0.7); padding: 10px; border-radius: 16px; text-align: center; }
.stat-l { font-size: 11px; color: #8aaccc; display: block; }
.stat-v { font-size: 22px; font-weight: 800; font-family: monospace; }
.danger-text { color: #ff7c7e; text-shadow: 0 0 4px #ff4d4f; }
.safe-text { color: #52c41a; text-shadow: 0 0 4px #52c41a; }
.cyan-glow { color: #0cf; text-shadow: 0 0 4px #0cf; }
.green-glow { color: #52c41a; text-shadow: 0 0 4px #52c41a; }
.m-btn-glow { background: rgba(0,193,222,0.1); border: 1px solid #00c1de; color: #0cf; padding: 6px 14px; border-radius: 30px; cursor: pointer; }
.m-btn-glow:hover { background: #00c1de22; box-shadow: 0 0 12px #00c1de; }
.primary-border { border: 1px solid #00c1de; background: transparent; }
.ref-info-box { margin-top: 10px; padding: 6px; border: 1px solid #00c1de; border-radius: 12px; font-size: 12px; text-align: center; background: rgba(0,193,222,0.1); }
.aligned-row { display: flex; align-items: center; justify-content: space-between; margin-top: 12px; }
.r-group { display: flex; align-items: center; gap: 8px; }
.c-input-glow { background: #071e28; border: 1px solid #2f8a9e; color: #0cf; width: 85px; text-align: right; border-radius: 28px; padding: 6px 12px; }
.desc { font-size: 11px; color: #7aa9c2; margin: 4px 0; }
.main-chart-outer { flex: 1.5; background: radial-gradient(ellipse at center, rgba(0,193,222,0.12) 0%, transparent 70%); border-radius: 28px; padding: 6px; }
.main-chart-canvas-box { flex: 1; min-height: 260px; }
.wave-chart-wrapper-v2 { height: 220px; background: rgba(0,12,18,0.7); border-radius: 24px; padding: 12px; margin-top: 14px; border: 1px solid rgba(0,193,222,0.3); }
.sub-title-glow { font-size: 12px; color: #88c8e0; text-align: center; }
.echarts-dom { width: 100%; height: 100%; min-height: 200px; }
.full-height { height: 100%; display: flex; flex-direction: column; }
.flex-fill-card { flex: 1; display: flex; flex-direction: column; }
.alert-scroll-window { flex: 1; overflow: hidden; margin-top: 12px; }
.modern-capsule { background: rgba(10,25,35,0.8); border: 1px solid rgba(0,193,222,0.4); border-radius: 40px; padding: 8px 16px; margin-bottom: 12px; display: flex; justify-content: space-between; font-size: 11px; }
.modern-capsule.info { border-left: 6px solid #00c1de; }
.modern-capsule .t { color: #00c1de; font-family: monospace; }
.scrolling { animation: scrollUp 28s linear infinite; }
@keyframes scrollUp { 0% { transform: translateY(0); } 100% { transform: translateY(-50%); } }
.bottom-signal-tip-fixed-v2 { background: rgba(0,20,28,0.8); border-radius: 32px; padding: 8px 12px; font-size: 11px; display: flex; align-items: center; gap: 8px; margin-top: 16px; border: 1px solid #2c6a7a; }
.pulse-dot { width: 8px; height: 8px; background: #52c41a; border-radius: 50%; animation: pulse 1.2s infinite; }
@keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
.title-text-glow { font-size: 24px; font-weight: 900; background: linear-gradient(135deg, #b0f0ff, #00c1de); -webkit-background-clip: text; background-clip: text; color: transparent; }
.time-box { font-family: monospace; font-size: 18px; color: #0cf; margin-right: 100px; }
.ghost-cyan-glow { background: transparent; border: 1.2px solid #00c1de; color: #00c1de; padding: 6px 20px; border-radius: 36px; cursor: pointer; }
.ghost-cyan-glow:hover { background: #00c1de20; box-shadow: 0 0 12px #00c1de; }
.margin-top-sm { margin-top: 16px; }
.text-center { text-align: center; }
.scroll-y::-webkit-scrollbar { width: 4px; }
.scroll-y::-webkit-scrollbar-track { background: #03161f; }
.scroll-y::-webkit-scrollbar-thumb { background: #00c1de; border-radius: 10px; }
/* 自动滚动开关样式 */
.auto-scroll-switch {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  font-size: 14px;
}
.switch {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 24px;
}
.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}
.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #2c3e50;
  transition: 0.3s;
  border-radius: 24px;
}
.slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: 0.3s;
  border-radius: 50%;
}
input:checked + .slider {
  background-color: #00c1de;
}
input:checked + .slider:before {
  transform: translateX(26px);
}
.hint {
  font-size: 12px;
  color: #88c8e0;
}
</style>