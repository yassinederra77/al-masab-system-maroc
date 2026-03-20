import streamlit as st
import pandas as pd
import datetime
from database import get_connection

def prof_panel():
    st.markdown("<h1 style='text-align: center; color: #4A90E2;'>👨‍🏫 تسجيل غياب التلاميذ</h1>", unsafe_allow_html=True)
    
    conn = get_connection()

    # 1. إعداد الخانات
    col1, col2 = st.columns(2)
    with col1:
        level = st.selectbox("السلك", ["الأولى إعدادي", "الثانية إعدادي", "الثالثة إعدادي", "جدع مشترك"])
        session = st.selectbox("اختر الحصة", ["الأولى", "الثانية", "الثالثة", "الرابعة"])
    
    with col2:
        class_num = st.text_input("رقم القسم")
        today = datetime.date.today().isoformat()
        day_mapping = {"Monday": "الإثنين", "Tuesday": "الثلاثاء", "Wednesday": "الأربعاء", "Thursday": "الخميس", "Friday": "الجمعة", "Saturday": "السبت", "Sunday": "الأحد"}
        day_name = day_mapping.get(datetime.date.today().strftime('%A'), datetime.date.today().strftime('%A'))

    period = st.radio("الفترة", ["صباحية", "مسائية"], horizontal=True)

    if st.button("🔍 بحث"):
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM classes WHERE level=? AND class_num=?", (level, class_num))
        result = cursor.fetchone()
        if result:
            st.session_state.class_id = result[0]
            st.session_state.show_list = True
            st.session_state.temp_absents = [] 
        else:
            st.error("❌ القسم غير موجود.")
            st.session_state.show_list = False

    if st.session_state.get("show_list", False):
        st.divider()
        c_id = st.session_state.class_id
        
        # جلب التلاميذ
        students = pd.read_sql_query(f"SELECT id, name, lastname FROM students WHERE class_id={c_id} AND status='active'", conn)
        
        # 1. جلب الغيابات المسجلة في "الحصة الحالية" فقط (باش نقفلوها)
        absent_this_session = pd.read_sql_query(f"""
            SELECT student_id FROM attendance 
            WHERE date='{today}' AND session='{session}' AND period='{period}' AND allowed = 0
        """, conn)['student_id'].tolist()

        # 2. جلب التلاميذ اللي غايبين في "حصص أخرى" ديال هاد النهار (باش نبينوهم بالأحمر ولكن نخليو الزر خدام)
        absent_other_sessions = pd.read_sql_query(f"""
            SELECT DISTINCT student_id FROM attendance 
            WHERE date='{today}' AND session != '{session}' AND allowed = 0
        """, conn)['student_id'].tolist()

        if "temp_absents" not in st.session_state: st.session_state.temp_absents = []

        for i, row in students.iterrows():
            col_n, col_btn = st.columns([4, 1])
            
            # تحديد الحالة
            is_recorded_now = row['id'] in absent_this_session # غايب دابا (مقفول)
            is_absent_before = row['id'] in absent_other_sessions # غايب في حصة خرا (لون أحمر ولكن زر خدام)
            is_selected = row['id'] in st.session_state.temp_absents # اختاره الأستاذ دابا
            
            # اللون كيكون أحمر إلا كان غايب دابا أو قبل أو مختار دابا
            bg_color = "#FF4B4B" if (is_recorded_now or is_absent_before or is_selected) else "#f9f9f9"
            text_color = "white" if (is_recorded_now or is_absent_before or is_selected) else "black"
            
            status_info = ""
            if is_recorded_now: status_info = " (مسجل في هذه الحصة)"
            elif is_absent_before: status_info = " (غائب في حصة سابقة)"

            col_n.markdown(f"""
                <div style="padding:12px; border-radius:8px; border:1px solid #ddd; 
                            background-color: {bg_color}; color: {text_color}; font-weight: bold; margin-bottom: 5px;">
                    👤 {row['name']} {row['lastname']} {status_info}
                </div>
            """, unsafe_allow_html=True)
            
            with col_btn:
                if is_recorded_now:
                    # إلا ديجا ماركاه هاد الأستاذ في هاد الحصة، كيتقفل
                    st.button("🔒", key=f"lock_{row['id']}", disabled=True)
                else:
                    # إلا كان غايب في حصة سابقة، الزر كيبقى خدام باش الأستاذ "يأكد" غيابه حتى في حصته
                    btn_label = "إلغاء" if is_selected else "غائب 🔴"
                    if st.button(btn_label, key=f"abs_{row['id']}"):
                        if row['id'] not in st.session_state.temp_absents:
                            st.session_state.temp_absents.append(row['id'])
                        else:
                            st.session_state.temp_absents.remove(row['id'])
                        st.rerun()

        st.divider()
        if st.button("💾 حفظ المعلومات", type="primary", use_container_width=True):
            if st.session_state.temp_absents:
                cursor = conn.cursor()
                for s_id in st.session_state.temp_absents:
                    cursor.execute("INSERT INTO attendance (student_id, date, day, session, period, allowed) VALUES (?,?,?,?,?,0)", 
                                   (int(s_id), today, day_name, session, period))
                conn.commit()
                st.session_state.temp_absents = []
                st.success(f"✅ تم تسجيل الغياب بنجاح {session}")
                st.rerun()
            else:
                st.warning("⚠️ نود إعلامكم بأنه لم يتم تسجيل أي غياب في هذا القسم في الوقت الحالي")

    conn.close()