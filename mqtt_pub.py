#!/usr/bin/env python3
# mqtt_pub.py - 用 Python 发布传感器数据到 MQTT
import json
import time
import random
from datetime import datetime
import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883
TOPIC = "iot/xcn666/sensor/room1"

client = mqtt.Client()           # 创建客户端
client.connect(BROKER, PORT)     # 连接 broker
client.loop_start()              # 启动后台网络循环

for i in range(5):
    data = {
        "device": "xcn666-esp32",
        "time": datetime.now().strftime("%H:%M:%S"),
        "temp": round(random.uniform(20, 35), 1),
        "hum": random.randint(40, 80),
    }
    text = json.dumps(data, ensure_ascii=False)
    client.publish(TOPIC, text)
    print("[发布]", TOPIC, text)
    time.sleep(1)

client.loop_stop()
client.disconnect()
print("发布完成")
