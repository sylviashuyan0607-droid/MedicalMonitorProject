const socket = io();

// 添加这一行：
socket.on(
'connect', () => { console.log("✅ 成功连接到后端服务器！"); });

socket.on('update_data', function(data) {
    // 1. 更新状态警报
    const alertBox = document.getElementById('alert-box');
    alertBox.innerText = data.status;
    if (data.status.includes("警告") || data.status.includes("异常")) {
        alertBox.className = "warning";
    } else {
        alertBox.className = "normal";
    }

    // 2. 更新 4 个传感器的圆圈大小 (根据压力值同步)
    data.pressures.forEach((val, i) => {
        const dot = document.getElementById(`sensor-${i}`);
        // 这里的 1.5 是缩放系数，你可以根据实际灵敏度调整
        const size = Math.max(40, val * 1.5); 
        dot.style.width = size + "px";
        dot.style.height = size + "px";
    });

    // 3. 更新重心 (CoP) 位置
    const copMarker = document.getElementById('cop-marker');
    // 映射坐标：X 范围约 -6到6，网页宽度 260px
    const posX = 130 + (data.cop[0] * 20); 
    const posY = 400 - (data.cop[1] * 30);
    copMarker.style.left = posX + "px";
    copMarker.style.top = posY + "px";

    // 4. 更新面板数值显示
    document.getElementById('val-cop').innerText = data.cop[0].toFixed(2);
    const totalP = data.pressures.reduce((a, b) => a + b, 0);
    document.getElementById('val-total').innerText = Math.round(totalP);
});