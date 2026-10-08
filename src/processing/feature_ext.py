def calculate_cop(pressures, sensor_configs):
    """
    根据公式 CoP = sum(P_i * pos_i) / sum(P_i) 计算
    """
    total_p = sum(pressures)
    if total_p == 0:
        return 0, 0
    
    cop_x = sum(p * conf['x'] for p, conf in zip(pressures, sensor_configs)) / total_p
    cop_y = sum(p * conf['y'] for p, conf in zip(pressures, sensor_configs)) / total_p
    
    return cop_x, cop_y