import pandas as pd
import streamlit as st
import requests

# 1. الرابط المأخوذ من صورتك (مع تحويله لـ https للعمل عبر API)
URL = "https://al-masab-db-yassinederra77.turso.io/v1/execute"
TOKEN = "EyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3NzQxMzIzNzYsImlkIjoiMDE5ZDEyODctODQwMS03ZTdhLWI4ODgtMTI2YmM3YjU1YTRiIiwicmlkIjoiOGVmYzQzOWMtZjAzMS00NWQwLWJhZTItMzRiOTRiNWMwNjZiIn0.mXHyH939WTc_dFjg82Z9Ur8zl5azWacapBWgjgv7A5w2lM7U6OAoH4IIMgWHNg861lvSDxIWOHfCbRidZ90aDQ"

class TursoAdapter:
    def __init__(self):
        self.rows = []
        self.columns = []

    def execute(self, query, params=None):
        p = list(params) if params is not None else []
        # تحويل المعاملات للشكل الذي يفهمه Turso API
        formatted_args = []
        for v in p:
            formatted_args.append({"type": "text", "value": str(v)})

        headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
        payload = {"stmt": {"sql": query, "args": formatted_args}}
        
        try:
            resp = requests.post(URL, headers=headers, json=payload, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if "result" in data:
                    self.columns = data["result"].get("cols", [])
                    # تحويل النتائج لمصفوفة بسيطة
                    self.rows = [[item.get("value") for item in row] for row in data["result"].get("rows", [])]
            else:
                st.error(f"خطأ 400: السيرفر لم يقبل الطلب. تأكد من Token.")
        except Exception as e:
            st.error(f"فشل الاتصال: {e}")
        return self

    def fetchone(self): return self.rows[0] if self.rows else None
    def fetchall(self): return self.rows
    def cursor(self): return self
    def close(self): pass

def get_connection(): return TursoAdapter()

def init_db():
    conn = get_connection()
    # إنشاء الجداول (هاد المرة غيتزاد الـ Activity في الصورة عندك)
    queries = [
        "CREATE TABLE IF NOT EXISTS users (login TEXT PRIMARY KEY, password TEXT, role TEXT, name TEXT, lastname TEXT, phone TEXT, subject TEXT, status TEXT DEFAULT 'active')",
        "CREATE TABLE IF NOT EXISTS system_config (key TEXT PRIMARY KEY, value TEXT)",
        "INSERT OR IGNORE INTO system_config (key, value) VALUES ('status', 'on')",
        "INSERT OR IGNORE INTO users (login, password, role, name, status) VALUES ('yassinederra@service', 'yassinederra.2009', 'admin', 'Yassine', 'active')"
    ]
    for q in queries: conn.execute(q)

def get_system_status():
    try:
        res = get_connection().execute("SELECT value FROM system_config WHERE key='status'").fetchone()
        return res[0] if res else "on"
    except: return "on"

# تشغيل التهيئة
init_db()
