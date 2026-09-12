#!/usr/bin/env python3
# mqtt_sub.py - 订阅 MQTT 消息并自动告警
import json
import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883
TOPIC = "iot/xcn666/#"
THRESHOLD = 26

def on_connect(client, userdata, flags, rc):
    """连接成功时自动调用"""
    print("已连接 broker, rc =", rc, flush=True)
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    """收到消息时自动调用"""
    text = msg.payload.decode("utf-8")
    print(f"[收到] {msg.topic}: {text}", flush=True)
    try:
        data = json.loads(text)
        if "temp" in data and data["temp"] > THRESHOLD:
            print("  >>> 温度超限告警!", flush=True)
    except json.JSONDecodeError:
        pass

client = mqtt.Client()
client.on_connect = on_connect      # 注册回调函数
client.on_message = on_message
client.connect(BROKER, PORT)
print("正在监听", TOPIC, "... (Ctrl+C 退出)", flush=True)
client.loop_forever()               # 一直循环等消息
