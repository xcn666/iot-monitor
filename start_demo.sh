#!/bin/bash
# start_demo.sh - 一键启动完整演示: broker + 大屏 + 设备模拟上报
cd ~/iot-lab
./start_broker.sh

# 关掉旧的大屏进程(如果还在)
pkill -f "python3 dashboard.py" 2>/dev/null
sleep 0.5

nohup python3 dashboard.py > /tmp/dashboard.log 2>&1 &
sleep 2
echo "大屏地址: http://localhost:5000  (请在浏览器打开)"

# 后台模拟设备上报 60 秒
python3 sensor_publisher.py 60 1 > /tmp/publisher.log 2>&1 &
echo "已在后台模拟设备上报(60秒), 打开浏览器即可看到曲线"
