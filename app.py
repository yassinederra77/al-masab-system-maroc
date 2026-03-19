import streamlit as st
from auth import login
from database import save_user, load_users
from admin import admin_panel
from prof import prof_panel
from surveillant import surveillant_panel
from directeur import directeur_panel

# إنشاء admin أول مرة
if "init" not in st.session_state:
    df = load_users()

    if df.empty:
        save_user(
            "yassinederra@service",
            "yassinederra.2009",
            "admin",
            "Yassine",
            "Derra",
            "-",        # phone
            "-"         # subject
        )

    st.session_state.init = True

# Login
if "login" not in st.session_state or not st.session_state["login"]:
    login()

else:
    role = st.session_state["role"]

    st.sidebar.title("Dashboard")

    if role == "admin":
       admin_panel()

    elif role == "prof":
       prof_panel()

    elif role == "surveillant":
       surveillant_panel()

    elif role == "directeur":
       directeur_panel()