#!/usr/bin/env python3
# sensor_v3.py - 列表与字典: 多条传感器记录
import json

records = [
    {"time": "12:00:01", "temp": 30.0, "hum": 60},
    {"time": "12:00:02", "temp": 27.1, "hum": 58},
    {"time": "12:00:03", "temp": 25.8, "hum": 62},
]

print("全部记录:", records)
print("第1条的温度:", records[0]["temp"])
print("最后1条:", records[-1])
print("记录条数:", len(records))

avg = (records[0]["temp"] + records[1]["temp"] + records[2]["temp"]) / len(records)
print(f"平均温度: {avg:.2f}C")

text = json.dumps(records, ensure_ascii=False)
print("JSON 格式:", text)
