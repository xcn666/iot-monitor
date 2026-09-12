#!/usr/bin/env python3
# dashboard.py - 网页实时显示 MQTT 传感器数据
import json
import threading
from collections import deque
from flask import Flask, jsonify, render_template_string
import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883
TOPIC = "iot/xcn666/#"
MAX_POINTS = 60

app = Flask(__name__)
points = deque(maxlen=MAX_POINTS)     # 只保留最近30条
lock = threading.Lock()

def on_connect(client, userdata, flags, rc):
    print("已连接 broker, 订阅", TOPIC, flush=True)
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    try:
        d = json.loads(msg.payload.decode("utf-8"))
    except json.JSONDecodeError:
        return
    with lock:
        points.append({"time": d.get("time", ""), "temp": d.get("temp"), "hum": d.get("hum")})
    print("收到:", d, flush=True)

mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(BROKER, PORT)
mqtt_client.loop_start()

PAGE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>物联网温湿度监测</title>
<script src="https://cdn.bootcdn.net/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
  body { font-family: "Microsoft YaHei", sans-serif; background:#0f172a; color:#e2e8f0; margin:0; padding:24px; }
  h1 { font-size:22px; margin:0 0 18px; }
  .cards { display:flex; gap:16px; margin-bottom:20px; }
  .card { background:#1e293b; border-radius:12px; padding:16px 22px; min-width:150px; }
  .card .label { font-size:13px; color:#94a3b8; }
  .card .value { font-size:30px; font-weight:bold; margin-top:6px; }
  #temp { color:#f87171; } #hum { color:#60a5fa; }
  .box { background:#1e293b; border-radius:12px; padding:16px; }
</style>
</head>
<body>
<h1>物联网温湿度监测大屏</h1>
<div class="cards">
  <div class="card"><div class="label">当前温度</div><div class="value"><span id="temp">--</span> C</div></div>
  <div class="card"><div class="label">当前湿度</div><div class="value"><span id="hum">--</span> %</div></div>
  <div class="card"><div class="label">数据点数</div><div class="value" id="count">0</div></div>
</div>
<div class="box"><canvas id="chart" height="90"></canvas></div>
<script>
const chart = new Chart(document.getElementById('chart'), {
  type: 'line',
  data: { labels: [], datasets: [
    { label: '温度 (C)', data: [], borderColor: '#f87171', backgroundColor:'rgba(248,113,113,0.15)', fill:true, tension: 0.3 },
    { label: '湿度 (%)', data: [], borderColor: '#60a5fa', backgroundColor:'rgba(96,165,250,0.15)', fill:true, tension: 0.3 }
  ]},
  options: { responsive:true, animation:false, plugins:{legend:{labels:{color:'#e2e8f0'}}},
    scales:{ x:{ticks:{color:'#94a3b8'}}, y:{ticks:{color:'#94a3b8'}} } }
});
async function refresh() {
  const res = await fetch('/api/data');
  const data = await res.json();
  chart.data.labels = data.map(d => d.time);
  chart.data.datasets[0].data = data.map(d => d.temp);
  chart.data.datasets[1].data = data.map(d => d.hum);
  chart.update();
  if (data.length) {
    document.getElementById('temp').textContent = data[data.length-1].temp;
    document.getElementById('hum').textContent = data[data.length-1].hum;
  }
  document.getElementById('count').textContent = data.length;
}
setInterval(refresh, 2000);
refresh();
</script>
</body>
</html>"""

@app.route("/")
def index():
    return render_template_string(PAGE)

@app.route("/api/data")
def api_data():
    with lock:
        return jsonify(list(points))

if __name__ == "__main__":
    print("大屏已启动: http://localhost:5000", flush=True)
    app.run(host="0.0.0.0", port=5000, debug=False)
