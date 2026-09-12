#!/usr/bin/env python3
# db.py - SQLite 数据存储模块(数据 + 告警)
import os
import sqlite3
from datetime import datetime

DB_PATH = os.path.expanduser("~/iot-lab/logs/sensor.db")

def get_conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS readings (
            id     INTEGER PRIMARY KEY AUTOINCREMENT,
            day    TEXT,
            time   TEXT,
            temp   REAL,
            hum    INTEGER,
            device TEXT
        )
    """)
    # 数据库迁移: 老版本的表没有 day 列, 自动补上
    cols = [r[1] for r in conn.execute("PRAGMA table_info(readings)").fetchall()]
    if "day" not in cols:
        conn.execute("ALTER TABLE readings ADD COLUMN day TEXT")
        conn.execute("UPDATE readings SET day = ? WHERE day IS NULL",
                     (datetime.now().strftime("%Y-%m-%d"),))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            time      TEXT,
            temp      REAL,
            threshold REAL,
            device    TEXT
        )
    """)
    conn.commit()
    conn.close()

def insert_reading(time_str, temp, hum, device=""):
    conn = get_conn()
    conn.execute(
        "INSERT INTO readings (day, time, temp, hum, device) VALUES (?, ?, ?, ?, ?)",
        (datetime.now().strftime("%Y-%m-%d"), time_str, temp, hum, device),
    )
    conn.commit()
    conn.close()

def insert_alert(time_str, temp, threshold, device=""):
    conn = get_conn()
    conn.execute("INSERT INTO alerts (time, temp, threshold, device) VALUES (?, ?, ?, ?)",
                 (time_str, temp, threshold, device))
    conn.commit()
    conn.close()

def recent(limit=30):
    conn = get_conn()
    rows = conn.execute("SELECT time, temp, hum, device FROM readings ORDER BY id DESC LIMIT ?",
                        (limit,)).fetchall()
    conn.close()
    rows.reverse()
    return [{"time": r[0], "temp": r[1], "hum": r[2], "device": r[3]} for r in rows]

def all_rows():
    """全部数据(导出用)"""
    conn = get_conn()
    rows = conn.execute("SELECT time, temp, hum, device FROM readings ORDER BY id").fetchall()
    conn.close()
    return [{"time": r[0], "temp": r[1], "hum": r[2], "device": r[3]} for r in rows]

def recent_alerts(limit=10):
    conn = get_conn()
    rows = conn.execute("SELECT time, temp, threshold, device FROM alerts ORDER BY id DESC LIMIT ?",
                        (limit,)).fetchall()
    conn.close()
    return [{"time": r[0], "temp": r[1], "threshold": r[2], "device": r[3]} for r in rows]

def stats():
    conn = get_conn()
    row = conn.execute(
        "SELECT COUNT(*), AVG(temp), MAX(temp), MIN(temp), AVG(hum), MAX(hum), MIN(hum) FROM readings"
    ).fetchone()
    alert_cnt = conn.execute("SELECT COUNT(*) FROM alerts").fetchone()[0]
    conn.close()
    return {
        "count": row[0] or 0,
        "avg_temp": round(row[1], 2) if row[1] is not None else None,
        "max_temp": row[2],
        "min_temp": row[3],
        "avg_hum": round(row[4], 2) if row[4] is not None else None,
        "max_hum": row[5],
        "min_hum": row[6],
        "alert_count": alert_cnt or 0,
    }

def daily_stats(day):
    conn = get_conn()
    row = conn.execute(
        "SELECT COUNT(*), AVG(temp), MAX(temp), MIN(temp), AVG(hum) FROM readings WHERE day = ?",
        (day,)).fetchone()
    conn.close()
    return {
        "count": row[0] or 0,
        "avg_temp": round(row[1], 2) if row[1] is not None else None,
        "max_temp": row[2],
        "min_temp": row[3],
        "avg_hum": round(row[4], 2) if row[4] is not None else None,
        "max_hum": row[5],
        "min_hum": row[6],
    }

if __name__ == "__main__":
    init_db()
    print("数据库初始化/迁移完成:", DB_PATH)
    print("统计:", stats())
