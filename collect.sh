#!/bin/bash
# collect.sh - 模拟传感器采集器
count=${1:-5}
log=~/iot-lab/logs/collect.log
mkdir -p ~/iot-lab/logs
echo "开始采集 $count 次..."
for i in $(seq 1 "$count"); do
  temp=$((20 + RANDOM % 15))
  hum=$((40 + RANDOM % 40))
  echo "$(date '+%F %T') 采集#$i temp=$temp hum=$hum" >> "$log"
  sleep 1
done
echo "完成! 共 $(wc -l < "$log") 条记录"
tail -3 "$log"
