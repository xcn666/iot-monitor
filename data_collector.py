#!/usr/bin/env python3
# data_collector.py - 订阅设备数据, 写入 SQLite 并告警
import json
import paho.mqtt.client as mqtt
import db

BROKER = "localhost"
PORT = 1883
TOPIC = "iot/xcn666/#"
THRESHOLD = 30

db.init_db()

def on_connect(client, userdata, flags, rc):
    print("已连接 broker, 订阅:", TOPIC, flush=True)
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode("utf-8"))
    except json.JSONDecodeError:
        return
    if "temp" not in data:
        return
    db.insert_reading(data.get("time", ""), data.get("temp"), data.get("hum", 0), data.get("device", ""))
    print(f"[入库] temp={data['temp']}C hum={data.get('hum')}%", flush=True)
    if data["temp"] > THRESHOLD:
        print(f"  >>> 告警! 温度 {data['temp']}C 超过 {THRESHOLD}C", flush=True)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER, PORT)
print("监听中... Ctrl+C 退出", flush=True)
client.loop_forever()
