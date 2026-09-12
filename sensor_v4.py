#!/usr/bin/env python3
# sensor_v4.py - 条件与循环: 批量采集并告警
import random
from datetime import datetime

records = []

# 循环采集 5 条
for i in range(5):
    record = {
        "time": datetime.now().strftime("%H:%M:%S"),
        "temp": round(random.uniform(20, 35), 1),
        "hum": random.randint(40, 80),
    }
    records.append(record)

# 遍历 + 判断 + 统计
total = 0
alerts = 0
for r in records:
    print(f"{r['time']} temp={r['temp']}C hum={r['hum']}%")
    total = total + r["temp"]
    if r["temp"] > 26:
        alerts = alerts + 1
        print("  >>> 温度超限告警!")

avg = total / len(records)
print()
print(f"共 {len(records)} 条, 平均温度 {avg:.2f}C, 告警 {alerts} 次")
