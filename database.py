import pandas as pd
import streamlit as st
import requests
import json


# 1. الإعدادات الصحيحة (تم تصحيح الرابط للعمل عبر API)
URL = "https://al-masab-db-yassinederra77.turso.io/v1/execute"
TOKEN = "EyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3NzQxMzIzNzYsImlkIjoiMDE5ZDEyODctODQwMS03ZTdhLWI4ODgtMTI2YmM3YjU1YTRiIiwicmlkIjoiOGVmYzQzOWMtZjAzMS00NWQwLWJhZTItMzRiOTRiNWMwNjZiIn0.mXHyH939WTc_dFjg82Z9Ur8zl5azWacapBWgjgv7A5w2lM7U6OAoH4IIMgWHNg861lvSDxIWOHfCbRidZ90aDQ"


class TursoAdapter:
    def __init__(self):
        self.last_result = None
        self.columns = []
        self.rows = []


    def cursor(self): return self


    def execute(self, query, params=None):
        p = list(params) if params is not None else []
        headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
        payload = {"stmt": {"sql": query, "args": [{"type": "text", "value": str(v)} for v in p]}}
        
        try:
            # الاتصال المباشر بـ API السيرفر (كيهرب من مشاكل بايثون 3.14)
            resp = requests.post(URL, headers=headers, json=payload, timeout=10)
            if resp.status_code != 200:
                st.error(f"❌ خطأ من السيرفر: {resp.status_code}")
                return self
            
            data = resp.json()
            # استخراج النتائج
            if "result" in data:
                self.columns = data["result"].get("cols", [])
                self.rows = []
                for row_data in data["result"].get("rows", []):
                    self.rows.append([item.get("value") for item in row_data])
        except Exception as e:
            st.error(f"⚠️ فشل الاتصال: {e}")
        return self


    def fetchone(self): return self.rows[0] if self.rows else None
    def fetchall(self): return self.rows


    @property
    def last_result_cols(self): return self.columns


def get_connection(): return TursoAdapter()


def init_db():
    conn = get_connection()
    queries = [
        "CREATE TABLE IF NOT EXISTS users (login TEXT PRIMARY KEY, password TEXT, role TEXT, name TEXT, lastname TEXT, phone TEXT, subject TEXT, status TEXT DEFAULT 'active')",
        "CREATE TABLE IF NOT EXISTS classes (id INTEGER PRIMARY KEY AUTOINCREMENT, level TEXT, class_num TEXT, UNIQUE(level, class_num))",
        "CREATE TABLE IF NOT EXISTS students (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, lastname TEXT, birth TEXT, number TEXT, gender TEXT, class_id INTEGER, status TEXT DEFAULT 'active', FOREIGN KEY (class_id) REFERENCES classes (id))",
        "CREATE TABLE IF NOT EXISTS attendance (id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER, date TEXT, day TEXT, session TEXT, period TEXT, allowed INTEGER DEFAULT 0, FOREIGN KEY (student_id) REFERENCES students (id))",
        "CREATE TABLE IF NOT EXISTS system_config (key TEXT PRIMARY KEY, value TEXT)",
        "INSERT OR IGNORE INTO system_config (key, value) VALUES ('status', 'on')"
    ]
    for q in queries: conn.execute(q)


def load_users():
    conn = get_connection()
    res = conn.execute("SELECT * FROM users")
    cols = res.columns if res.columns else ["login", "password", "role", "name", "lastname", "phone", "subject", "status"]
    return pd.DataFrame(res.rows, columns=cols)


def save_user(login, password, role, name, lastname, phone, subject):
    get_connection().execute(
        "INSERT OR REPLACE INTO users (login, password, role, name, lastname, phone, subject, status) VALUES (?,?,?,?,?,?,?, 'active')",
        [login, password, role, name, lastname, phone, subject]
    )


def get_system_status():
    try:
        row = get_connection().execute("SELECT value FROM system_config WHERE key='status'").fetchone()
        return row[0] if row else "on"
    except: return "on"


def set_system_status(status):
    get_connection().execute("UPDATE system_config SET value=?", [status])


# تشغيل
init_db()
