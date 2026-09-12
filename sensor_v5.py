#!/usr/bin/env python3
# sensor_v5.py - 使用自己的模块 sensor_lib
import sensor_lib

records = []
for i in range(5):
    records.append(sensor_lib.make_record())

temps = []
alerts = 0
for r in records:
    print(f"{r['time']} temp={r['temp']}C hum={r['hum']}%")
    temps.append(r["temp"])
    if sensor_lib.is_alert(r["temp"]):
        alerts = alerts + 1
        print("  >>> 温度超限告警!")

print()
print(f"共 {len(records)} 条, 平均温度 {sensor_lib.average(temps):.2f}C, 告警 {alerts} 次")
