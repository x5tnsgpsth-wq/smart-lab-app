import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# إعداد الصفحة
st.set_page_config(page_title="نظام المختبر الذكي", layout="wide")

# تصميم بسيط للتقرير (CSS)
st.markdown("""
    <style>
    .report-style {
        border: 2px solid #333;
        padding: 25px;
        border-radius: 10px;
        background-color: #f9f9f9;
        direction: rtl;
        text-align: right;
    }
    </style>
""", unsafe_allow_html=True)

# قاعدة البيانات
conn = sqlite3.connect("lab_final.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS patients (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, test TEXT, result REAL, status TEXT, date TEXT)")
conn.commit()

# القائمة الجانبية
menu = st.sidebar.selectbox("القائمة", ["إدخال بيانات", "السجل والطباعة"])

if menu == "إدخال بيانات":
    st.header("📝 تسجيل فحص")
    with st.form("entry_form"):
        name = st.text_input("اسم المريض")
        test = st.selectbox("الفحص", ["Glucose", "HbA1c", "Urea", "Creatinine"])
        res = st.number_input("النتيجة")
        if st.form_submit_button("حفظ"):
            status = "طبيعي" if res < 120 else "مرتفع ⚠️"
            dt = datetime.now().strftime("%Y-%m-%d %H:%M")
            cursor.execute("INSERT INTO patients (name, test, result, status, date) VALUES (?,?,?,?,?)", (name, test, res, status, dt))
            conn.commit()
            st.success("تم الحفظ!")

else:
    st.header("🔍 السجل وإصدار التقارير")
    df = pd.read_sql("SELECT * FROM patients", conn)
    
    if not df.empty:
        # جدول البحث
        st.dataframe(df[['name', 'test', 'result', 'status', 'date']], use_container_width=True)
        
        st.divider()
        
        # اختيار مريض للطباعة
        patient_to_print = st.selectbox("اختر مريضاً لعرض تقريره:", df['name'].unique())
        
        if st.button("توليد التقرير"):
            p_info = df[df['name'] == patient_to_print].iloc[-1]
            st.markdown(f"""
                <div class="report-style">
                    <h2 style="text-align:center;">تقرير مختبر التحليلات المرضية</h2>
                    <hr>
                    <p><b>اسم المريض:</b> {p_info['name']}</p>
                    <p><b>التاريخ:</b> {p_info['date']}</p>
                    <p><b>نوع الفحص:</b> {p_info['test']}</p>
                    <p><b>النتيجة:</b> <span style="font-size:24px; color:{"red" if "⚠️" in p_info['status'] else "green"};">{p_info['result']}</span></p>
                    <p><b>الحالة:</b> {p_info['status']}</p>
                    <br>
                    <p style="text-align:left;">توقيع المختبر: ........................</p>
                </div>
            """, unsafe_allow_html=True)
            st.info("💡 يمكنك الآن تصوير الشاشة أو استخدام أمر الطباعة في التابلت لحفظ التقرير.")
