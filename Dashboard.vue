<template>
  <div class="dashboard-wrapper">
    <div class="grid-bg"></div>

    <header class="custom-header">
      <div class="header-content-wrapper">
        <h1 class="title-text-glow">鏌旀€т紶鎰熷櫒浜轰綋濮挎€佹櫤鑳界洃娴嬬郴缁?/h1>
        <div class="center-status-wrapper">
          <div class="floating-status-pill" :class="statusClass">
            {{ postureStatus }}
          </div>
        </div>
        <div class="header-right">
          <div class="time-box">{{ currentTime }}</div>
          <button v-if="!isReading" class="nav-btn ghost-cyan-glow" @click="connectSerial" :disabled="!isWebSerialSupported">
            杩炴帴涓插彛
          </button>
          <button v-else class="nav-btn ghost-cyan-glow" @click="disconnectSerial">
            鏂紑涓插彛
          </button>
          <button class="nav-btn ghost-cyan-glow" @click="$router.push('/admin')">鍚庡彴绠＄悊</button>
          <button class="nav-btn ghost-cyan-glow logout-btn" @click="logout">閫€鍑虹櫥褰?/button>
        </div>
      </div>
    </header>

    <main class="main-content">
      <!-- 宸︿晶闈㈡澘锛氭坊鍔?ref 鐢ㄤ簬鍚屾婊氬姩 -->
      <section class="grid-cell left-panel scroll-y" ref="leftScrollRef">
        <div class="glass-card">
          <h3 class="card-title-glow">瀹炴椂杞借嵎鏁板€?(A0-A3)</h3>
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
            <div class="f-stat">鎬昏浇鑽?<span class="cyan-glow">{{ totalLoad.toFixed(1) }} g</span></div>
            <div class="f-stat">绯荤粺閲囨牱鐜?<span class="green-glow">40 Hz</span></div>
          </div>
        </div>

        <div class="glass-card margin-top-sm">
          <h3 class="card-title-glow">鏍囧噯濮挎€佸畾鏍?/h3>
          <div class="aligned-setting-list">
            <div class="calib-baseline-row">
              <span class="label-sm">1. 纭欢褰掗浂锛?/span>
              <button class="m-btn-glow" @click="calibrateBaseline" :disabled="calibrating">
                {{ calibrating ? '褰掗浂涓?..' : '涓€閿綊闆? }}
              </button>
              <p class="desc">璇蜂繚鎸佷紶鎰熷櫒绌鸿浇锛岀偣鍑诲悗绛夊緟5绉?/p>
            </div>
            
            <div class="calib-baseline-row margin-top-sm">
              <span class="label-sm">2. 褰曞叆鏍囧噯鍧愬Э锛?/span>
              <p class="desc">绔鍧愬ソ鍚庣偣鍑伙紝绯荤粺灏嗕互姝や负鍩哄噯鐩戞祴</p>
              <button class="m-btn-glow primary-border" @click="captureStandardPosture">
                褰曞叆褰撳墠濮挎€佷负鏍囧噯
              </button>
              <div v-if="isReading && standardTotalLoad === 0" class="hint-text">
                鈿狅笍 褰撳墠灏氭湭褰曞叆鏍囧噯鍘嬪姏鍊硷紝璇风姝ｅ潗濮垮悗鐐瑰嚮鈥滃綍鍏ュ綋鍓嶅Э鎬佷负鏍囧噯鈥?
              </div>
              <div v-else-if="standardTotalLoad > 0" class="ref-info-box">
                馃幆 鏍囧噯鎬昏浇鑽? {{ standardTotalLoad.toFixed(1) }}g &nbsp;| 
                閲嶅績: ({{ standardCop.x.toFixed(1) }}, {{ standardCop.y.toFixed(1) }})
              </div>
            </div>

            <div class="aligned-row margin-top-sm">
              <span>鍘嬪姏瓒呴檺姣斾緥锛?/span>
              <div class="r-group">
                <input type="number" class="c-input-glow" v-model.number="pressureRatioThreshold" step="0.05" min="1.0">
                <span class="unit cyan-glow">鍊?/span>
              </div>
            </div>
            <div class="aligned-row margin-top-sm">
              <span>閲嶅績鍋忕Щ瀹瑰繊锛?/span>
              <div class="r-group">
                <input type="number" class="c-input-glow" v-model.number="copDistanceThreshold" step="0.2" min="0">
                <span class="unit cyan-glow">cm</span>
              </div>
            </div>

            <div class="aligned-row margin-top-sm">
              <span>姝诲尯闃堝€硷細</span>
              <div class="r-group">
                <input type="number" class="c-input-glow" v-model.number="deadzoneThreshold" step="0.1" min="0" max="5">
                <span class="unit cyan-glow">g</span>
              </div>
            </div>
          </div>
        </div>

        <div class="glass-card margin-top-sm">
          <h3 class="card-title-glow">鍚庡彴鍒ゅ畾鍙傛暟</h3>
          <div class="aligned-row">
            <span>绂诲骇鏈€灏忚浇鑽凤細</span>
            <span class="cyan-glow">{{ backendPressureThreshold.toFixed(1) }} g</span>
          </div>
          <div class="aligned-row margin-top-sm">
            <span>寮傚父瑙﹀彂鏃堕暱锛?/span>
            <span class="cyan-glow">{{ backendTimeLimit }} s</span>
          </div>
          <div class="aligned-row margin-top-sm">
            <span>鍘嬪姏寮傚父姣斾緥闃堝€硷細</span>
            <span class="cyan-glow">{{ backendPressureRatioThreshold.toFixed(2) }}x</span>
          </div>
          <div class="aligned-row margin-top-sm">
            <span>閲嶅績鍋忕Щ鍒ゅ畾闃堝€硷細</span>
            <span class="cyan-glow">{{ backendCopDistanceThreshold.toFixed(2) }} cm</span>
          </div>
          <p class="desc">鍚庡彴绠＄悊涓缃彉鍖栨椂锛屾澶勪細绔嬪嵆鍒锋柊骞跺奖鍝嶅綋鍓嶅垽瀹氶€昏緫銆?/p>
        </div>

        <div class="glass-card margin-top-sm flex-fill-card">
          <h3 class="card-title-glow">鍒嗗姏鍚戦噺鍒嗗竷</h3>
          <div class="radar-dom-container"><div ref="polarChartRef" class="echarts-dom"></div></div>
        </div>
      </section>

      <!-- 涓ぎ闈㈡澘锛堜笉鍙備笌鍚屾婊氬姩锛?-->
      <section class="grid-cell center-stage">
        <div class="display-flex-column full-height">
          <div class="main-chart-outer flex-fill-main-v2">
            <div class="inline-card-header-v2">
              <h3 class="card-title-glow">閲嶅績鍋忕鐩戞祴 (Toe 鏈濆彸)</h3>
            </div>
            <div class="main-chart-canvas-box">
              <div ref="mainChartRef" class="echarts-dom"></div>
            </div>
          </div>
          <div class="wave-chart-wrapper-v2 flex-shrink-0">
            <h4 class="sub-title-glow text-center">鍥涜矾瀹炴椂娉㈠舰鐩戞帶 (A0-A3)</h4>
            <div ref="multiWaveRef" style="width: 100%; height: 210px;"></div>
          </div>
        </div>
      </section>

      <!-- 鍙充晶闈㈡澘锛氭坊鍔?ref 鐢ㄤ簬鍚屾婊氬姩 -->
      <section class="grid-cell right-panel scroll-y" ref="rightScrollRef">
        <div class="glass-card">
          <h3 class="card-title-glow">閲嶅績璇︾粏鍙傛暟</h3>
          <div class="stats-dark-row">
            <div class="stat-dark-item"><span class="stat-l">褰撳墠 X</span><span class="stat-v cyan-glow">{{ currentCop.x.toFixed(2) }}</span></div>
            <div class="stat-dark-item"><span class="stat-l">褰撳墠 Y</span><span class="stat-v green-glow">{{ currentCop.y.toFixed(2) }}</span></div>
          </div>
          <div class="stats-dark-row margin-top-sm">
            <div class="stat-dark-item"><span class="stat-l">鍘嬪姏姣斾緥</span><span class="stat-v" :class="pressureRatio >= pressureRatioThreshold ? 'danger-text' : 'safe-text'">{{ pressureRatio.toFixed(2) }}x</span></div>
            <div class="stat-dark-item"><span class="stat-l">閲嶅績鍋忕Щ</span><span class="stat-v" :class="copDistance >= copDistanceThreshold ? 'danger-text' : 'safe-text'">{{ copDistance.toFixed(2) }} cm</span></div>
          </div>
        </div>

        <div class="glass-card margin-top-sm">
          <h3 class="card-title-glow">濮挎€佹椂闂村垎甯?(H)</h3>
          <div class="pie-dom-container"><div ref="pieChartRef" class="echarts-dom"></div></div>
        </div>

        <!-- 鑷姩婊氬姩寮€鍏冲尯鍩?-->
        <div class="glass-card margin-top-sm">
          <div class="auto-scroll-switch">
            <span class="label">馃摐 鑷姩婊氬姩妯″紡</span>
            <label class="switch">
              <input type="checkbox" v-model="autoScrollEnabled" @change="toggleAutoScroll">
              <span class="slider round"></span>
            </label>
            <span class="hint">{{ autoScrollEnabled ? '寮€鍚腑' : '宸插叧闂? }}</span>
          </div>
        </div>

        <div class="glass-card margin-top-sm flex-fill-card">
          <h3 class="card-title-glow card-header-fixed">瀹炴椂琛屼负蹇</h3>
          <div class="alert-scroll-window">
            <ul class="alert-list-dynamic scrolling">
              <li v-for="(alert, index) in alertHistory" :key="index" :class="['modern-capsule', alert.type]">
                <span class="t">{{ alert.time }}</span><span class="m">{{ alert.msg }}</span>
              </li>
            </ul>
          </div>
        </div>

        <div class="bottom-signal-tip-fixed-v2">
          <span class="pulse-dot"></span> 鍚庣鏁版嵁娴佹甯歌幏鍙栦腑...
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { io } from 'socket.io-client'

// ---------- WebSocket 杩炴帴 ----------
// Socket.IO 杩炴帴瀵硅薄锛堟寜闇€鍒涘缓锛?
let socket = null

// ---------- Web Serial API 鐩稿叧 ----------
// 妫€鏌ユ祻瑙堝櫒鏀寔
const isWebSerialSupported = 'serial' in navigator
let port = null
let reader = null
const isReading = ref(false)

// 涓插彛閰嶇疆锛堜笌鍚庣淇濇寔涓€鑷达級
const SERIAL_BAUD_RATE = 115200
const CALIB_FACTOR = 500.0 / 1023.0
const DEFAULT_DEADZONE = 0.1  // 榛樿姝诲尯闃堝€?

const backendApiUrl = 'http://localhost:5000'

// 鍚庣鍚屾闃堝€?
const backendPressureThreshold = ref(20)
const backendTimeLimit = ref(120)
const backendPressureRatioThreshold = ref(1.2)
const backendCopDistanceThreshold = ref(1.2)

// 鍙厤缃弬鏁?
const deadzoneThreshold = ref(DEFAULT_DEADZONE)

// 淇″彿澶勭悊鍙橀噺锛堜笌鍚庣淇濇寔涓€鑷达級
let baselines = [0.0, 0.0, 0.0, 0.0]
let isCalibrated = false
let calibrationCounter = 0
const CALIBRATION_SAMPLES = 50
const filterQueues = [[], [], [], []]

// ---------- Web Serial API 鍑芥暟 ----------
// 杩炴帴 Socket.IO 鏈嶅姟鍣?
const connectSocket = () => {
  if (socket && socket.connected) {
    postureStatus.value = '鉁?宸查€氳繃 Socket.IO 杩炴帴鍒板悗绔?
    addAlertMessage('宸查€氳繃 Socket.IO 杩炴帴鍚庣', 'info')
    return
  }

  postureStatus.value = '姝ｅ湪杩炴帴鍚庣鏈嶅姟鍣?..'
  socket = io(backendApiUrl)

  socket.on('connect', () => {
    isReading.value = true
    addAlertMessage('鉁?Socket.IO 宸茶繛鎺?, 'info')
    postureStatus.value = '鉁?绯荤粺宸插氨缁紝鎺ユ敹鏁版嵁涓?..'
  })

  // 鏍稿績锛氱洃鍚悗绔彂閫佺殑瀹炴椂浼犳劅鍣ㄦ暟鎹?
  socket.on('sensorData', (data) => {
    if (data && data.pressures && isCalibrated) {
      updateSensorData(data.pressures)
    }
  })

  socket.on('disconnect', () => {
    isReading.value = false
    postureStatus.value = '鉂?涓庡悗绔繛鎺ユ柇寮€'
    addAlertMessage('鍚庣 Socket.IO 杩炴帴宸叉柇寮€', 'error')
  })

  socket.on('connect_error', () => {
    postureStatus.value = '鉂?杩炴帴澶辫触锛岃妫€鏌ュ悗绔▼搴?
  })
}

// 鏂紑 Socket.IO 杩炴帴
const disconnectSocket = () => {
  if (socket) {
    socket.disconnect()
    socket = null
    isReading.value = false
    postureStatus.value = '馃攲 宸叉柇寮€杩炴帴'
  }
}

// 璇锋眰鐢ㄦ埛閫夋嫨涓插彛
const connectSerial = async () => {
  // 棣栧厛灏濊瘯閫氳繃 Socket.IO 杩炴帴鍚庣
  connectSocket()

  try {
    // 濡傛灉涔嬪墠鏈変竴涓墦寮€鐨勭鍙ｏ紝鍏堟柇寮€瀹冿紝閬垮厤閲嶅鎵撳紑
    if (port) {
      await disconnectSerial()
    }

    // 璇锋眰鐢ㄦ埛閫夋嫨涓插彛
    port = await navigator.serial.requestPort()
    
    // 鎵撳紑涓插彛
    await port.open({ 
      baudRate: SERIAL_BAUD_RATE,
      dataBits: 8,
      stopBits: 1,
      parity: 'none'
    })
    
    console.log('鉁?涓插彛宸茶繛鎺?)
    postureStatus.value = '鉁?涓插彛宸茶繛鎺ワ紝姝ｅ湪璇诲彇鏁版嵁...'
    addAlertMessage('涓插彛宸茶繛鎺?, 'info')
    
    // 寮€濮嬭鍙栨暟鎹紙涓峚wait锛屽湪鍚庡彴杩愯锛?
    startReading()

    if (standardTotalLoad.value === 0) {
      postureStatus.value = '璇峰綍鍏ュ帇鍔涙爣鍑嗗€?
      alert('璇峰綍鍏ュ帇鍔涙爣鍑嗗€硷細鐐瑰嚮鈥滃綍鍏ュ綋鍓嶅Э鎬佷负鏍囧噯鈥?)
      addAlertMessage('璇峰綍鍏ュ帇鍔涙爣鍑嗗€?, 'warning')
    }
  } catch (error) {
    console.error('鉂?涓插彛杩炴帴澶辫触:', error)
    postureStatus.value = '鉂?涓插彛杩炴帴澶辫触锛? + (error.message || error)
    addAlertMessage('涓插彛杩炴帴澶辫触: ' + (error.message || error), 'error')
  }
}

// 寮€濮嬭鍙栦覆鍙ｆ暟鎹?
const startReading = async () => {
  if (!port || isReading.value) return
  
  isReading.value = true
  reader = port.readable.getReader()
  
  try {
    console.log('馃摗 寮€濮嬭鍙栦覆鍙ｆ暟鎹?..')
    while (true) {
      const { value, done } = await reader.read()
      if (done) break
      
      // 澶勭悊鎺ユ敹鍒扮殑鏁版嵁
      const line = new TextDecoder().decode(value).trim()
      if (line) {
        processSerialData(line)
      }
    }
  } catch (error) {
    console.error('鉂?璇诲彇涓插彛鏁版嵁鍑洪敊:', error)
    postureStatus.value = '鉂?涓插彛璇诲彇涓柇锛? + (error.message || error)
    addAlertMessage('涓插彛璇诲彇鍑洪敊: ' + (error.message || error), 'error')
  } finally {
    isReading.value = false
    if (reader) {
      reader.releaseLock()
      reader = null
    }
  }
}

// 澶勭悊涓插彛鏁版嵁锛堜笌鍚庣閫昏緫淇濇寔涓€鑷达級
const processSerialData = (line) => {
  const parts = line.replace(/\s/g, '').split(',')
  if (parts.length === 4) {
    try {
      const rawVals = parts.map(p => parseFloat(p))
      const pressures = processSignals(rawVals)
      
      if (isCalibrated) {
        // 鏇存柊鍓嶇鐘舵€?
        updateSensorData(pressures)
      }
    } catch (e) {
      console.warn('鏁版嵁瑙ｆ瀽澶辫触:', line)
    }
  }
}

// 淇″彿澶勭悊锛堝鍒跺悗绔€昏緫锛?
const processSignals = (rawVals) => {
  // 1. 纭欢褰掗浂闃舵
  if (!isCalibrated) {
    for (let i = 0; i < 4; i++) {
      baselines[i] += rawVals[i]
    }
    calibrationCounter++
    
    if (calibrationCounter >= CALIBRATION_SAMPLES) {
      baselines = baselines.map(b => b / CALIBRATION_SAMPLES)
      isCalibrated = true
      console.log('纭欢鐜褰掗浂瀹屾垚锛佸熀鍑嗗€?', baselines)
      addAlertMessage('纭欢褰掗浂瀹屾垚', 'info')
      // 娓呯┖婊ゆ尝闃熷垪
      filterQueues.forEach(q => q.length = 0)
    }
    return [0, 0, 0, 0]
  }
  
  // 2. 鍑忓幓鍩哄噯骞舵护娉?
  const calibratedVals = rawVals.map((raw, i) => Math.max(0, raw - baselines[i]))
  
  const filteredVals = []
  for (let i = 0; i < 4; i++) {
    filterQueues[i].push(calibratedVals[i])
    if (filterQueues[i].length > 10) filterQueues[i].shift()
    const avg = filterQueues[i].reduce((a, b) => a + b, 0) / filterQueues[i].length
    filteredVals.push(avg)
  }
  
  // 3. 杞崲鍗曚綅骞跺簲鐢ㄦ鍖?
  const pressures = filteredVals.map(v => v * CALIB_FACTOR)
  return pressures.map(p => p > deadzoneThreshold.value ? p : 0)
}

// 鏇存柊浼犳劅鍣ㄦ暟鎹?
const updateSensorData = (newPressures) => {
  pressures.value = newPressures
  currentCop.value = computeCop(pressures.value)
  const isGood = evaluatePosture()
  updatePieChart(isGood)
  updateAllCharts()
}

// 鏂紑涓插彛杩炴帴
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
  isReading.value = false
  isCalibrated = false
  calibrationCounter = 0
  baselines = [0, 0, 0, 0]
  postureStatus.value = '涓插彛宸叉柇寮€'
  addAlertMessage('涓插彛宸叉柇寮€', 'info')
}

// ---------- 鍝嶅簲寮忕姸鎬?----------
const pressures = ref([0, 0, 0, 0])
const currentCop = ref({ x: 0, y: 0 })
const postureStatus = ref('姝ｅ湪杩炴帴绯荤粺...')
const currentTime = ref(new Date().toLocaleTimeString())
const alertHistory = ref([{ time: '绯荤粺', msg: '浼犳劅鍣ㄩ€氫俊宸插氨缁?, type: 'info' }])

// 鏍囧噯鍧愬Э鏁版嵁
const standardTotalLoad = ref(0)
const standardCop = ref({ x: 0, y: 0 })
const standardPressures = ref([0, 0, 0, 0])

// 鐢ㄦ埛鍙皟闃堝€硷紙鍓嶇鏈湴瀛樺偍锛?
const pressureRatioThreshold = ref(1.2)
const copDistanceThreshold = ref(1.2)

// UI 鐘舵€?
const calibrating = ref(false)
const hasValidData = ref(false)

// 婊氬姩鍚屾鐩稿叧
const leftScrollRef = ref(null)
const rightScrollRef = ref(null)
let isSyncing = false  // 闃叉寰幆瑙﹀彂

// ---------- 鑷姩婊氬姩鐩稿叧 ----------
const autoScrollEnabled = ref(false)
let autoScrollTimer = null
let autoScrollPaused = false       // 鐢ㄦ埛鎵嬪姩婊氬姩鏃朵复鏃舵殏鍋?
let pauseTimeout = null

// 娉㈠舰缂撳啿鍖?
const WAVE_LEN = 100
const waveData = ref({
  A0: new Array(WAVE_LEN).fill(0),
  A1: new Array(WAVE_LEN).fill(0),
  A2: new Array(WAVE_LEN).fill(0),
  A3: new Array(WAVE_LEN).fill(0)
})
let waveIndex = 0
const xAxisData = ref(Array.from({ length: WAVE_LEN }, (_, i) => i))

// 楗煎浘绱鏃堕棿
let goodTime = 0, badTime = 0
let lastTimestamp = 0
let currentGood = true

// ECharts 瀹炰緥
let waveChart = null
let footChart = null
let pieChart = null
let radarChart = null

const multiWaveRef = ref(null)
const mainChartRef = ref(null)
const pieChartRef = ref(null)
const polarChartRef = ref(null)

const router = useRouter()

// 閲嶆柊璁捐鐨勫乏鑴氬舰鐘跺潗鏍囷細澧炲己鑴氳毒娉㈡氮鎰熷拰瓒冲紦娣卞害
// 閲嶆柊璁捐鐨勫乏鑴氬舰鐘跺潗鏍囷細瀹屽叏妯℃嫙鍥句竴鐨?5 涓渾寮ц剼瓒惧拰楗辨弧杞粨
// 閲嶆柊璁捐鐨勫乏鑴氬舰鐘跺潗鏍?(Toe鏈濆彸)
// 鐗圭偣锛氬彸渚ц剼瓒句粠灏忓埌澶ф帓鍒楋紝涓嬫柟瓒冲紦澶у集鏇诧紝涓婃柟澶栫紭灏忓集鏇?
// 閲嶆柊璁捐鐨勫乏鑴氬舰鐘跺潗鏍?(Toe鏈濆彸)
// 1. 鑴氳毒鍦嗘鼎鍖栵細閫氳繃澧炲姞杩囨浮鐐规秷闄ゅ皷鍒恒€?
// 2. 鎺岄儴鍔犲锛氬鍔犲ぇ鑴氳毒鍜屽皬鑴氳毒闄勮繎鐨?Y 杞撮棿璺濄€?
// 3. 瓒冲紦宸︾Щ锛氬皢涓嬫柟澶у集鏇茬殑娉㈣胺鍚戝乏渚э紙璐?X 鏂瑰悜锛夊亸绉汇€?
// 閲嶆柊璁捐鐨勫乏鑴氬舰鐘跺潗鏍?(Toe鏈濆彸)
// 1. 鎾戝紑鎺岄儴锛氭樉钁楀鍔犲彸渚ц剼瓒惧尯鍩熺殑 Y 杞磋法搴︼紙浠?4.5 鍒?-7.5锛?
// 2. 妯℃嫙鍥句簩锛氫簲涓渾婊戝姬绾胯剼瓒撅紝涓嬫柟鍐呭集澶у渾寮у乏绉诲苟鍔犲鍙充晶杩炴帴澶?
// 閲嶆柊璁捐鐨勫乏鑴氬舰鐘跺潗鏍?(Toe鏈濆彸) 
// 鐗圭偣锛氫笅鏂瑰唴寮彸渚ф湁鍚戝澶у集鏇诧紝涓婃柟鍐呭集鍙充晶鏈夊悜澶栧皬寮洸锛屾帉閮ㄥ鍘?
// 閲嶆柊璁捐鐨勫乏鑴氬舰鐘跺潗鏍?(Toe鏈濆彸)
// 鏍稿績鏀瑰姩锛氭樉钁楀寮轰簡涓嬫柟瓒冲紦锛堝唴寮級鍙充晶鐨勫悜澶栧嚫璧凤紙澶栧集锛夛紝浣挎帉閮ㄧ湅璧锋潵闈炲父楗辨弧
// 閲嶆柊璁捐鐨勫乏鑴氬舰鐘跺潗鏍?(Toe鏈濆彸)  
// ==================== 绮剧‘鐨勫彸鑴氳疆寤擄紙Toe 鏈濆彸锛?涓渾寮ц剼瓒撅紝涓嶇矘杩烇級 ====================
const footOutline = [
  // --- 鍙充晶 5 涓剼瓒?(鐗圭偣锛氬ご閮?鏍归儴鍧囧姞瀹斤紝灏忚毒涓婄Щ锛岃毒缂濇竻鏅颁笉绮樿繛) ---
  // 灏忚剼瓒?(涓婄Щ骞跺姞瀹斤紝澶撮儴鍦嗘鼎)
  [7.2, 5.0], [8.5, 5.4], [9.2, 5.8], [9.4, 5.0], [9.2, 4.2], [8.5, 4.0], [7.2, 4.2], 
  // 绗洓瓒?(澧炲姞鏍归儴瀹藉害锛屾媺寮€涓庡皬瓒剧殑鍨傜洿璺濈)
  [7.4, 2.6], [8.6, 3.0], [9.6, 3.6], [9.8, 2.8], [9.6, 2.0], [8.6, 1.6], [7.4, 2.0],
  // 绗笁瓒?
  [7.7, 0.2], [8.9, 0.5], [10.0, 1.3], [10.2, 0.3], [10.0, -0.7], [8.9, -1.1], [7.7, -0.7],
  // 绗簩瓒?(鏄庢樉鍔犲锛屽ご閮ㄦ瀬鍦?
  [8.0, -2.6], [9.2, -1.9], [10.6, -1.2], [11.0, -2.7], [10.6, -4.2], [9.2, -4.7], [8.0, -4.0],
  // 澶ц剼瓒?(鏋佸叾瀹藉ぇ楗辨弧锛屼綋鐜版牴閮ㄤ笌澶撮儴鍚屾鍙樺)
  [8.2, -5.9], [9.7, -6.2], [11.2, -6.9], [11.7, -8.4], [11.2, -10.2], [9.7, -10.9], [8.2, -9.9],

  // --- 涓嬫柟锛氳冻寮撳強鍙充晶鎵╁紶 (瀵瑰簲鍥句笁绾㈢嚎楗辨弧寮у害) ---
  [4.5, -11.6], [1.5, -12.4], [-2.5, -6.5], [-6.5, -9.5], [-9.5, -9.0], 

  // --- 宸︿晶锛氳剼鍚庤窡 (鍦嗘鼎楗辨弧) ---
  [-11.5, -5.0], [-12.5, 0], [-11.5, 5.0], 

  // --- 涓婃柟锛氳冻澶栦晶鍙婂彸渚ф墿寮?---
  [-8.0, 8.2], [-3.0, 6.8], [1.5, 8.8], [5.5, 8.2], 

  [7.2, 5.0] // 鍥炲埌璧峰鐐归棴鍚?
]

// ==================== 浼犳劅鍣ㄥ潗鏍囷紙涓庤剼褰㈠尮閰嶏紝閲嶅績璁＄畻鍚堢悊锛?====================
// 浼犳劅鍣ㄥ潗鏍?
const sensorPos = [
  { x: 4.5, y: 5.5 },
  { x: -4.5, y: 5.5 },
  { x: 3.5, y: -4.5 },
  { x: -3.5, y: -4.5 }
]

// 璁＄畻灞炴€?
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
  if (postureStatus.value.includes('璀﹀憡') || postureStatus.value.includes('棰勮')) return 'danger-bg'
  if (postureStatus.value.includes('鑹ソ')) return 'safe-bg'
  return 'idle-bg'
})

// 濮挎€佸垽瀹氶€昏緫
let warningStartAt = null

const evaluatePosture = () => {
  const load = totalLoad.value
  const minLoad = backendPressureThreshold.value ?? 5
  const timeLimitMs = Math.max(0, backendTimeLimit.value || 0) * 1000
  if (load < minLoad) {
    warningStartAt = null
    postureStatus.value = '绂诲骇 / 绌洪棽'
    return false
  }
  hasValidData.value = true
  if (standardTotalLoad.value === 0) {
    warningStartAt = null
    postureStatus.value = '璇峰厛褰曞叆鏍囧噯濮挎€?
    return false
  }
  const pressureLimit = backendPressureRatioThreshold.value || pressureRatioThreshold.value
  const copLimit = backendCopDistanceThreshold.value || copDistanceThreshold.value
  const isPressureOver = pressureRatio.value > pressureLimit
  const isCopOver = copDistance.value > copLimit
  const isWarning = isPressureOver || isCopOver
  if (!isWarning) {
    warningStartAt = null
    postureStatus.value = '鉁?鍧愬Э淇濇寔鑹ソ'
    return true
  }

  if (!warningStartAt) {
    warningStartAt = Date.now()
  }
  const elapsed = Date.now() - warningStartAt
  const issues = []
  if (isPressureOver) issues.push(`鍘嬪姏寮傚父 ${pressureRatio.value.toFixed(1)}x`)
  if (isCopOver) issues.push(`閲嶅績鍋忕Щ ${copDistance.value.toFixed(1)}cm`)
  const issueText = issues.join(' & ')

  if (elapsed < timeLimitMs) {
    postureStatus.value = `鈿狅笍 棰勮锛?{issueText}锛屾寔缁?${backendTimeLimit.value}s 鍚庣‘璁
    return false
  }

  postureStatus.value = `鈿狅笍 璀﹀憡锛?{issueText}`
  return false
}

// 楗煎浘鏇存柊
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
          { value: goodTime, name: '鑹ソ濮挎€? },
          { value: badTime, name: '寮傚父濮挎€? }
        ]
      }]
    })
  }
}

// 鍥捐〃鏇存柊鍑芥暟
const updateWaveform = () => {
  if (!waveChart) return
  waveData.value.A0.push(pressures.value[0])
  waveData.value.A1.push(pressures.value[1])
  waveData.value.A2.push(pressures.value[2])
  waveData.value.A3.push(pressures.value[3])
  if (waveData.value.A0.length > WAVE_LEN) waveData.value.A0.shift()
  if (waveData.value.A1.length > WAVE_LEN) waveData.value.A1.shift()
  if (waveData.value.A2.length > WAVE_LEN) waveData.value.A2.shift()
  if (waveData.value.A3.length > WAVE_LEN) waveData.value.A3.shift()
  waveIndex++
  xAxisData.value.push(waveIndex)
  if (xAxisData.value.length > WAVE_LEN) xAxisData.value.shift()
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
      { name: '褰撳墠閲嶅績', data: currentPoint },
      { name: '鏍囧噯閲嶅績', data: standardPoint }
    ]
  })
}

const updateRadar = () => {
  if (!radarChart) return
  radarChart.setOption({
    series: [{ data: [{ value: pressures.value }] }]
  })
}

const updateAllCharts = () => {
  updateWaveform()
  updateFootChart()
  updateRadar()
}

// 璁＄畻閲嶅績
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

// 淇濆瓨鏍囧噯鏁版嵁鍒?localStorage
const saveStandardToLocal = () => {
  localStorage.setItem('standardTotalLoad', standardTotalLoad.value)
  localStorage.setItem('standardCopX', standardCop.value.x)
  localStorage.setItem('standardCopY', standardCop.value.y)
  localStorage.setItem('standardPressures', JSON.stringify(standardPressures.value))
}

// 浠?localStorage 鍔犺浇鏍囧噯鏁版嵁
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

// 鍓嶇纭欢褰掗浂锛堢洿鎺ユ搷浣滃墠绔姸鎬侊級
const calibrateBaseline = () => {
  calibrating.value = true
  addAlertMessage("姝ｅ湪鎵ц纭欢褰掗浂锛岃淇濇寔浼犳劅鍣ㄧ┖杞?..", "info")
  
  // 閲嶇疆鍓嶇鏍″噯鐘舵€?
  baselines = [0.0, 0.0, 0.0, 0.0]
  calibrationCounter = 0
  isCalibrated = false
  filterQueues.forEach(q => q.length = 0)
  
  // 閲嶇疆鏍囧噯鏁版嵁
  standardTotalLoad.value = 0
  standardCop.value = { x: 0, y: 0 }
  standardPressures.value = [0, 0, 0, 0]
  saveStandardToLocal()
  
  setTimeout(() => {
    addAlertMessage("纭欢褰掗浂瀹屾垚锛岃寮€濮嬪綍鍏ユ爣鍑嗗潗濮?, "info")
    calibrating.value = false
  }, 5000)
}

// 鍓嶇褰曞叆鏍囧噯鍧愬Э
const captureStandardPosture = () => {
  if (!isCalibrated) {
    alert('璇峰厛鐐瑰嚮鈥滀竴閿綊闆垛€濓紝绛夊緟褰掗浂瀹屾垚鍚庡啀褰曞叆鏍囧噯鍧愬Э銆?)
    addAlertMessage('鏈畬鎴愬綊闆讹紝褰曞叆澶辫触', 'error')
    return
  }

  const minLoad = 5
  const currentLoad = totalLoad.value
  if (currentLoad < minLoad) {
    const loadText = currentLoad.toFixed(1)
    const thresholdText = minLoad.toFixed(1)
    const hint = currentLoad === 0
      ? '褰撳墠鏈娴嬪埌鏈夋晥杞借嵎锛屽彲鑳藉皻鏈帴瑙︿紶鎰熷櫒鎴栦紶鎰熷櫒鏈繛鎺ャ€?
      : `褰撳墠鎬昏浇鑽?${loadText}g锛岄渶鑷冲皯 ${thresholdText}g銆俙
    alert(`鍘嬪姏杩囧皬锛岃绔鍧愬Э骞跺鍔犲帇鍔涘悗鍐嶅綍鍏ワ紒\n${hint}`)
    addAlertMessage(`鍘嬪姏杩囧皬锛屽綍鍏ュけ璐ワ紙褰撳墠 ${loadText}g锛塦, 'error')
    console.warn(`鏍囧噯濮挎€佸綍鍏ュけ璐ワ細鎬昏浇鑽?${loadText}g锛岄槇鍊?${thresholdText}g`)
    return
  }
  
  // 鐩存帴淇濆瓨褰撳墠鏁版嵁
  standardTotalLoad.value = currentLoad
  standardPressures.value = [...pressures.value]
  standardCop.value = computeCop(standardPressures.value)
  saveStandardToLocal()
  
  alert(`鉁?鏍囧噯濮挎€佸凡褰曞叆锛乗n鎬昏浇鑽凤細${standardTotalLoad.value.toFixed(1)}g\n閲嶅績锛?${standardCop.value.x.toFixed(1)}, ${standardCop.value.y.toFixed(1)})`)
  addAlertMessage(`鏍囧噯濮挎€佸凡褰曞叆 (鎬昏浇鑽?${standardTotalLoad.value.toFixed(1)}g)`, "info")
}

const addAlertMessage = (msg, type = 'info') => {
  const timeStr = new Date().toLocaleTimeString().slice(0,5)
  alertHistory.value.unshift({ time: timeStr, msg, type })
  if (alertHistory.value.length > 12) alertHistory.value.pop()
}

// 浠庡悗绔姞杞芥爣鍑嗘暟鎹?
const loadStandardFromBackend = async () => {
  try {
    const res = await fetch('http://localhost:5000/api/get_settings')
    const data = await res.json()
    if (data.refTotal && data.refTotal > 0 && data.refCop && data.refCop.length === 2) {
      standardTotalLoad.value = data.refTotal
      standardCop.value = { x: data.refCop[0], y: data.refCop[1] }
      standardPressures.value = [0, 0, 0, 0]
      saveStandardToLocal()
      addAlertMessage(`宸蹭粠鍚庣鎭㈠鏍囧噯鏁版嵁锛氭€昏浇鑽?${standardTotalLoad.value.toFixed(1)}g锛岄噸蹇?${standardCop.value.x.toFixed(1)}, ${standardCop.value.y.toFixed(1)})`, "info")
      return true
    }
  } catch (err) {
    console.error("浠庡悗绔姞杞芥爣鍑嗘暟鎹け璐?, err)
  }
  return false
}

// 鏈湴瀛樺偍闃堝€?
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

// 浠庡悗绔姞杞芥牳蹇冪畻娉曢槇鍊?
const loadBackendSettings = async () => {
  try {
    const res = await fetch(`${backendApiUrl}/api/get_settings`)
    if (!res.ok) throw new Error('鍚庣杩斿洖寮傚父')
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
      addAlertMessage(`宸插悓姝ュ悗绔缃細绂诲骇闃堝€?${backendPressureThreshold.value.toFixed(1)}g锛岃鍛婃椂闀?${backendTimeLimit.value}s锛屽帇鍔涙瘮渚?${backendPressureRatioThreshold.value.toFixed(2)}x锛屽亸绉婚槇鍊?${backendCopDistanceThreshold.value.toFixed(2)}cm`, 'info')
    }
  } catch (err) {
    console.warn('鏃犳硶鍔犺浇鍚庣闃堝€?', err)
  }
}

// 婊氬姩鍚屾澶勭悊鍑芥暟
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

// 鑷姩婊氬姩锛氱紦鎱㈠悜涓婃粴鍔ㄥ乏鍙抽潰鏉匡紝鍒拌揪搴曢儴鍚庡洖鍒伴《閮?
const startAutoScroll = () => {
  if (autoScrollTimer) clearInterval(autoScrollTimer)
  if (!leftScrollRef.value || !rightScrollRef.value) return

  const STEP = 8.0          // 姣忓抚绉诲姩鍍忕礌
  const INTERVAL = 15       // 姣

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

// 涓存椂鏆傚仠鑷姩婊氬姩锛堢敤鎴锋墜鍔ㄦ粴鍔ㄦ椂璋冪敤锛?
const pauseAutoScroll = () => {
  if (!autoScrollEnabled.value) return
  autoScrollPaused = true
  if (pauseTimeout) clearTimeout(pauseTimeout)
  pauseTimeout = setTimeout(() => {
    autoScrollPaused = false
  }, 5000)   // 5绉掑悗鎭㈠鑷姩婊氬姩
}

// 寮€鍏冲垏鎹?
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
  // 鐢ㄦ埛鎵嬪姩婊氬姩鏃讹紝涓存椂鏆傚仠鑷姩婊氬姩
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
    // 閿佸畾鑼冨洿锛氳缃负 -15 鍒?15銆?
    // 杩欒兘纭繚鏈€涓婃柟涓婄Щ鍒?5.8 鐨勫皬鑴氳毒涓嶈鍒囪竟锛屽苟鎷夊紑鏁翠綋鎺岄儴鐨勮瑙夐棿璺濄€?
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
      name: '瓒冲簳杞粨', 
      type: 'line', 
      // 鍏抽敭锛氬钩婊戝害淇濇寔鍦?0.36銆?
      // 杈冧綆鐨勫钩婊戝害鑳界‘淇濊剼瓒句箣闂村畾涔夌殑鈥滃嚬闄烽棿闅欌€濅笉琚畻娉曡嚜鍔ㄧ（骞宠瀺鍚堬紝浠庤€岄槻姝㈢矘杩炪€?
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
      name: '褰撳墠閲嶅績', 
      type: 'scatter', 
      data: [[currentCop.value.x, currentCop.value.y]], 
      symbolSize: 28, 
      itemStyle: { color: '#ff4d4f', shadowBlur: 15, borderColor: '#fff', borderWidth: 2 }, 
      label: { show: true, formatter: 'CoP', color: '#fff', fontSize: 10, offset: [0, -15] },
      zIndex: 10 
    },
    { name: '鏍囧噯閲嶅績', type: 'scatter', data: [], symbol: 'circle', symbolSize: 20, itemStyle: { color: 'transparent', borderColor: '#00c1de', borderType: 'dashed', borderWidth: 2 }, label: { show: true, formatter: '鏍囧噯', color: '#00c1de', fontSize: 10, offset: [0, -12] } }
  ]
})

  radarChart = echarts.init(polarChartRef.value)
  radarChart.setOption({
    radar: {
      indicator: [{ name: 'A0', max: 500 }, { name: 'A1', max: 500 }, { name: 'A2', max: 500 }, { name: 'A3', max: 500 }],
      center: ['50%', '50%'], radius: '70%', axisName: { color: '#00c1de' }
    },
    series: [{ type: 'radar', data: [{ value: [0,0,0,0], name: '瀹炴椂杞借嵎' }], areaStyle: { color: 'rgba(0,193,222,0.3)' }, lineStyle: { color: '#0cf', width: 2 } }]
  })

  waveChart = echarts.init(multiWaveRef.value)
  waveChart.setOption({
    grid: { left: '45', right: '15', top: '35', bottom: '30', containLabel: true },
    legend: { data: ['A0', 'A1', 'A2', 'A3'], textStyle: { color: '#9cd9e8' }, top: 0 },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: xAxisData.value, axisLabel: { color: '#8aaec0' } },
    yAxis: { type: 'value', min: 0, name: '杞借嵎 (g)', nameTextStyle: { color: '#00c1de' }, splitLine: { lineStyle: { color: 'rgba(0,193,222,0.2)' } } },
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
      data: [{ value: 0, name: '鑹ソ濮挎€? }, { value: 0, name: '寮傚父濮挎€? }],
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
  //   series: [{ type: 'radar', data: [{ value: [0,0,0,0], name: '瀹炴椂杞借嵎' }], areaStyle: { color: 'rgba(0,193,222,0.3)' }, lineStyle: { color: '#0cf', width: 2 } }]
  // })
  // waveChart = echarts.init(multiWaveRef.value)
  // waveChart.setOption({
  //   grid: { left: '45', right: '15', top: '35', bottom: '30', containLabel: true },
  //   legend: { data: ['A0', 'A1', 'A2', 'A3'], textStyle: { color: '#9cd9e8' }, top: 0 },
  //   tooltip: { trigger: 'axis' },
  //   xAxis: { type: 'category', data: xAxisData.value, axisLabel: { color: '#8aaec0' } },
  //   yAxis: { type: 'value', min: 0, name: '杞借嵎 (g)', nameTextStyle: { color: '#00c1de' }, splitLine: { lineStyle: { color: 'rgba(0,193,222,0.2)' } } },
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
  //     data: [{ value: 0, name: '鑹ソ濮挎€? }, { value: 0, name: '寮傚父濮挎€? }],
  //     itemStyle: { borderRadius: 10, borderColor: '#000d1a', borderWidth: 2, color: params => params.dataIndex === 0 ? '#00c1de' : '#ff4d4f' }
  //   }]
  // })


// 鐢熷懡鍛ㄦ湡
onMounted(async() => {
  loadThresholds();
  await loadBackendSettings();
  
  window.addEventListener('backend-settings-updated', loadBackendSettings)

  // ---------- Socket.IO 鑷姩杩炴帴 ----------
  connectSocket()

  // 妫€鏌eb Serial API鏀寔
  if (!isWebSerialSupported) {
    postureStatus.value = '娴忚鍣ㄤ笉鏀寔 Web Serial API'
    addAlertMessage('娴忚鍣ㄤ笉鏀寔 Web Serial API锛岃浣跨敤 Chrome 鎴?Edge', 'error')
  } else {
    postureStatus.value = '璇风偣鍑?杩炴帴涓插彛"寮€濮嬬洃娴?
    addAlertMessage('Web Serial API 鏀寔锛屽噯澶囪繛鎺ヤ覆鍙?, 'info')
  }
  
  // 鍔犺浇鏈湴鏍囧噯鏁版嵁锛堝悗绔笉鍙敤鏃讹級
  loadStandardFromLocal();
  
  // 鍏抽敭锛氫娇鐢?nextTick 纭繚鎵€鏈?DOM 鑺傜偣 (ref) 宸茬粡娓叉煋瀹屾垚
  await nextTick();
  // 澧炲姞涓€涓皬寤惰繜锛岀‘淇?CSS 鍔ㄧ敾锛堝鍏ㄥ睆杩囨浮锛変笉褰卞搷 ECharts 鑾峰彇瀹介珮
  setTimeout(() => {
    initCharts();
    if (autoScrollEnabled.value) {
      startAutoScroll();
    }
  }, 100);

  setInterval(() => { currentTime.value = new Date().toLocaleTimeString() }, 1000)
  window.addEventListener('resize', () => {
    [waveChart, footChart, radarChart, pieChart].forEach(ch => ch && ch.resize())
  })
  addAlertMessage("绯荤粺宸插惎鍔紝璇疯繛鎺ヤ覆鍙?, "info")

  // 鍔犺浇鑷姩婊氬姩寮€鍏崇姸鎬?
  const savedAutoScroll = localStorage.getItem('autoScrollEnabled')
  if (savedAutoScroll !== null) {
    autoScrollEnabled.value = savedAutoScroll === 'true'
  }
  // 绛夊緟 DOM 瀹屽叏娓叉煋鍚庯紝濡傛灉寮€鍏充负 true锛屽惎鍔ㄨ嚜鍔ㄦ粴鍔?
  await nextTick()
  if (autoScrollEnabled.value) {
    startAutoScroll()
  }

  // 娣诲姞婊氬姩鍚屾鐩戝惉
  if (leftScrollRef.value && rightScrollRef.value) {
    leftScrollRef.value.addEventListener('scroll', handleLeftScroll)
    rightScrollRef.value.addEventListener('scroll', handleRightScroll)
  }
})

// onUnmounted(() => {
//   socket.disconnect()
//   [waveChart, footChart, radarChart, pieChart].forEach(ch => ch && ch.dispose())
//   // 绉婚櫎婊氬姩鐩戝惉
//   if (leftScrollRef.value) leftScrollRef.value.removeEventListener('scroll', handleLeftScroll)
//   if (rightScrollRef.value) rightScrollRef.value.removeEventListener('scroll', handleRightScroll)

//     // ---------- 鑷姩婊氬姩娓呯悊 ----------
//   stopAutoScroll()
//   if (pauseTimeout) clearTimeout(pauseTimeout)
// })

onUnmounted(async () => {
  // 娓呯悊 Socket.IO 杩炴帴
  disconnectSocket()
  
  // 娓呯悊涓插彛杩炴帴
  await disconnectSerial()
  
  // 娓呯悊鍥捐〃
  [waveChart, footChart, radarChart, pieChart].forEach(ch => ch && ch.dispose())
  
  // 绉婚櫎婊氬姩鐩戝惉
  if (leftScrollRef.value) leftScrollRef.value.removeEventListener('scroll', handleLeftScroll)
  if (rightScrollRef.value) rightScrollRef.value.removeEventListener('scroll', handleRightScroll)

  // 娓呯悊鍚庣璁剧疆鍒锋柊浜嬩欢
  window.removeEventListener('backend-settings-updated', loadBackendSettings)

  // 娓呯悊鑷姩婊氬姩
  stopAutoScroll()
  if (pauseTimeout) clearTimeout(pauseTimeout)
})

// 銆愪慨鏀圭偣2銆戦€€鍑虹櫥褰?- 涓诲姩娓呯悊璧勬簮鍚庤烦杞紝閬垮厤鐘舵€佹畫鐣?
const logout = () => {
  // 娓呯悊瀹氭椂鍣?
  if (autoScrollTimer) {
    clearInterval(autoScrollTimer);
    autoScrollTimer = null;
  }
  if (pauseTimeout) {
    clearTimeout(pauseTimeout);
    pauseTimeout = null;
  }

  // 閿€姣佸浘琛ㄥ疄渚?
  [waveChart, footChart, radarChart, pieChart].forEach(ch => {
    if (ch && ch.dispose) ch.dispose();
  });
  
  // 浣跨敤 replace 璺宠浆鐧诲綍椤?
  router.replace('/').catch(err => {
    console.error("閫€鍑虹櫥褰曡烦杞け璐?", err);
    window.location.href = '/';
  });
}
</script>

<style scoped>
/* 姝ゅ瀹屾暣淇濈暀鎮ㄥ師鏉ョ殑鏍峰紡锛屽洜绡囧箙闄愬埗涓嶅啀閲嶅锛岃纭繚澶嶅埗鍘?Dashboard.vue 鐨?style 鍐呭 */
/* 浠ヤ笅涓鸿ˉ鍏呯殑蹇呰鏍峰紡锛堝鏋滃師鏍峰紡涓凡瀛樺湪鍙拷鐣ワ級 */
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
/* 鑷姩婊氬姩寮€鍏虫牱寮?*/
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

