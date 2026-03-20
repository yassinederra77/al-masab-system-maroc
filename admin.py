import streamlit as st
import random
import string
import sqlite3
import pandas as pd
from database import get_connection, get_system_status, set_system_status

# 🔐 توليد password
def generate_password():
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(10))

# 🎯 توليد login
def generate_login(name, lastname):
    return f"{name.lower()}{lastname.lower()}@taalim.ma"

def admin_panel():
    st.title("🧑‍🔧 Service technique")

    # جلب البيانات من SQL بدل CSV
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM users", conn)
    conn.close()

    # =========================
    # 🔒 معلومات الحساب التقني
    # =========================
    st.info("👨‍💻 الحساب التقني الأساسي:\nlogin: yassinederra@service")

    # =========================
    # ➕ إضافة مستخدم
    # =========================
    st.subheader("➕ إضافة مستخدم جديد إلى القاعدة")

    name = st.text_input("الإسم")
    lastname = st.text_input("النسب")
    phone = st.text_input("رقم الهاتف")
    subject = st.text_input("المادة")

    role = st.selectbox("الفئة", ["prof", "surveillant", "directeur"])

    if st.button("إنشاء حساب"):
        if name and lastname and phone and subject:
            login = generate_login(name, lastname)
            password = generate_password()

            # حفظ في SQL
            conn = get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO users (login, password, role, name, lastname, phone, subject, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 'active')
                ''', (login, password, role, name, lastname, phone, subject))
                conn.commit()
                st.success(f"✅ تم الحفظ في القاعدة: {login}")
                st.warning(f"🔐 كلمة المرور: {password}")
            except Exception as e:
                st.error(f"❌ خطأ: {e}")
            finally:
                conn.close()
            st.rerun()
        else:
            st.error("❌ جميع الخانات ضرورية")

    # =========================
    # 📊 إدارة المستخدمين
    # =========================
    st.subheader("📊 قائمة المستخدمين المسجلين")
    st.dataframe(df)

    # =========================
    # ⛔ توقيف أو حذف حساب
    # =========================
    col_stop, col_del = st.columns(2)

    with col_stop:
        st.subheader("⛔ توقيف حساب")
        if not df.empty:
            user_to_stop = st.selectbox("اختار login لتوقيفه", df["login"], key="stop_select")
            if st.button("توقيف الآن"):
                conn = get_connection()
                conn.execute("UPDATE users SET status = 'stopped' WHERE login = ?", (user_to_stop,))
                conn.commit()
                conn.close()
                st.success("تم التوقيف بنجاح ✅")
                st.rerun()

    with col_del:
        st.subheader("❌ حذف نهائي")
        if not df.empty:
            user_to_del = st.selectbox("اختار login لحذفه", df["login"], key="del_select")
            if st.button("حذف نهائي"):
                conn = get_connection()
                conn.execute("DELETE FROM users WHERE login = ?", (user_to_del,))
                conn.commit()
                conn.close()
                st.success("تم الحذف من القاعدة ✅")
                st.rerun()

    # =========================
    # 🔌 التحكم في النظام
    # =========================
    st.divider()
    status = get_system_status()
    st.write(f"حالة النظام الحالية: *{status}*")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("إيقاف النظام 🚫"):
            set_system_status("off")
            st.rerun()
    with c2:
        if st.button("تشغيل النظام ✅"):
            set_system_status("on")
            st.rerun()