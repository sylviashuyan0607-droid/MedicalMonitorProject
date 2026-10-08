#!/usr/bin/env python3
# -*- coding: utf-8 -*-

filepath = 'frontend/src/views/Dashboard.vue'

with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 修复具体行的问题
fixed_lines = []
for i, line in enumerate(lines, 1):
    # 修复 connectSerial 中的字符串
    if "console.log('✅ 串口已连接')" in line or "console.log('✅ 串口已连接" in line:
        line = "    console.log('✅ 串口已连接')\n"
    elif "postureStatus.value = '✅ 串口已连接" in line:
        line = "    postureStatus.value = '✅ 串口已连接，正在读取数据...'\n"
    elif "addAlertMessage('串口已连接'" in line:
        line = "    addAlertMessage('串口已连接', 'info')\n"
    elif "postureStatus.value = '请录入压力标准值'" in line:
        line = "      postureStatus.value = '请录入压力标准值'\n"
    elif "alert('请录入压力标准值" in line:
        line = "      alert('请录入压力标准值：点击\"录入当前姿态为标准\"')\n"
    elif "addAlertMessage('请录入压力标准值'" in line:
        line = "      addAlertMessage('请录入压力标准值', 'warning')\n"
    elif "console.error('❌ 串口连接失败'," in line:
        line = "    console.error('❌ 串口连接失败:', error)\n"
    elif "postureStatus.value = '❌ 串口连接失败：'" in line:
        line = "    postureStatus.value = '❌ 串口连接失败：' + (error.message || error)\n"
    elif "addAlertMessage('串口连接失败:" in line:
        line = "    addAlertMessage('串口连接失败: ' + (error.message || error), 'error')\n"
    elif "console.error('❌ 读取串口数据出错'," in line:
        line = "    console.error('❌ 读取串口数据出错:', error)\n"
    elif "postureStatus.value = '❌ 串口读取中断：'" in line:
        line = "    postureStatus.value = '❌ 串口读取中断：' + (error.message || error)\n"
    elif "addAlertMessage('串口读取出错:" in line:
        line = "    addAlertMessage('串口读取出错: ' + (error.message || error), 'error')\n"
    elif "const alertHistory = ref([{ time: '系统'" in line and "传感器通信已就绪'" in line:
        line = "const alertHistory = ref([{ time: '系统', msg: '传感器通信已就绪', type: 'info' }])\n"
    
    fixed_lines.append(line)

with open(filepath, 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print('✅ 已修复 connectSerial 及其他字符串问题')
