#!/usr/bin/env python3
# data_collector.py - 订阅设备数据, 存日志并告警 (服务器端)
import json
import os
import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883
TOPIC = "iot/xcn666/#"
THRESHOLD = 26
LOG = os.path.expanduser("~/iot-lab/logs/mqtt_data.jsonl")

def on_connect(client, userdata, flags, rc):
    print("已连接 broker, 订阅:", TOPIC, flush=True)
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    text = msg.payload.decode("utf-8")
    print("[收到]", text, flush=True)
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(text + "\n")
    if data.get("temp", 0) > THRESHOLD:
        print(f"  >>> 告警! 温度 {data['temp']}C 超过 {THRESHOLD}C", flush=True)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER, PORT)
print("监听中... Ctrl+C 退出", flush=True)
client.loop_forever()
