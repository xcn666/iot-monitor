#!/usr/bin/env python3
# sensor_publisher.py - 采集传感器数据并发布到 MQTT (设备端模拟)
import json
import time
import sys
import paho.mqtt.client as mqtt
import sensor_lib

BROKER = "localhost"
PORT = 1883
TOPIC = "iot/xcn666/sensor"

count = int(sys.argv[1]) if len(sys.argv) > 1 else 5
interval = float(sys.argv[2]) if len(sys.argv) > 2 else 1

client = mqtt.Client()
client.connect(BROKER, PORT)
client.loop_start()

print(f"开始采集并发布 {count} 次, 间隔 {interval} 秒", flush=True)
for i in range(count):
    r = sensor_lib.make_record()
    r["device"] = "xcn666-sim"
    text = json.dumps(r, ensure_ascii=False)
    client.publish(TOPIC, text)
    print("[发布]", text, flush=True)
    if i < count - 1:
        time.sleep(interval)

client.loop_stop()
client.disconnect()
print("发布完成", flush=True)
