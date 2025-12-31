import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# إعداد الصفحة وتغيير الاتجاه للعربية
st.set_page_config(page_title="المختبر الذكي", layout="wide")
st.markdown("""<style> body { text-align: right; direction: rtl; } </style>""", unsafe_allow_html=True)

# الاتصال بقاعدة البيانات
conn = sqlite3.connect("lab_results.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_name TEXT,
    test_name TEXT,
    result_value TEXT,
    normal_range TEXT,
    date TEXT
)
""")
conn.commit()

st.title("🧪 نظام المختبر الذكي")
st.divider()

# تقسيم الواجهة إلى أعمدة
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📝 إدخال نتيجة جديدة")
    patient_name = st.text_input("اسم المريض")
    test_name = st.text_input("نوع الفحص")
    result_value = st.text_input("النتيجة")
    normal_range = st.text_input("المعدل الطبيعي")
    
    if st.button("💾 حفظ النتيجة"):
        if patient_name and test_name and result_value:
            cursor.execute("INSERT INTO results (patient_name, test_name, result_value, normal_range, date) VALUES (?, ?, ?, ?, ?)",
                           (patient_name, test_name, result_value, normal_range, datetime.now().strftime("%Y-%m-%d %H:%M")))
            conn.commit()
            st.success("تم الحفظ بنجاح!")
            st.rerun() # لتحديث الجدول فوراً
        else:
            st.error("يرجى ملء البيانات الأساسية")

with col2:
    st.subheader("🔍 السجل والبحث")
    search = st.text_input("ابحث عن مريض بالاسم")
    
    query = "SELECT * FROM results"
    if search:
        query += f" WHERE patient_name LIKE '%{search}%'"
    
    df = pd.read_sql_query(query, conn)
    st.dataframe(df, use_container_width=True)

