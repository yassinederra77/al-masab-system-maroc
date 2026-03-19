import streamlit as st
import pandas as pd
from database import get_connection

def surveillant_panel():
    st.markdown("<h1 style='text-align: center; color: #2E86C1;'>🧑‍💼 تتبع غياب التلاميذ</h1>", unsafe_allow_html=True)
    
    conn = get_connection()

    # 1. اختيار القسم
    col1, col2 = st.columns(2)
    with col1:
        level = st.selectbox("السلك", ["الأولى إعدادي", "الثانية إعدادي", "الثالثة إعدادي", "جدع مشترك"])
    with col2:
        class_num = st.text_input("رقم القسم")

    if st.button("📊 عرض لائحة الغياب"):
        st.session_state.view_class = True
    
    if st.session_state.get("view_class", False):
        st.divider()
        
        # جلب كل التلاميذ اللي عندهم غياب (allowed=0 يعني باقي ما دخلوش، allowed=1 يعني دخلوا ولكن السجل كاين)
        query = """
            SELECT a.id as abs_id, s.id as std_id, s.name, s.lastname, a.date, a.session, a.period, a.allowed
            FROM attendance a
            JOIN students s ON a.student_id = s.id
            JOIN classes c ON s.class_id = c.id
            WHERE c.level = ? AND c.class_num = ?
            ORDER BY a.date DESC, a.session ASC
        """
        df = pd.read_sql_query(query, conn, params=(level, class_num))

        if df.empty:
            st.success("✅ لا يوجد سجل غياب لهذا القسم.")
        else:
            # تجميع التلاميذ (Unique Students)
            students_with_abs = df[['std_id', 'name', 'lastname']].drop_duplicates()

            for _, std in students_with_abs.iterrows():
                # جلب غيابات هاد التلميذ فقط اللي "باقي ما مسموحش ليه" (اللون الأحمر)
                unallowed_abs = df[(df['std_id'] == std['std_id']) & (df['allowed'] == 0)]
                
                # جلب أرشيف الغياب كامل (حتى اللي مسموح ليه) باش يشوفو المدير/الحارس
                full_history = df[df['std_id'] == std['std_id']]

                # حساب الساعات اللي باقي ما تبرراتش
                total_hours = len(unallowed_abs)
                status_color = "#FF4B4B" if total_hours > 0 else "#28a745"
                
                # العنوان (إسم التلميذ)
                with st.expander(f"👤 {std['name']} {std['lastname']} | الساعات غير المبررة: {total_hours}"):
                    
                    if total_hours > 0:
                        st.markdown(f"<h4 style='color:red;'>⚠️ غيابات تنتظر السماح:</h4>", unsafe_allow_html=True)
                        
                        # تجميع الغيابات حسب التاريخ
                        dates = unallowed_abs['date'].unique()
                        for d in dates:
                            day_abs = unallowed_abs[unallowed_abs['date'] == d]
                            st.markdown(f"*📅 يوم {d} (عدد الساعات: {len(day_abs)})*")
                            for _, row in day_abs.iterrows():
                                st.write(f"🔹 الحصة {row['session']} - الفترة {row['period']}")
                        
                        # زر السماح بالدخول (يبرر كل الساعات دفعة واحدة)
                        if st.button(f"✅ إعطاء ورقة السماح لـ {std['name']}", key=f"btn_{std['std_id']}"):
                            cursor = conn.cursor()
                            cursor.execute("UPDATE attendance SET allowed = 1 WHERE student_id = ? AND allowed = 0", (int(std['std_id']),))
                            conn.commit()
                            st.success(f"تم السماح للدخول. الغياب تم أرشفته.")
                            st.rerun()
                    else:
                        st.success("✅ التلميذ وضعيتُه سليمة حالياً (حاضر).")

                    # الجزء الخاص بالأرشيف (ليحتاجه المدير عند حضور ولي الأمر)
                    st.divider()
                    with st.expander("📚 أرشيف الغياب الكامل (للمدير)"):
                        if full_history.empty:
                            st.write("الأرشيف فارغ.")
                        else:
                            # جدول مرتب للأرشيف
                            archive_df = full_history[['date', 'session', 'period', 'allowed']].copy()
                            archive_df['الحالة'] = archive_df['allowed'].apply(lambda x: "مسموح/مبرر" if x==1 else "غير مبرر")
                            st.table(archive_df[['date', 'session', 'period', 'الحالة']])

    conn.close()