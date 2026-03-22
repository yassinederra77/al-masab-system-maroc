import libsql_client as libsql
import pandas as pd
import streamlit as st


# إعدادات السحاب
TURSO_URL = "https://al-masab-db-yassinederra77.aws-eu-west-1.turso.io"
TURSO_TOKEN = "EyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3NzQxMzIzNzYsImlkIjoiMDE5ZDEyODctODQwMS03ZTdhLWI4ODgtMTI2YmM3YjU1YTRiIiwicmlkIjoiOGVmYzQzOWMtZjAzMS00NWQwLWJhZTItMzRiOTRiNWMwNjZiIn0.mXHyH939WTc_dFjg82Z9Ur8zl5azWacapBWgjgv7A5w2lM7U6OAoH4IIMgWHNg861lvSDxIWOHfCbRidZ90aDQ"


class TursoAdapter:
    def __init__(self):
        self.last_result = None


    def cursor(self):
        return self


    def execute(self, query, params=None):
        # الحل الأقوى: إنشاء عميل جديد لكل عملية تنفيذ لضمان عدم حدوث تعارض في بايثون 3.14
        p = list(params) if params is not None else []
        try:
            with libsql.create_client_sync(url=TURSO_URL, auth_token=TURSO_TOKEN) as client:
                self.last_result = client.execute(query, p)
        except Exception as e:
            # إظهار الخطأ الحقيقي للمساعدة في التشخيص
            st.error(f"⚠️ فشل في السحاب: {query}")
            raise e
        return self


    def fetchone(self):
        return self.last_result.rows[0] if self.last_result and self.last_result.rows else None


    def fetchall(self):
        return self.last_result.rows if self.last_result else []


    def commit(self): pass
    def close(self): pass


def get_connection():
    return TursoAdapter()


def init_db():
    conn = get_connection()
    # أوامر الجداول من كودك الأصلي
    queries = [
        "CREATE TABLE IF NOT EXISTS users (login TEXT PRIMARY KEY, password TEXT, role TEXT, name TEXT, lastname TEXT, phone TEXT, subject TEXT, status TEXT DEFAULT 'active')",
        "CREATE TABLE IF NOT EXISTS classes (id INTEGER PRIMARY KEY AUTOINCREMENT, level TEXT, class_num TEXT, UNIQUE(level, class_num))",
        "CREATE TABLE IF NOT EXISTS students (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, lastname TEXT, birth TEXT, number TEXT, gender TEXT, class_id INTEGER, status TEXT DEFAULT 'active', FOREIGN KEY (class_id) REFERENCES classes (id))",
        "CREATE TABLE IF NOT EXISTS attendance (id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER, date TEXT, day TEXT, session TEXT, period TEXT, allowed INTEGER DEFAULT 0, FOREIGN KEY (student_id) REFERENCES students (id))",
        "CREATE TABLE IF NOT EXISTS system_config (key TEXT PRIMARY KEY, value TEXT)",
        "INSERT OR IGNORE INTO system_config (key, value) VALUES ('status', 'on')"
    ]
    for q in queries:
        conn.execute(q)


def load_users():
    conn = get_connection()
    res = conn.execute("SELECT * FROM users")
    # التأكد من أسماء الأعمدة للتوافق مع باقي النظام
    cols = res.last_result.columns if res.last_result else ["login", "password", "role", "name", "lastname", "phone", "subject", "status"]
    df = pd.DataFrame(res.fetchall(), columns=cols)
    return df


def save_user(login, password, role, name, lastname, phone, subject):
    conn = get_connection()
    conn.execute(
        "INSERT OR REPLACE INTO users (login, password, role, name, lastname, phone, subject, status) VALUES (?,?,?,?,?,?,?, 'active')",
        [login, password, role, name, lastname, phone, subject]
    )


def get_system_status():
    try:
        conn = get_connection()
        row = conn.execute("SELECT value FROM system_config WHERE key='status'").fetchone()
        return row[0] if row else "on"
    except:
        return "on"


def set_system_status(status):
    conn = get_connection()
    conn.execute("UPDATE system_config SET value=?", [status])


# تشغيل التهيئة عند تحميل الملف
init_db()
