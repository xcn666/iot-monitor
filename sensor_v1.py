#!/usr/bin/env python3
# sensor_v1.py - 第一个 Python 传感器模拟器
import random
from datetime import datetime

temp = round(random.uniform(20, 35), 1)
hum = random.randint(40, 80)
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

print(f"{now} temp={temp}C hum={hum}%")
