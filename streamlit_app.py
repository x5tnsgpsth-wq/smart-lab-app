import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# إعدادات الصفحة والجمالية
st.set_page_config(page_title="نظام المختبر المتكامل", layout="wide")
st.markdown("""
    <style>
    .report-card {
        border: 2px solid #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        background-color: #ffffff;
        text-align: right;
    }
    @media print {
        .no-print { display: none !important; }
    }
    </style>
""", unsafe_allow_html=True)

# قاعدة البيانات
conn = sqlite3.connect("lab_plus.db", check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS tests 
             (id INTEGER PRIMARY KEY, name TEXT, test_type TEXT, result REAL, unit TEXT, min_v REAL, max_v REAL, date TEXT)''')
conn.commit()

# القائمة الجانبية للتنقل
menu = st.sidebar.selectbox("القائمة الرئيسية", ["إضافة نتائج", "سجل الفحوصات", "إصدار تقرير طباعة"])

if menu == "إضافة نتائج":
    st.header("📥 إدخال بيانات الفحص")
    with st.form("input_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("اسم المريض")
            test_type = st.selectbox("نوع الفحص", ["Glucose", "CBC", "Uric Acid", "Cholesterol", "Creatinine"])
            unit = st.text_input("الوحدة (مثل mg/dL)", value="mg/dL")
        with col2:
            res = st.number_input("النتيجة", format="%.2f")
            min_v = st.number_input("الحد الأدنى", value=0.0)
            max_v = st.number_input("الحد الأعلى", value=100.0)
        
        submit = st.form_submit_button("حفظ النتيجة")
        if submit and name:
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            c.execute("INSERT INTO tests (name, test_type, result, unit, min_v, max_v, date) VALUES (?,?,?,?,?,?,?)",
                      (name, test_type, res, unit, min_v, max_v, now))
            conn.commit()
            st.success("تم الحفظ بنجاح!")

elif menu == "سجل الفحوصات":
    st.header("📋 السجل العام")
    df = pd.read_sql("SELECT * FROM tests ORDER BY id DESC", conn)
    st.dataframe(df, use_container_width=True)

elif menu == "إصدار تقرير طباعة":
    st.header("🖨️ قسم الطباعة والتقارير")
    search_name = st.selectbox("اختر اسم المريض لإصدار تقريره", pd.read_sql("SELECT DISTINCT name FROM tests", conn))
    
    if search_name:
        data = pd.read_sql(f"SELECT * FROM tests WHERE name = '{search_name}'", conn)
        for index, row in data.iterrows():
            with st.container():
                st.markdown(f"""
                <div class="report-card">
                    <h2 style="color: #1E88E5;">تقرير مختبر تحليلات مرضية</h2>
                    <hr>
                    <p><b>اسم المريض:</b> {row['name']}</p>
                    <p><b>التاريخ:</b> {row['date']}</p>
                    <table style="width:100%; border-collapse: collapse; margin-top: 10px;">
                        <tr style="background-color: #f8f9fa;">
                            <th style="border: 1px solid #ddd; padding: 8px;">الفحص</th>
                            <th style="border: 1px solid #ddd; padding: 8px;">النتيجة</th>
                            <th style="border: 1px solid #ddd; padding: 8px;">المعدل الطبيعي</th>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 8px;">{row['test_type']}</td>
                            <td style="border: 1px solid #ddd; padding: 8px;">{row['result']} {row['unit']}</td>
                            <td style="border: 1px solid #ddd; padding: 8px;">{row['min_v']} - {row['max_v']}</td>
                        </tr>
                    </table>
                </div>
                """, unsafe_allow_html=True)
                st.button(f"طباعة تقرير {row['id']}", on_click=lambda: st.write("اضغط Ctrl+P للطباعة"))

