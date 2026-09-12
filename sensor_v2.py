#!/usr/bin/env python3
# sensor_v2.py - 数据类型与类型转换练习
import random

# 模拟: 传感器通过串口读回来的原始数据是"字符串"
raw_temp = f"{random.uniform(20, 35):.1f}"
raw_hum = str(random.randint(40, 80))

print("原始数据(字符串):", raw_temp, raw_hum)
print("类型:", type(raw_temp), type(raw_hum))

# 字符串 → 数字
temp = float(raw_temp)
hum = int(raw_hum)

# 摄氏 → 华氏: F = C * 9 / 5 + 32
fahrenheit = temp * 9 / 5 + 32

print(f"温度 {temp:.1f}C = {fahrenheit:.1f}F, 湿度 {hum}%")
print("类型:", type(temp), type(hum))
