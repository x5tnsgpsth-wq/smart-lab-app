import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# إعداد الصفحة وتغيير الاتجاه للعربية
st.set_page_config(page_title="المختبر الذكي", layout="wide")
st.markdown("""<style> * { direction: rtl; text-align: right; } </style>""", unsafe_allow_html=True)

# الاتصال بقاعدة البيانات
conn = sqlite3.connect("lab_final.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    test TEXT,
    result REAL,
    unit TEXT,
    status TEXT,
    date TEXT
)
""")
conn.commit()

# واجهة التطبيق
st.title("🧪 نظام إدارة المختبر الذكي")
st.divider()

# القائمة الجانبية
menu = st.sidebar.radio("القائمة الرئيسية", ["إضافة فحص جديد", "سجل المرضى", "الإحصائيات"])

if menu == "إضافة فحص جديد":
    st.header("📝 إدخال بيانات مريض")
    with st.form("lab_form"):
        col1, col2 = st.columns(2)
        with col1:
            p_name = st.text_input("اسم المريض")
            t_name = st.selectbox("نوع الفحص", ["Glucose", "CBC", "Uric Acid", "Creatinine", "TSH"])
            unit = st.text_input("الوحدة", value="mg/dL")
        with col2:
            res = st.number_input("النتيجة", format="%.2f")
            ref_max = st.number_input("الحد الأعلى الطبيعي", value=100.0)
            
        submit = st.form_submit_button("حفظ البيانات")
        
        if submit and p_name:
            status = "طبيعي" if res <= ref_max else "مرتفع ⚠️"
            date_now = datetime.now().strftime("%Y-%m-%d %H:%M")
            cursor.execute("INSERT INTO patients (name, test, result, unit, status, date) VALUES (?,?,?,?,?,?)",
                           (p_name, t_name, res, unit, status, date_now))
            conn.commit()
            st.success(f"تم حفظ بيانات {p_name}")

elif menu == "سجل المرضى":
    st.header("🔍 سجل النتائج")
    search = st.text_input("ابحث باسم المريض")
    df = pd.read_sql(f"SELECT name as 'المريض', test as 'الفحص', result as 'النتيجة', unit as 'الوحدة', status as 'الحالة', date as 'التاريخ' FROM patients WHERE name LIKE '%{search}%'", conn)
    
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("لا توجد بيانات حالياً")

elif menu == "الإحصائيات":
    st.header("📊 ملخص العمل")
    df_all = pd.read_sql("SELECT * FROM patients", conn)
    if not df_all.empty:
        st.metric("إجمالي الفحوصات", len(df_all))
        st.bar_chart(df_all['test'].value_counts())
    else:
        st.write("لا توجد بيانات كافية للإحصائيات")
