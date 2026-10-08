import time

class PostureAnalyzer:
    def __init__(self, threshold_x=1.5, delay_seconds=3, normal_pressure=200):
        # --- 倾斜监测参数 ---
        self.threshold_x = threshold_x    # 允许左右偏移的最大厘米数
        self.delay_limit = delay_seconds  # 只有偏移持续超过设定秒数才报警
        self.start_tilt_time = None       # 记录开始歪斜的时间点
        
        # --- 翘二郎腿监测参数 ---
        self.normal_limit = normal_pressure * 1.5 # 设定 1.5 倍为异常阈值

    def check_posture(self, cop_x, pressures):
        """
        输入：当前的压力中心 X 坐标，以及 4 通道的原始压力数组
        返回：状态信息列表
        """
        results = []
        
        # 1. 监测翘二郎腿 (基于总压力)
        total_p = sum(pressures)
        if total_p > self.normal_limit:
            results.append(f"【严重警告】检测到总压力({int(total_p)})远超正常值，疑似翘二郎腿！")
        
        # 2. 监测身体倾斜 (基于重心偏移)
        is_tilted = abs(cop_x) > self.threshold_x
        if is_tilted:
            if self.start_tilt_time is None:
                self.start_tilt_time = time.time()
                results.append("监测倾斜中...")
            else:
                duration = time.time() - self.start_tilt_time
                if duration > self.delay_limit:
                    direction = "左" if cop_x < 0 else "右"
                    results.append(f"【警告】向{direction}侧歪斜已持续 {int(duration)} 秒！")
        else:
            self.start_tilt_time = None

        # 如果没有任何异常
        if not results:
            return "坐姿良好"
        
        # 返回所有检测到的异常状态，用换行符连接
        return "\n".join(results)