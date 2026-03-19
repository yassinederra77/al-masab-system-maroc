import sqlite3
import pandas as pd
import os

DB_NAME = "school_data.db"
SYSTEM_FILE = "system_state.txt"

def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    # جدول المستخدمين
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
        (login TEXT PRIMARY KEY, password TEXT, role TEXT, name TEXT, lastname TEXT, phone TEXT, subject TEXT, status TEXT DEFAULT 'active')''')
    
    # جدول الأقسام
    cursor.execute('''CREATE TABLE IF NOT EXISTS classes 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, level TEXT, class_num TEXT, UNIQUE(level, class_num))''')
    
    # جدول التلاميذ (بكل التفاصيل)
    cursor.execute('''CREATE TABLE IF NOT EXISTS students 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, lastname TEXT, birth TEXT, number TEXT, gender TEXT, class_id INTEGER, status TEXT DEFAULT 'active',
        FOREIGN KEY (class_id) REFERENCES classes (id))''')
    
    # جدول الغياب
    cursor.execute('''CREATE TABLE IF NOT EXISTS attendance 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER, date TEXT, day TEXT, session TEXT, period TEXT, allowed INTEGER DEFAULT 0,
        FOREIGN KEY (student_id) REFERENCES students (id))''')
    conn.commit()
    conn.close()

def load_users():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM users", conn)
    conn.close()
    return df

def save_user(login, password, role, name, lastname, phone, subject):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO users (login, password, role, name, lastname, phone, subject, status) VALUES (?,?,?,?,?,?,?, 'active')",
                   (login, password, role, name, lastname, phone, subject))
    conn.commit()
    conn.close()

def get_system_status():
    if not os.path.exists(SYSTEM_FILE): return "on"
    with open(SYSTEM_FILE, "r") as f: return f.read().strip()

def set_system_status(status):
    with open(SYSTEM_FILE, "w") as f: f.write(status)

init_db()