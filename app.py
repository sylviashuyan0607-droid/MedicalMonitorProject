from flask import Flask, request, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
import serial
import threading
import time
import collections

app = Flask(__name__)
CORS(app)
# 允许所有跨域请求以连接 Vue 前端
socketio = SocketIO(app, cors_allowed_origins="*")

# ---------- 系统配置 ----------
class SystemConfig:
    def __init__(self):
        # 基础算法参数
        self.pressure_threshold = 20.0  # 初始偏差阈值
        self.warning_time_limit = 600    # 报警时限
        self.pressure_ratio_threshold = 1.2
        self.cop_distance_threshold = 1.2
        
        # 定标参考值 (用户“坐正”时的状态)
        self.ref_total_load = 0.0
        self.ref_pressures = [0.0, 0.0, 0.0, 0.0]

config = SystemConfig()

# 串口配置：请确保与你的 Arduino 实际端口一致 (COM3 或 COM6)
SERIAL_PORT = 'COM6'           
BAUD_RATE = 115200
CALIB_FACTOR = 500.0 / 1023.0  # 单位转换因子

# ---------- 信号处理 (滤波与基准) ----------
baselines = [0.0, 0.0, 0.0, 0.0]
is_calibrated = False
calibration_counter = 0
CALIBRATION_SAMPLES = 50       # 硬件初始化采样数，适当减小以加快启动

filter_queues = [collections.deque(maxlen=10) for _ in range(4)] # 滑动窗口滤波

def process_signals(raw_vals):
    global baselines, is_calibrated, calibration_counter

    # # 1. 硬件归零阶段 (自动或手动触发)
    # if not is_calibrated:
    #     for i in range(4):
    #         baselines[i] += raw_vals[i]
    #     calibration_counter += 1

    #     if calibration_counter >= CALIBRATION_SAMPLES:
    #         baselines = [b / CALIBRATION_SAMPLES for b in baselines]
    #         is_calibrated = True
    #         print(f"✅ 硬件环境归零完成！基准值: {baselines}")
    #         for q in filter_queues:
    #             q.clear()
    #     return [0.0, 0.0, 0.0, 0.0]
    # 1. 硬件归零阶段
    if not is_calibrated:
        for i in range(4):
            # 增加安全性检查：过滤掉极端跳变的噪声值
            # 假设 AD 采样范围是 0-1023，如果值突然变成几万，说明解析出错了
            if 0 <= raw_vals[i] <= 1024:
                baselines[i] += raw_vals[i]
        
        calibration_counter += 1

        # 采样完成判定
        if calibration_counter >= CALIBRATION_SAMPLES:
            baselines = [b / CALIBRATION_SAMPLES for b in baselines]
            is_calibrated = True
            # 关键：归零完成后必须主动通知前端
            socketio.emit('calibration_done', {
                "status": "success",
                "baselines": baselines
            })
            print(f"✅ 归零完成: {baselines}")
        return [0.0, 0.0, 0.0, 0.0]

    # 2. 减去硬件基准并滤波
    calibrated_vals = [max(0, raw - base) for raw, base in zip(raw_vals, baselines)]
    
    filtered_vals = []
    for i in range(4):
        filter_queues[i].append(calibrated_vals[i])
        avg = sum(filter_queues[i]) / len(filter_queues[i])
        filtered_vals.append(avg)

    # 3. 转换物理单位 (克)
    DEADZONE = 1.0 # 死区阈值，去除微小抖动
    pressures = [v * CALIB_FACTOR for v in filtered_vals]
    pressures = [p if p > DEADZONE else 0.0 for p in pressures]
    return pressures

# ---------- 串口后台线程 ----------
def read_serial():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"✅ 串口 {SERIAL_PORT} 已成功打开")
    except Exception as e:
        print(f"❌ 无法打开串口 {SERIAL_PORT}. 请检查串口号是否被占用！ Error: {e}")
        return

    while True:
        try:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                # 兼容多种 CSV 格式，确保数据能切分
                parts = line.replace(' ', '').split(',')
                if len(parts) == 4:
                    try:
                        raw_vals = [float(p) for p in parts]
                        pressures = process_signals(raw_vals)
                        
                        if is_calibrated:
                            # 实时通过 WebSocket 推送到前端 Dashboard.vue
                            socketio.emit('sensorData', {
                                'pressures': pressures,
                                'timestamp': int(time.time() * 1000)
                            })
                    except ValueError:
                        pass
        except Exception as e:
            print(f"读取数据流出错: {e}")
        time.sleep(0.01) # 控制采样率约 100Hz

# 启动异步读取线程
threading.Thread(target=read_serial, daemon=True).start()

# ---------- 业务控制 API ----------

@app.route('/api/get_settings', methods=['GET'])
def get_settings():
    """获取当前算法配置"""
    return jsonify({
        "threshold": config.pressure_threshold,
        "timeLimit": config.warning_time_limit,
        "pressureRatioThreshold": config.pressure_ratio_threshold,
        "copDistanceThreshold": config.cop_distance_threshold,
        "refTotal": config.ref_total_load
    })

@app.route('/api/update_settings', methods=['POST'])
def update_settings():
    """更新阈值"""
    data = request.json
    if 'threshold' in data:
        config.pressure_threshold = float(data['threshold'])
    if 'timeLimit' in data:
        config.warning_time_limit = int(data['timeLimit'])
    if 'pressureRatioThreshold' in data:
        config.pressure_ratio_threshold = float(data['pressureRatioThreshold'])
    if 'copDistanceThreshold' in data:
        config.cop_distance_threshold = float(data['copDistanceThreshold'])
    return jsonify({"status": "success"})

@app.route('/api/reset_calibration', methods=['POST'])
def reset_calibration():
    """1. 触发硬件环境归零 (清除传感器零飘)"""
    global is_calibrated, calibration_counter, baselines
    baselines = [0.0, 0.0, 0.0, 0.0]
    calibration_counter = 0
    is_calibrated = False
    print("⚠️ 正在重新执行硬件基准归零...")
    return jsonify({"status": "success", "message": "环境归零已重置，请保持传感器空载"})

@app.route('/api/capture_reference', methods=['POST'])
def capture_reference():
    """2. 录入标准坐姿 (定标)"""
    data = request.json
    current_pressures = data.get('pressures', [0,0,0,0])
    total = sum(current_pressures)
    
    # 检查是否有有效负荷
    if total < 5:
        return jsonify({"status": "error", "message": "压力值过低，请入座后再录入"})
    
    config.ref_total_load = total
    config.ref_pressures = current_pressures
    print(f"🎯 标准姿态已保存: 总压力={total:.1f}g")
    
    return jsonify({
        "status": "success", 
        "ref_total": total,
        "message": "标准坐姿参考值录入成功"
    })

if __name__ == '__main__':
    # 禁用 debug 模式下的 reloader 避免串口被二次打开报错
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, use_reloader=False)