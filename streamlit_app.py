import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# 1. إعدادات الصفحة (يجب أن يكون أول أمر)
st.set_page_config(page_title="نظام المختبر", layout="wide")

# 2. الاتصال بقاعدة البيانات
conn = sqlite3.connect("lab_final.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    test TEXT,
    result REAL,
    status TEXT,
    date TEXT
)
""")
conn.commit()

# 3. واجهة المستخدم
st.title("🧪 نظام المختبر الذكي")

# القائمة الجانبية للتنقل
menu = st.sidebar.selectbox("القائمة الرئيسية", ["إضافة فحص", "عرض السجل"])

if menu == "إضافة فحص":
    st.subheader("📝 إدخال بيانات مريض جديد")
    with st.form("my_form"):
        p_name = st.text_input("اسم المريض")
        t_name = st.selectbox("نوع الفحص", ["Glucose", "CBC", "Urea", "Creatinine"])
        res = st.number_input("النتيجة", format="%.2f")
        
        submitted = st.form_submit_button("حفظ")
        if submitted and p_name:
            status = "طبيعي" if res < 100 else "مرتفع ⚠️"
            dt = datetime.now().strftime("%Y-%m-%d %H:%M")
            cursor.execute("INSERT INTO patients (name, test, result, status, date) VALUES (?,?,?,?,?)",
                           (p_name, t_name, res, status, dt))
            conn.commit()
            st.success("تم الحفظ!")

elif menu == "عرض السجل":
    st.subheader("🔍 سجل النتائج")
    df = pd.read_sql("SELECT name, test, result, status, date FROM patients", conn)
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("السجل فارغ حالياً")

