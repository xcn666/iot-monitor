# 物联网温湿度监测系统

一个**端到端**的物联网数据采集与可视化项目：模拟传感器采集 → MQTT 上报 → 服务端处理入库 → 网页实时展示与告警。

![大屏效果](docs/dashboard.png)

## ✨ 功能特性

- **数据采集**：定时采集温湿度数据，支持命令行参数配置采集次数与间隔
- **MQTT 通信**：设备端发布 JSON 数据到主题，服务端订阅处理（发布/订阅解耦）
- **数据持久化**：存入 **SQLite 数据库**（`readings` 表），支持高效查询与统计
- **历史查询与统计**：提供 `/api/history`、`/api/stats` 接口（平均值/最高/最低/总数）
- **实时可视化**：Flask + Chart.js 网页大屏，实时曲线 + 数字卡片 + 历史趋势
- **告警系统**：超阈值自动告警，写入 `alerts` 表；**告警抑制**（冷却时间）防止告警风暴
- **断线重连**：MQTT 客户端自动重连，采用**退避策略**（1s→10s）避免雪崩
- **离线缓存补发**：断网期间数据先存本地队列，网络恢复后自动补发，**不丢数据**

## 🏗️ 系统架构

```
┌──────────────┐   发布    ┌────────────┐   订阅    ┌────────────────────┐
│ 设备端        │ ───────> │  MQTT      │ ───────> │  服务端             │
│ sensor_      │          │  Broker    │          │  data_collector.py │
│ publisher.py │          │ (mosquitto)│          │  dashboard.py      │
│ (离线缓存)    │          └────────────┘          └─────────┬──────────┘
└──────────────┘                                            │
                                                   ┌────────▼────────┐
                                                   │  SQLite 数据库    │
                                                   │ readings/alerts │
                                                   └────────┬────────┘
                                                            │
                                                   ┌────────▼────────┐
                                                   │ 网页大屏 (Flask)  │
                                                   │ 实时曲线/统计/告警 │
                                                   └─────────────────┘
```

## 🛠️ 技术栈

| 类别 | 技术 |
|------|------|
| 语言 | Python 3.10 |
| 通信协议 | MQTT (paho-mqtt)、HTTP |
| 消息中间件 | Mosquitto Broker |
| 数据存储 | SQLite3（嵌入式数据库） |
| Web 框架 | Flask |
| 前端图表 | Chart.js |
| 数据格式 | JSON / JSON Lines / CSV |
| 开发环境 | WSL2 + Ubuntu 22.04、Linux 命令行、Git |

## 📁 目录结构

```
iot-lab/
├── sensor_lib.py          # 传感器数据模块(采集/判断/统计)
├── db.py                  # SQLite 存储模块(readings/alerts 表)
├── sensor_publisher.py    # 设备端: 采集+发布(含离线缓存补发)
├── data_collector.py      # 服务端: 订阅+入库+告警
├── dashboard.py           # 网页大屏(Flask + MQTT + SQLite)
├── query_db.py            # 命令行 SQL 查询工具(练习/排障)
├── collect_tool.py        # 命令行采集工具(定时采集+报告)
├── start_broker.sh        # 一键启动 MQTT Broker
├── start_demo.sh          # 一键启动完整演示
├── docs/dashboard.png     # 大屏效果截图
└── README.md
```

## 🚀 运行方法

```bash
# 1. 启动 MQTT Broker
~/iot-lab/start_broker.sh

# 2. 启动网页大屏(后台)
cd ~/iot-lab
nohup python3 dashboard.py > /tmp/dashboard.log 2>&1 &

# 3. 浏览器打开 http://localhost:5000

# 4. 模拟设备上报数据(次数 间隔秒)
python3 sensor_publisher.py 30 1

# 5. 服务端订阅入库(可选, 与大屏二选一或并存)
python3 data_collector.py
```

## 🔍 运维/排障

```bash
# 查询数据库统计
python3 query_db.py

# 查询温度最高的 3 条
python3 query_db.py "SELECT time, temp FROM readings ORDER BY temp DESC LIMIT 3"

# 查询告警记录
python3 query_db.py "SELECT * FROM alerts ORDER BY id DESC LIMIT 5"

# 查看大屏日志(含断线重连记录)
tail -f /tmp/dashboard.log
```

## 💡 关键技术点（面试可展开）

1. **发布/订阅解耦**：设备端与服务端互不感知，只依赖 Broker 与主题
2. **主题设计**：`iot/xcn666/#` 通配符订阅 vs 精确订阅的取舍
3. **告警抑制**：冷却时间避免告警风暴；**数据不丢，仅告警去重**
4. **退避重连**：1s→10s 指数退避，避免海量设备同时重连打垮服务端
5. **离线补传**：断网写入本地队列，恢复后先补发再采新，保证数据完整与时序
6. **存储分层**：JSON Lines 便于追加日志，SQLite 便于查询统计

## 🔭 后续计划

- [ ] 接入真实硬件（ESP32 + DHT22 温湿度传感器 + OLED 显示）
- [ ] 数据接入云平台（阿里云 IoT / EMQX Cloud）
- [ ] 告警推送（微信/钉钉/邮件通知）

## 👤 作者

xcn666 · 2026
