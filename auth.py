import streamlit as st
from database import get_connection, get_system_status

def login():
    st.markdown("<h2 style='text-align: center;'>🏫 Al Masab Service</h2>", unsafe_allow_html=True)
    st.markdown("<div style='display:flex; justify-content:center; font-size:18px; font-weight:bold; background: linear-gradient(90deg, #2c3e50, #4b6cb7); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>⚙️ VERSION DE SYSTÈMES v1.0.0</div>", unsafe_allow_html=True)

    login_input = st.text_input("Login")
    password = st.text_input("Password", type="password")

    if st.button("Se connecter"):
        # 🔌 التحقق من حالة النظام
        system_status = get_system_status()
        if system_status == "off" and login_input != "yassinederra@service":
            st.error("🔧 نود إعلامكم بأن النظام متوقف مؤقتًا لأغراض الصيانة للاستفسار أو لمزيد من المعلومات يرجى التواصل مع خدمة العملاء على الرقم 07.21.82.59.21")
            return

        # 📥 التحقق من قاعدة البيانات
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT role, name, status FROM users WHERE login=? AND password=?", (login_input, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            role, name, status = user
            if status == "stopped":
                st.error("تعذر الاتصال بالخادم يُرجى التواصل مع خدمة العملاء.")
                return

            st.session_state["login"] = True
            st.session_state["role"] = role
            st.session_state["name"] = name
            st.success(f"مرحباً {name}!")
            st.rerun()
        else:
            st.error("❌ معلومات تسجيل الدخول غير صحيحة، يُرجى التحقق منها")
