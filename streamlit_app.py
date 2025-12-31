import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# الاتصال بقاعدة البيانات
conn = sqlite3.connect("lab_results.db", check_same_thread=False)
cursor = conn.cursor()

# إنشاء الجدول إذا لم يكن موجودًا
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

st.title("🧪 المختبر الذكي")

st.subheader("إدخال نتيجة فحص")

patient_name = st.text_input("اسم المريض")
test_name = st.text_input("اسم الفحص")
result_value = st.text_input("النتيجة")
normal_range = st.text_input("القيم الطبيعية")

if st.button("💾 حفظ النتيجة"):
    if patient_name and test_name and result_value:
        cursor.execute("""
        INSERT INTO results (patient_name, test_name, result_value, normal_range, date)
        VALUES (?, ?, ?, ?, ?)
        """, (
            patient_name,
            test_name,
            result_value,
            normal_range,
            datetime.now().strftime("%Y-%m-%d %H:%M")
        ))
        conn.commit()
        st.success("✅ تم حفظ النتيجة بنجاح")
    else:
        st.warning("⚠️ يرجى ملء الحقول الأساسية")

st.subheader("النتائج المحفوظة")

# البحث
search_name = st.text_input("🔍 ابحث باسم المريض")

if search_name:
    df = pd.read_sql_query(
        "SELECT * FROM results WHERE patient_name LIKE ?",
        conn,
        params=(f"%{search_name}%",)
    )
else:
    df = pd.read_sql_query("SELECT * FROM results", conn)

st.dataframe(df, use_container_width=True)
