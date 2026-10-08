import serial
import numpy as np

class SensorReader:
    def __init__(self, port="COM6", baudrate=115200, timeout=1):
        self.is_simulated = (port is None)
        if not self.is_simulated:
            try:
                self.ser = serial.Serial(port, baudrate, timeout=timeout)
                print(f"成功连接到硬件端口: {port}")
            except Exception as e:
                print(f"连接失败: {e}，自动切换至模拟模式。")
                self.is_simulated = True

    def read_data(self):
        if self.is_simulated:
            return np.random.uniform(10, 50, size=4)
        
        try:
            line = self.ser.readline().decode('utf-8').strip()
            if line:
                # 解析字符串 "val1,val2,val3,val4"
                data = [float(val) for val in line.split(',')]
                return np.array(data)
        except:
            pass
        return np.zeros(4)