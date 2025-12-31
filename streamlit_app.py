import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# إعدادات الصفحة
st.set_page_config(page_title="المختبر الذكي Pro", layout="wide", initial_sidebar_state="expanded")

# تصميم CSS لتحسين الواجهة والطباعة
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Tajawal', sans-serif; text-align: right; direction: rtl; }
    .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 10px; text-align: center; }
    .report-box { border: 2px solid #000; padding: 30px; margin: 20px; border-radius: 5px; background: #fff; color: #000; }
    @media print { .no-print { display: none !important; } .report-box { border: none; padding: 0; } }
    </style>
""", unsafe_allow_html=True)

# قاعدة البيانات
conn = sqlite3.connect("pro_lab.db", check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS data 
             (id INTEGER PRIMARY KEY, patient TEXT, test TEXT, result REAL, status TEXT, date TEXT)''')
conn.commit()

# القائمة الجانبية
st.sidebar.title("🧪 قائمة التحكم")
page = st.sidebar.radio("انتقل إلى:", ["لوحة الإحصائيات", "إدخال نتائج", "البحث والتقارير"])

if page == "لوحة الإحصائيات":
    st.title("📊 ملخص العمل اليومي")
    df = pd.read_sql("SELECT * FROM data", conn)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("إجمالي الفحوصات", len(df))
    with col2:
        today = datetime.now().strftime("%Y-%m-%d")
        today_count = len(df[df['date'].str.contains(today)])
        st.metric("فحوصات اليوم", today_count)
    with col3:
        high_risk = len(df[df['status'].str.contains("⚠️")])
        st.metric("نتائج غير طبيعية", high_risk)
    
    st.divider()
    st.subheader("📈 آخر 5 فحوصات مسجلة")
    st.table(df.tail(5)[['patient', 'test', 'result', 'status']])

elif page == "إدخال نتائج":
    st.title("📝 تسجيل فحص جديد")
    with st.form("lab_form", clear_on_submit=True):
        p_name = st.text_input("اسم المريض الثلاثي")
        col1, col2, col3 = st.columns(3)
        with col1:
            t_name = st.selectbox("نوع الفحص", ["Glucose", "HBA1C", "Urea", "Creatinine", "TSH", "CBC"])
        with col2:
            res = st.number_input("النتيجة", step=0.01)
        with col3:
            ref_max = st.number_input("الحد الأعلى الطبيعي", value=100.0)
            
        submit = st.form_submit_button("حفظ النتيجة في السجل")
        
        if submit and p_name:
            status = "طبيعي" if res <= ref_max else "مرتفع ⚠️"
            date_now = datetime.now().strftime("%Y-%m-%d %H:%M")
            c.execute("INSERT INTO data (patient, test, result, status, date) VALUES (?,?,?,?,?)",
                      (p_name, t_name, res, status, date_now))
            conn.commit()
            st.success(f"تم حفظ بيانات {p_name} بنجاح")

elif page == "البحث والتقارير":
    st.title("🔍 البحث وإصدار التقارير")
    search = st.text_input("ادخل اسم المريض للبحث...")
    df = pd.read_sql(f"SELECT * FROM data WHERE patient LIKE '%{search}%'", conn)
    
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        
        selected_patient = st.selectbox("اختر المريض لعرض تقريره القابل للطباعة:", df['patient'].unique())
        if st.button("توليد التقرير الطبي"):
            p_data = df[df['patient'] == selected_patient].iloc[-1]
            st.markdown(f"""
                <div class="report-box">
                    <div style="text-align:center;">
                        <h1>تقرير نتائج مخبرية</h1>
                        <p>تاريخ الإصدار: {p_data['date']}</p>
                    </div>
                    <hr>
                    <p><b>اسم المريض:</b> {p_data['patient']}</p>
                    <p><b>نوع الفحص:</b> {p_data['test']}</p>
                    <p><b>النتيجة:</b> <span style="font-size:20px; color:{'red' if '⚠️' in p_data['status'] else 'green'};">{p_data['result']}</span></p>
                    <p><b>الحالة:</b> {p_data['status']}</p>
                    <br><br>
                    <div style="text-align:left;">
                        <p>توقيع المختبر: _______________</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            st.info("نصيحة: استخدم متصفح التابلت (Print) لتحويل هذا التقرير إلى PDF.")
