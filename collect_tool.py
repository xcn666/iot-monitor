#!/usr/bin/env python3
# collect_tool.py - 阶段验收: 定时采集 + 存日志 + 统计 + 报告
import sys
import time
import json
import csv
import os
from datetime import datetime
import sensor_lib

# ---- 读命令行参数, 带默认值 ----
count = int(sys.argv[1]) if len(sys.argv) > 1 else 5
interval = float(sys.argv[2]) if len(sys.argv) > 2 else 1

BASE = os.path.expanduser("~/iot-lab/logs")
os.makedirs(BASE, exist_ok=True)
LOG = os.path.join(BASE, "sensor_log.jsonl")
CSV_PATH = os.path.join(BASE, "sensor_report.csv")
REPORT = os.path.join(BASE, "report.txt")
THRESHOLD = 30

print(f"开始采集: {count} 次, 间隔 {interval} 秒")

# ---- 采集 + 实时告警 + 追加写日志 ----
with open(LOG, "a", encoding="utf-8") as f:
    for i in range(count):
        r = sensor_lib.make_record()
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
        f.flush()
        if r["temp"] > THRESHOLD:
            flag = "  >>> 超限告警!"
        else:
            flag = ""
        print(f"[{i+1}/{count}] {r['time']} temp={r['temp']}C hum={r['hum']}%{flag}")
        if i < count - 1:
            time.sleep(interval)

# ---- 读回来统计 ----
records = []
with open(LOG, "r", encoding="utf-8") as f:
    for line in f:
        records.append(json.loads(line))

temps = []
alerts = []
for r in records:
    temps.append(r["temp"])
    if r["temp"] > THRESHOLD:
        alerts.append(r)

avg = sensor_lib.average(temps)
mx = max(temps)

# ---- 生成文本报告 ----
with open(REPORT, "w", encoding="utf-8") as f:
    f.write("===== 传感器数据报告 =====\n")
    f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"总记录数: {len(records)}\n")
    f.write(f"平均温度: {avg:.2f}C\n")
    f.write(f"最高温度: {mx}C\n")
    f.write(f"告警次数: {len(alerts)}\n")
    for r in alerts:
        f.write(f"  告警: {r['time']} temp={r['temp']}C hum={r['hum']}%\n")
    if avg > 30:
        f.write("整体评价:偏高\n")
    else:
        f.write("整体评价:正常\n")

print()
print(f"统计: 共 {len(records)} 条, 平均 {avg:.2f}C, 最高 {mx}C, 告警 {len(alerts)} 次")
print("报告:", REPORT)

# ---- 导出 CSV ----
with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["time", "temp", "hum"])
    for r in records:
        w.writerow([r["time"], r["temp"], r["hum"]])
print("CSV:", CSV_PATH)
