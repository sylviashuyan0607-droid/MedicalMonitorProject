#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys

filepath = 'frontend/src/views/Dashboard.vue'

try:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 找到 connectSocket 函数的开始位置并替换
    start_marker = '// ---------- Web Serial API'
    end_marker = 'const connectSerial'

    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker, start_idx)

    if start_idx >= 0 and end_idx > start_idx:
        before = content[:start_idx]
        after_part = content[end_idx:]
        
        new_code = '''// ---------- Socket.IO连接相关函数 ----------

// Socket.IO 连接到后端
const connectSocket = () => {
  if (socket && socket.connected) {
    postureStatus.value = '✅ 已通过 Socket.IO 连接到后端'
    addAlertMessage('已通过 Socket.IO 连接后端', 'info')
    return
  }

  postureStatus.value = '正在连接后端服务器...'
  socket = io(backendApiUrl)

  socket.on('connect', () => {
    isReading.value = true
    addAlertMessage('✅ Socket.IO 已连接', 'info')
    postureStatus.value = '✅ 系统已就绪，接收数据中...'
  })

  socket.on('sensorData', (data) => {
    if (data && data.pressures && isCalibrated) {
      updateSensorData(data.pressures)
    }
  })

  socket.on('disconnect', () => {
    isReading.value = false
    postureStatus.value = '❌ 与后端连接断开'
    addAlertMessage('后端 Socket.IO 连接已断开', 'error')
  })

  socket.on('connect_error', () => {
    postureStatus.value = '❌ 连接失败，请检查后端程序'
  })
}

const disconnectSocket = () => {
  if (socket) {
    socket.disconnect()
    socket = null
    isReading.value = false
    postureStatus.value = '🔌 已断开连接'
  }
}

// 请求用户选择串口（现在主要使用 Socket.IO）


'''
        
        newContent = before + new_code + after_part
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(newContent)
        print('✅ connectSocket 函数已修复')
    else:
        print(f'❌ 未能找到要替换的代码块 (start={start_idx}, end={end_idx})')
        sys.exit(1)
except Exception as e:
    print(f'❌ 错误：{e}')
    sys.exit(1)
