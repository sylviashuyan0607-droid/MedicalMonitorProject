#!/usr/bin/env python3
# -*- coding: utf-8 -*-

filepath = 'frontend/src/views/Dashboard.vue'

with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 修复具体行的问题
# 查找并修复所有未闭合的字符串
fixed_lines = []
for i, line in enumerate(lines, 1):
    # 修复 Socket.IO 相关的字符串
    if i == 467 and "postureStatus.value = '✅ 已通过 Socket.IO 连接到后端" in line:
        line = "    postureStatus.value = '✅ 已通过 Socket.IO 连接到后端'\n"
    elif i == 470 and "addAlertMessage('已通过 Socket.IO 连接后端" in line:
        line = "    addAlertMessage('已通过 Socket.IO 连接后端', 'info')\n"
    elif i == 477 and "postureStatus.value = '✅ 系统已就绪" in line:
        line = "    postureStatus.value = '✅ 系统已就绪，接收数据中...'\n"
    elif i == 487 and "addAlertMessage('✅ Socket.IO 已连接" in line:
        line = "    addAlertMessage('✅ Socket.IO 已连接', 'info')\n"
    elif i == 488 and "postureStatus.value = '✅ 系统已就绪" in line:
        line = "    postureStatus.value = '✅ 系统已就绪，接收数据中...'\n"
    elif i == 522 and "postureStatus.value = '❌ 连接失败" in line:
        line = "    postureStatus.value = '❌ 连接失败，请检查后端程序'\n"
    
    fixed_lines.append(line)

with open(filepath, 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print('✅ 已修复字符串引号问题')
