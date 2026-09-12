#!/usr/bin/env python3
# dashboard.py - 网页实时显示 MQTT 传感器数据 (SQLite 版)
import json
import threading
from flask import Flask, jsonify, render_template_string, request
import paho.mqtt.client as mqtt
import db

BROKER = "localhost"
PORT = 1883
TOPIC = "iot/xcn666/#"
THRESHOLD = 30

app = Flask(__name__)
lock = threading.Lock()
db.init_db()

def on_connect(client, userdata, flags, rc):
    print("已连接 broker, 订阅", TOPIC, flush=True)
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    try:
        d = json.loads(msg.payload.decode("utf-8"))
    except json.JSONDecodeError:
        return
    if "temp" not in d:
        return
    with lock:
        db.insert_reading(d.get("time", ""), d.get("temp"), d.get("hum", 0), d.get("device", ""))
    print("已入库:", d, flush=True)

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
  .cards { display:flex; gap:16px; margin-bottom:14px; flex-wrap:wrap; }
  .card { background:#1e293b; border-radius:12px; padding:14px 22px; min-width:140px; }
  .card .label { font-size:13px; color:#94a3b8; }
  .card .value { font-size:28px; font-weight:bold; margin-top:6px; }
  .red { color:#f87171; } .blue { color:#60a5fa; } .green { color:#4ade80; } .yellow { color:#fbbf24; }
  .box { background:#1e293b; border-radius:12px; padding:16px; }
  .stats-title { font-size:13px; color:#94a3b8; margin:6px 0 10px; }
</style>
</head>
<body>
<h1>物联网温湿度监测大屏</h1>
<div class="cards">
  <div class="card"><div class="label">当前温度</div><div class="value red"><span id="temp">--</span> C</div></div>
  <div class="card"><div class="label">当前湿度</div><div class="value blue"><span id="hum">--</span> %</div></div>
  <div class="card"><div class="label">总记录数</div><div class="value"><span id="count">0</span></div></div>
</div>
<div class="stats-title">数据库统计</div>
<div class="cards">
  <div class="card"><div class="label">平均温度</div><div class="value green"><span id="avg">--</span> C</div></div>
  <div class="card"><div class="label">最高温度</div><div class="value red"><span id="max">--</span> C</div></div>
  <div class="card"><div class="label">最低温度</div><div class="value blue"><span id="min">--</span> C</div></div>
  <div class="card"><div class="label">平均湿度</div><div class="value yellow"><span id="avghum">--</span> %</div></div>
</div>
<div class="box"><canvas id="chart" height="80"></canvas></div>
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
  const [histRes, statRes] = await Promise.all([
    fetch('/api/history?limit=60'),
    fetch('/api/stats')
  ]);
  const history = await histRes.json();
  const s = await statRes.json();
  chart.data.labels = history.map(d => d.time);
  chart.data.datasets[0].data = history.map(d => d.temp);
  chart.data.datasets[1].data = history.map(d => d.hum);
  chart.update();
  if (history.length) {
    document.getElementById('temp').textContent = history[history.length-1].temp;
    document.getElementById('hum').textContent = history[history.length-1].hum;
  }
  document.getElementById('count').textContent = s.count;
  document.getElementById('avg').textContent = s.avg_temp === null ? '--' : s.avg_temp;
  document.getElementById('max').textContent = s.max_temp === null ? '--' : s.max_temp;
  document.getElementById('min').textContent = s.min_temp === null ? '--' : s.min_temp;
  document.getElementById('avghum').textContent = s.avg_hum === null ? '--' : s.avg_hum;
}
setInterval(refresh, 2000);
refresh();
</script>
</body>
</html>"""

@app.route("/")
def index():
    return render_template_string(PAGE)

@app.route("/api/history")
def api_history():
    limit = request.args.get("limit", 60, type=int)
    return jsonify(db.recent(limit))

@app.route("/api/stats")
def api_stats():
    return jsonify(db.stats())

if __name__ == "__main__":
    print("大屏已启动: http://localhost:5000", flush=True)
    app.run(host="0.0.0.0", port=5000, debug=False)
