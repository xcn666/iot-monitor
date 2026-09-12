#!/usr/bin/env python3
# db.py - SQLite 数据存储模块
import os
import sqlite3

DB_PATH = os.path.expanduser("~/iot-lab/logs/sensor.db")

def get_conn():
    """连接数据库(目录不存在就创建)"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    """建表(如果不存在)"""
    conn = get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS readings (
            id     INTEGER PRIMARY KEY AUTOINCREMENT,
            time   TEXT,
            temp   REAL,
            hum    INTEGER,
            device TEXT
        )
    """)
    conn.commit()
    conn.close()

def insert_reading(time_str, temp, hum, device=""):
    """插入一条数据(? 是占位符, 防SQL注入)"""
    conn = get_conn()
    conn.execute(
        "INSERT INTO readings (time, temp, hum, device) VALUES (?, ?, ?, ?)",
        (time_str, temp, hum, device),
    )
    conn.commit()
    conn.close()

def recent(limit=30):
    """取最近 N 条(按时间从旧到新返回)"""
    conn = get_conn()
    rows = conn.execute(
        "SELECT time, temp, hum, device FROM readings ORDER BY id DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    rows.reverse()
    return [{"time": r[0], "temp": r[1], "hum": r[2], "device": r[3]} for r in rows]

def stats():
    """统计: 总数/平均温度/最高/最低/平均湿度"""
    conn = get_conn()
    row = conn.execute(
        "SELECT COUNT(*), AVG(temp), MAX(temp), MIN(temp), AVG(hum) FROM readings"
    ).fetchone()
    conn.close()
    return {
        "count": row[0] or 0,
        "avg_temp": round(row[1], 2) if row[1] is not None else None,
        "max_temp": row[2],
        "min_temp": row[3],
        "avg_hum": round(row[4], 2) if row[4] is not None else None,
    }

if __name__ == "__main__":
    init_db()
    print("数据库初始化完成:", DB_PATH)
    print("当前统计:", stats())
