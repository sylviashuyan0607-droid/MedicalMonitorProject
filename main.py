import yaml
import time
from src.hardware.serial_reader import SensorReader
from src.processing.feature_ext import calculate_cop
from src.visualization.real_time_plot import RealTimePlotter
from src.analysis.posture_eval import PostureAnalyzer

def load_config():
    with open("config/settings.yaml", 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def main():
    config = load_config()
    # 确保这里的端口和你 Arduino 连上的一致
    reader = SensorReader(port="COM6") 
    plotter = RealTimePlotter(config['sensors'])
    analyzer = PostureAnalyzer(threshold_x=1.2)
    
    print("系统已启动，正在实时监测压力数据...")
    
    try:
        # 【关键】必须要有这个 while 循环，程序才不会退出
        while True:
            pressures = reader.read_data()
            cop = calculate_cop(pressures, config['sensors'])
            
            # 修改前：
            # posture_status = analyzer.check_posture(cop[0])

            # 修改后：
            posture_status = analyzer.check_posture(cop[0], pressures)
            
            # 更新绘图窗口
            plotter.update(pressures, cop)
            
            if "警告" in posture_status:
                print(f"\033[91m {posture_status} \033[0m")
                
    except KeyboardInterrupt:
        print("\n监测已手动停止。")

# 【关键】必须确保这两行在文件的最底部，且没有缩进
if __name__ == "__main__":
    main()