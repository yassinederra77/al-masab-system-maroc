import pandas as pd
import streamlit as st
import requests

# الإعدادات السحابية الصحيحة
URL = "https://al-masab-db-yassinederra77.turso.io/v1/execute"
TOKEN = "EyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3NzQxMzIzNzYsImlkIjoiMDE5ZDEyODctODQwMS03ZTdhLWI4ODgtMTI2YmM3YjU1YTRiIiwicmlkIjoiOGVmYzQzOWMtZjAzMS00NWQwLWJhZTItMzRiOTRiNWMwNjZiIn0.mXHyH939WTc_dFjg82Z9Ur8zl5azWacapBWgjgv7A5w2lM7U6OAoH4IIMgWHNg861lvSDxIWOHfCbRidZ90aDQ"

class TursoAdapter:
    def _init_(self):
        self.rows = []
        self.columns = []

    def execute(self, query, params=None):
        p = list(params) if params is not None else []
        formatted_args = [{"type": "text", "value": str(v)} for v in p]
        headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
        payload = {"stmt": {"sql": query, "args": formatted_args}}
        
        try:
            resp = requests.post(URL, headers=headers, json=payload, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if "result" in data:
                    self.columns = data["result"].get("cols", [])
                    self.rows = [[item.get("value") for item in row] for row in data["result"].get("rows", [])]
            return self
        except Exception as e:
            st.error(f"⚠️ خطأ في قاعدة البيانات: {e}")
            return self

    def fetchone(self): return self.rows[0] if self.rows else None
    def fetchall(self): return self.rows
    def cursor(self): return self
    def close(self): pass

def get_connection(): return TursoAdapter()

# --- الدوال التي يطلبها ملف app.py بالاسم ---

def load_users():
    """تستخدمها app.py في السطر 11 للتحقق من وجود مستخدمين"""
    conn = get_connection()
    res = conn.execute("SELECT * FROM users", [])
    # تعريف الأعمدة الافتراضية للتوافق مع DataFrame
    cols = ["login", "password", "role", "name", "lastname", "phone", "subject", "status"]
    return pd.DataFrame(res.rows, columns=cols)

def save_user(login, password, role, name, lastname, phone, subject):
    """تستخدمها app.py في السطر 14 لإنشاء حساب المدير"""
    conn = get_connection()
    query = "INSERT OR REPLACE INTO users (login, password, role, name, lastname, phone, subject, status) VALUES (?,?,?,?,?,?,?, 'active')"
    conn.execute(query, [login, password, role, name, lastname, phone, subject])

def get_system_status():
    """تستخدمها auth.py للتحقق من حالة النظام"""
    try:
        res = get_connection().execute("SELECT value FROM system_config WHERE key='status'").fetchone()
        return res[0] if res else "on"
    except: return "on"

def init_db():
    """إنشاء الجداول عند أول تشغيل"""
    conn = get_connection()
    queries = [
        "CREATE TABLE IF NOT EXISTS users (login TEXT PRIMARY KEY, password TEXT, role TEXT, name TEXT, lastname TEXT, phone TEXT, subject TEXT, status TEXT DEFAULT 'active')",
        "CREATE TABLE IF NOT EXISTS system_config (key TEXT PRIMARY KEY, value TEXT)",
        "INSERT OR IGNORE INTO system_config (key, value) VALUES ('status', 'on')"
    ]
    for q in queries: conn.execute(q)

# تشغيل التهيئة آلياً
init_db()
