#!/usr/bin/env python3
# dashboard.py - 网页实时监测大屏(SQLite + 告警)
import csv as csv_mod
import io
import json
import threading
import time
from flask import Flask, Response, jsonify, render_template_string, request
import paho.mqtt.client as mqtt
import db
import notify

BROKER = "localhost"
PORT = 1883
TOPIC = "iot/xcn666/#"
THRESHOLD = 30
ALERT_COOLDOWN = 10      # 同一设备 10 秒内只记一次告警(防刷屏)

app = Flask(__name__)
lock = threading.Lock()
last_alert = {}          # device -> 上次告警时间戳
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

    temp = d["temp"]
    device = d.get("device", "unknown")
    now = time.time()

    with lock:
        db.insert_reading(d.get("time", ""), temp, d.get("hum", 0), device)

        # 超限判断 + 告警抑制(冷却时间)
        if temp > THRESHOLD:
            last = last_alert.get(device, 0)
            if now - last >= ALERT_COOLDOWN:
                last_alert[device] = now
                db.insert_alert(d.get("time", ""), temp, THRESHOLD, device)
                msg = f"[告警] {device} 温度 {temp}C 超过阈值 {THRESHOLD}C (时间 {d.get('time', '')})"
                print(msg, flush=True)
                notify.push_alert(msg)
            else:
                print(f"[抑制] {device} 温度 {temp}C 超限, 但处于冷却期(不重复记录)", flush=True)

    print("已入库:", d, flush=True)

mqtt_client = mqtt.Client()
mqtt_client.reconnect_delay_set(min_delay=1, max_delay=10)

def on_disconnect(c, userdata, rc):
    print(f"[断线] 与 broker 断开(rc={rc}), 等待自动重连...", flush=True)

mqtt_client.on_disconnect = on_disconnect
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
  h1 { font-size:22px; margin:0 0 14px; }
  .cards { display:flex; gap:14px; margin-bottom:12px; flex-wrap:wrap; }
  .card { background:#1e293b; border-radius:12px; padding:12px 20px; min-width:135px; }
  .card .label { font-size:13px; color:#94a3b8; }
  .card .value { font-size:26px; font-weight:bold; margin-top:5px; }
  .red { color:#f87171; } .blue { color:#60a5fa; } .green { color:#4ade80; }
  .yellow { color:#fbbf24; } .alert { color:#f87171; }
  .grid { display:grid; grid-template-columns: 2fr 1fr; gap:14px; }
  .box { background:#1e293b; border-radius:12px; padding:16px; }
  .box h3 { font-size:14px; color:#94a3b8; margin:0 0 10px; }
  .alert-item { padding:8px 10px; margin-bottom:6px; border-radius:8px; background:#450a0a; border-left:4px solid #ef4444; font-size:13px; }
  .empty { color:#64748b; font-size:13px; }
  .btn { background:#2563eb; color:#fff; padding:8px 16px; border-radius:8px;
         text-decoration:none; font-size:14px; }
  .btn:hover { background:#1d4ed8; }
  #tempCard.warn { outline:2px solid #ef4444; }
</style>
</head>
<body>
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
  <h1 style="margin:0;">物联网温湿度监测大屏</h1>
  <a class="btn" href="/api/export">下载 CSV 数据</a>
</div>
<div class="cards">
  <div class="card" id="tempCard"><div class="label">当前温度</div><div class="value red"><span id="temp">--</span> C</div></div>
  <div class="card"><div class="label">当前湿度</div><div class="value blue"><span id="hum">--</span> %</div></div>
  <div class="card"><div class="label">总记录数</div><div class="value"><span id="count">0</span></div></div>
  <div class="card"><div class="label">告警次数</div><div class="value alert"><span id="alerts">0</span></div></div>
</div>
<div class="cards">
  <div class="card"><div class="label">平均温度</div><div class="value green"><span id="avg">--</span> C</div></div>
  <div class="card"><div class="label">最高温度</div><div class="value red"><span id="max">--</span> C</div></div>
  <div class="card"><div class="label">最低温度</div><div class="value blue"><span id="min">--</span> C</div></div>
  <div class="card"><div class="label">平均湿度</div><div class="value yellow"><span id="avghum">--</span> %</div></div>
</div>
<div class="grid">
  <div class="box"><canvas id="chart" height="80"></canvas></div>
  <div class="box">
    <h3>最近告警</h3>
    <div id="alertList"><div class="empty">暂无告警</div></div>
  </div>
</div>
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
  const [histRes, statRes, alertRes] = await Promise.all([
    fetch('/api/history?limit=60'), fetch('/api/stats'), fetch('/api/alerts?limit=5')
  ]);
  const history = await histRes.json();
  const s = await statRes.json();
  const alerts = await alertRes.json();

  chart.data.labels = history.map(d => d.time);
  chart.data.datasets[0].data = history.map(d => d.temp);
  chart.data.datasets[1].data = history.map(d => d.hum);
  chart.update();

  const tempCard = document.getElementById('tempCard');
  if (history.length) {
    const last = history[history.length-1];
    document.getElementById('temp').textContent = last.temp;
    document.getElementById('hum').textContent = last.hum;
    tempCard.classList.toggle('warn', last.temp > 30);
  }
  document.getElementById('count').textContent = s.count;
  document.getElementById('alerts').textContent = s.alert_count;
  document.getElementById('avg').textContent = s.avg_temp === null ? '--' : s.avg_temp;
  document.getElementById('max').textContent = s.max_temp === null ? '--' : s.max_temp;
  document.getElementById('min').textContent = s.min_temp === null ? '--' : s.min_temp;
  document.getElementById('avghum').textContent = s.avg_hum === null ? '--' : s.avg_hum;

  const box = document.getElementById('alertList');
  if (!alerts.length) { box.innerHTML = '<div class="empty">暂无告警</div>'; }
  else {
    box.innerHTML = alerts.map(a =>
      `<div class="alert-item">${a.time} &nbsp; 温度 <b>${a.temp}C</b> 超过阈值 ${a.threshold}C</div>`
    ).join('');
  }
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
    return jsonify(db.recent(request.args.get("limit", 60, type=int)))

@app.route("/api/stats")
def api_stats():
    return jsonify(db.stats())

@app.route("/api/alerts")
def api_alerts():
    return jsonify(db.recent_alerts(request.args.get("limit", 10, type=int)))

@app.route("/api/export")
def api_export():
    """把全部数据导出为 CSV 文件下载"""
    rows = db.all_rows()
    buf = io.StringIO()
    w = csv_mod.writer(buf)
    w.writerow(["time", "temp", "hum", "device"])
    for r in rows:
        w.writerow([r["time"], r["temp"], r["hum"], r["device"]])
    return Response(buf.getvalue(), mimetype="text/csv; charset=utf-8",
                    headers={"Content-Disposition": "attachment; filename=readings.csv"})

if __name__ == "__main__":
    print("大屏已启动: http://localhost:5000", flush=True)
    app.run(host="0.0.0.0", port=5000, debug=False)
