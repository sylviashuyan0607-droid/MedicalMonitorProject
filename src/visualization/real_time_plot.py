import matplotlib.pyplot as plt

class RealTimePlotter:
    def __init__(self, sensor_configs):
        plt.ion()
        self.fig, self.ax = plt.subplots(figsize=(5, 7))
        self.configs = sensor_configs
        
    def update(self, pressures, cop):
        self.ax.clear()
        self.ax.set_xlim(-6, 6)
        self.ax.set_ylim(-2, 14)
        self.ax.set_title("Medical Monitor - Real-time Foot Pressure")

        # 绘制传感器点
        for i, conf in enumerate(self.configs):
            size = pressures[i] * 20 # 压力越大圆圈越大
            self.ax.scatter(conf['x'], conf['y'], s=size, alpha=0.5, color='blue')
            self.ax.text(conf['x'], conf['y'], conf['name'])

        # 绘制重心点
        self.ax.scatter(cop[0], cop[1], color='red', marker='X', s=200, label='CoP')
        self.ax.legend()
        plt.pause(0.01)