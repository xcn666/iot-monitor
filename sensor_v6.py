#!/usr/bin/env python3
# sensor_v6.py - 数据持久化: 写日志 -> 读回来 -> 统计 -> 导出CSV
import json
import csv
import os
import sensor_lib

LOG = os.path.expanduser("~/iot-lab/logs/sensor_log.jsonl")
CSV_PATH = os.path.expanduser("~/iot-lab/logs/sensor_report.csv")
os.makedirs(os.path.dirname(LOG), exist_ok=True)

# 1) 采集 5 条, 追加写入 JSON Lines
with open(LOG, "w", encoding="utf-8") as f:
    for i in range(5):
        r = sensor_lib.make_record()
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
print("已追加 5 条到", LOG)

# 2) 读回来
records = []
with open(LOG, "r", encoding="utf-8") as f:
    for line in f:
        records.append(json.loads(line))
print("文件里共", len(records), "条记录")

# 3) 统计
temps = []
alerts = 0
for r in records:
    temps.append(r["temp"])
    if sensor_lib.is_alert(r["temp"]):
        alerts += 1
print(f"平均温度 {sensor_lib.average(temps):.2f}C, 告警 {alerts} 次")

# 4) 导出 CSV
with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["time", "temp", "hum"])
    for r in records:
        w.writerow([r["time"], r["temp"], r["hum"]])
print("已导出 CSV:", CSV_PATH)
