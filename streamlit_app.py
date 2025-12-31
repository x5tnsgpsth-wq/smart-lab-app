import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# إعدادات الصفحة
st.set_page_config(page_title="المختبر الذكي", layout="wide")

# تصميم واجهة عربية
st.markdown("""
    <style>
    .main { text-align: right; direction: rtl; }
    div[data-testid="stBlock"] { text-align: right; direction: rtl; }
    </style>
    """, unsafe_allow_html=True)

# الاتصال بقاعدة البيانات
conn = sqlite3.connect("lab_results.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_name TEXT,
    test_name TEXT,
    result_value REAL,
    min_range REAL,
    max_range REAL,
    date TEXT
)
""")
conn.commit()

st.title("🧪 نظام إدارة نتائج المختبر")

# --- قسم إدخال البيانات ---
with st.expander("➕ إضافة نتيجة فحص جديدة"):
    col1, col2 = st.columns(2)
    with col1:
        p_name = st.text_input("اسم المريض")
        t_name = st.text_input("نوع الفحص (مثلاً: Glucose)")
    with col2:
        r_val = st.number_input("النتيجة المخبرية", format="%.2f")
        min_v = st.number_input("الحد الأدنى الطبيعي", value=0.0)
        max_v = st.number_input("الحد الأعلى الطبيعي", value=100.0)

    if st.button("💾 حفظ وإضافة للسجل"):
        if p_name and t_name:
            cursor.execute("INSERT INTO results (patient_name, test_name, result_value, min_range, max_range, date) VALUES (?,?,?,?,?,?)",
                           (p_name, t_name, r_val, min_v, max_v, datetime.now().strftime("%Y-%m-%d %H:%M")))
            conn.commit()
            st.success(f"تم تسجيل فحص المريض: {p_name}")
            st.rerun()

st.divider()

# --- قسم العرض والبحث ---
st.subheader("📋 سجل الفحوصات")
search = st.text_input("🔍 ابحث عن اسم مريض...")

query = "SELECT * FROM results"
if search:
    query += f" WHERE patient_name LIKE '%{search}%'"

df = pd.read_sql_query(query, conn)

# وظيفة لتلوين النتائج غير الطبيعية
def highlight_results(row):
    color = 'white'
    if row['result_value'] > row['max_range'] or row['result_value'] < row['min_range']:
        color = '#ffcccc' # أحمر خفيف للنتائج المقلقة
    return ['background-color: %s' % color] * len(row)

if not df.empty:
    st.dataframe(df.style.apply(highlight_results, axis=1), use_container_width=True)
else:
    st.info("لا توجد بيانات مسجلة حالياً.")


