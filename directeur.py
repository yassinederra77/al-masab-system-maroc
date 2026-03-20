import streamlit as st
import pandas as pd
import random
import string
from database import get_connection

# دالات مساعدة
def generate_password():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))

def generate_login(name, lastname):
    return f"{name.lower().replace(' ', '')}{lastname.lower().replace(' ', '')}@taalim.ma"

def find_column(columns, keywords):
    for key in keywords:
        for col in columns:
            if key in str(col).lower(): return col
    return None

def directeur_panel():
    st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🤵 لوحة المدير</h1>", unsafe_allow_html=True)
    
    menu = [
        "➕ إضافة قسم جديد (Excel)", 
        "🗑️ حذف قسم",
        "👤 إضافة تلميذ يدوي", 
        "🚫 توقيف تلميذ", 
        "✅ إرجاع تلميذ موقوف",
        "📊 إحصائيات الغياب الأسبوعي",
        "🔐 إضافة Login للطاقم"
    ]
    choice = st.sidebar.selectbox("القائمة الإدارية", menu)

    conn = get_connection()

    # 1. إضافة قسم جديد (Excel)
    if choice == "➕ إضافة قسم جديد (Excel)":
        st.subheader("إضافة قسم جديد داخل نظام")
        level = st.selectbox("سلك القسم", ["الأولى إعدادي", "الثانية إعدادي", "الثالثة إعدادي", "جدع مشترك"])
        class_num = st.text_input("رقم القسم الذي يجب إضافته")
        file = st.file_uploader("ارفع ملف Excel", type=["xlsx", "xls"])

        if st.button("💾 معالجة وحفظ القسم"):
            if file and class_num:
                df_excel = pd.read_excel(file, dtype=str).fillna("")
                cols = df_excel.columns
                
                # البحث الذكي عن الأعمدة لتناسب كود database.py الخاص بك
                n_col = find_column(cols, ["الاسم", "name", "first"])
                ln_col = find_column(cols, ["النسب", "lastname", "last"])
                dob_col = find_column(cols, ["ازدياد", "birth", "date"])
                num_col = find_column(cols, ["ترتيب", "number", "no"])
                gen_col = find_column(cols, ["نوع", "gender", "sexe"])

                cursor = conn.cursor()
                cursor.execute("INSERT OR IGNORE INTO classes (level, class_num) VALUES (?,?)", (level, class_num))
                cursor.execute("SELECT id FROM classes WHERE level=? AND class_num=?", (level, class_num))
                c_id = cursor.fetchone()[0]

                for i, row in df_excel.iterrows():
                    # استعمال الأسماء الصحيحة: birth, number, gender
                    cursor.execute("""
                        INSERT INTO students (name, lastname, birth, number, gender, class_id, status) 
                        VALUES (?, ?, ?, ?, ?, ?, 'active')
                    """, (str(row.get(n_col, "")), str(row.get(ln_col, "")), str(row.get(dob_col, "")), 
                          str(row.get(num_col, "")), str(row.get(gen_col, "")), c_id))
                
                conn.commit()
                st.success(f"✅ تم حفظ القسم {level} {class_num} بنجاح.")

    # 2. حذف قسم
    elif choice == "🗑️ حذف قسم":
        st.subheader("🗑️ حذف قسم نهائياً")
        classes = pd.read_sql_query("SELECT * FROM classes", conn)
        if not classes.empty:
            selected_class = st.selectbox("اختر القسم لحذفه", classes.apply(lambda x: f"{x['id']} | {x['level']} - {x['class_num']}", axis=1))
            c_id = selected_class.split(" | ")[0]
            if st.button("❌ تأكيد الحذف النهائي"):
                cursor = conn.cursor()
                cursor.execute("DELETE FROM attendance WHERE student_id IN (SELECT id FROM students WHERE class_id=?)", (c_id,))
                cursor.execute("DELETE FROM students WHERE class_id=?", (c_id,))
                cursor.execute("DELETE FROM classes WHERE id=?", (c_id,))
                conn.commit()
                st.warning("⚠️ تم حذف القسم وجميع بياناته.")
                st.rerun()

    # 3. إضافة تلميذ يدوي
    elif choice == "👤 إضافة تلميذ يدوي":
        st.subheader("📝 إضافة تلميذ جديد")
        with st.form("add_student"):
            n = st.text_input("إسم التلميذ")
            ln = st.text_input("نسب التلميذ")
            birth = st.text_input("تاريخ الإزدياد (YYYY-MM-DD)")
            num = st.text_input("رقم الترتيب")
            gen = st.selectbox("النوع", ["ذكر", "أنثى"])
            lv = st.selectbox("السلك", ["الأولى إعدادي", "الثانية إعدادي", "الثالثة إعدادي", "جدع مشترك"])
            cn = st.text_input("رقم القسم")
            if st.form_submit_button("حفظ في النظام"):
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM classes WHERE level=? AND class_num=?", (lv, cn))
                res = cursor.fetchone()
                if res:
                    cursor.execute("""
                        INSERT INTO students (name, lastname, birth, number, gender, class_id, status) 
                        VALUES (?,?,?,?,?,?,'active')""", (n, ln, birth, num, gen, res[0]))
                    conn.commit()
                    st.success("✅ تم إضافة التلميذ بنجاح")
                else: st.error("❌ القسم غير موجود")

    # 4. توقيف تلميذ
    elif choice == "🚫 توقيف تلميذ":
        st.subheader("🚫 توقيف تلميذ")
        col1, col2 = st.columns(2)
        with col1:
            lv = st.selectbox("السلك", ["الأولى إعدادي", "الثانية إعدادي", "الثالثة إعدادي", "جدع مشترك"])
            n = st.text_input("الإسم")
        with col2:
            cn = st.text_input("رقم القسم")
            ln = st.text_input("النسب")
        
        if st.button("🔍 بحث عن التلميذ"):
            query = """
                SELECT s.id, s.name, s.lastname, s.status FROM students s 
                JOIN classes c ON s.class_id = c.id 
                WHERE c.level=? AND c.class_num=?
            """
            df = pd.read_sql_query(query, conn, params=(lv, cn))
            for _, row in df.iterrows():
                c1, c2 = st.columns([3,1])
                is_target = (row['name'] == n and row['lastname'] == ln)
                color = "red" if is_target else "black"
                c1.markdown(f"<p style='color:{color}; font-weight:bold;'>👤 {row['name']} {row['lastname']} | الحالة: {row['status']}</p>", unsafe_allow_html=True)
                if c2.button("توقيف", key=f"stop_{row['id']}"):
                    conn.execute("UPDATE students SET status='stopped' WHERE id=?", (row['id'],))
                    conn.commit()
                    st.success(f"تم توقيف {row['name']}")
                    st.rerun()

    # 5. إرجاع تلميذ موقوف
    elif choice == "✅ إرجاع تلميذ موقوف":
        st.subheader("🔄 إرجاع تلميذ")
        search = st.text_input("ابحث عن اسم التلميذ الموقوف")
        if search:
            df = pd.read_sql_query("SELECT id, name, lastname FROM students WHERE name LIKE ? AND status='stopped'", conn, params=(f'%{search}%',))
            for _, row in df.iterrows():
                col1, col2 = st.columns([3,1])
                col1.write(f"👤 {row['name']} {row['lastname']}")
                if col2.button("إرجاع", key=f"back_{row['id']}"):
                    conn.execute("UPDATE students SET status='active' WHERE id=?", (row['id'],))
                    conn.commit()
                    st.success("✅ تم الإرجاع")
                    st.rerun()

    # 6. إحصائيات الغياب الأسبوعي
    elif choice == "📊 إحصائيات الغياب الأسبوعي":
        st.subheader("📈 تقارير الغياب")
        classes = pd.read_sql_query("SELECT * FROM classes", conn)
        for _, cl in classes.iterrows():
            if st.button(f"📁 قسم: {cl['level']} - {cl['class_num']}", key=f"cl_{cl['id']}"):
                # تجميع الغياب حسب الطالب والتاريخ
                query = """
                    SELECT s.name, s.lastname, a.date, COUNT(a.id) as sessions_count, 
                    GROUP_CONCAT(a.session || ' (' || a.period || ')') as details
                    FROM attendance a 
                    JOIN students s ON a.student_id = s.id 
                    WHERE s.class_id = ? 
                    GROUP BY s.id, a.date
                    ORDER BY a.date DESC
                """
                abs_data = pd.read_sql_query(query, conn, params=(cl['id'],))
                if abs_data.empty: st.info("لا غياب مسجل.")
                else: st.table(abs_data)

    # 7. إضافة Login
    elif choice == "🔐 إضافة Login للطاقم":
        st.subheader("🔑 إنشاء حساب جديد")
        role_disp = st.selectbox("الفئة", ["الأستاذ", "الحارس العام", "المدير"])
        role_map = {"الأستاذ": "prof", "الحارس العام": "surveillant", "المدير": "directeur"}
        
        n = st.text_input("الإسم")
        ln = st.text_input("النسب")
        ph = st.text_input("رقم الهاتف")
        sj = st.text_input("المادة")
        
        if st.button("إنشاء الحساب"):
            l = generate_login(n, ln)
            p = generate_password()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (login, password, role, name, lastname, phone, subject, status) 
                VALUES (?, ?, ?, ?, ?, ?, ?, 'active')
            """, (l, p, role_map[role_disp], n, ln, ph, sj))
            conn.commit()
            st.success(f"✅ Login: {l} | Pass: {p}")

    conn.close()