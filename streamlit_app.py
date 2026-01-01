import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import urllib.parse

# إعداد الصفحة
st.set_page_config(page_title="مختبرك الذكي - تليجرام وواتساب", layout="wide")
st.markdown("""<style> * { direction: rtl; text-align: right; font-family: 'Arial'; } </style>""", unsafe_allow_html=True)

# قاعدة البيانات
conn = sqlite3.connect("lab_final_v3.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS patients 
               (id INTEGER PRIMARY KEY, name TEXT, contact_info TEXT, contact_type TEXT, test TEXT, result REAL, status TEXT, date TEXT)""")
conn.commit()

# القائمة الجانبية
menu = st.sidebar.selectbox("القائمة", ["إدخال بيانات", "السجل وإرسال النتائج"])

if menu == "إدخال بيانات":
    st.header("📝 تسجيل فحص جديد")
    with st.form("entry_form"):
        name = st.text_input("اسم المريض")
        contact_type = st.radio("وسيلة التواصل المفضلة", ["رقم هاتف", "معرّف تليجرام (Username)"])
        contact_info = st.text_input("أدخل الرقم (مع رمز الدولة) أو المعرّف (بدون @)")
        test = st.selectbox("نوع الفحص", ["Glucose", "HbA1c", "Urea", "Creatinine"])
        res = st.number_input("النتيجة")
        
        if st.form_submit_button("حفظ النتيجة"):
            if name and contact_info:
                status = "طبيعي" if res < 120 else "مرتفع ⚠️"
                dt = datetime.now().strftime("%Y-%m-%d %H:%M")
                cursor.execute("INSERT INTO patients (name, contact_info, contact_type, test, result, status, date) VALUES (?,?,?,?,?,?,?)", 
                               (name, contact_info, contact_type, test, res, status, dt))
                conn.commit()
                st.success(f"تم حفظ بيانات {name}")
            else:
                st.error("يرجى إكمال البيانات")

else:
    st.header("🔍 السجل وإرسال النتائج")
    df = pd.read_sql("SELECT * FROM patients", conn)
    
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        st.divider()
        selected_p = st.selectbox("اختر المريض:", df['name'].unique())
        
        if selected_p:
            p_info = df[df['name'] == selected_p].iloc[-1]
            msg = f"النتيجة لـ {p_info['name']}: {p_info['test']} = {p_info['result']} ({p_info['status']})"
            msg_encoded = urllib.parse.quote(msg)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # رابط واتساب (يعمل بالرقم فقط)
                if "رقم" in p_info['contact_type']:
                    wa_url = f"https://wa.me/{p_info['contact_info']}?text={msg_encoded}"
                    st.markdown(f'<a href="{wa_url}" target="_blank" style="background-color: #25D366; color: white; padding: 15px; text-decoration: none; border-radius: 10px; display: block; text-align: center;">📱 إرسال WhatsApp</a>', unsafe_allow_html=True)
                else:
                    st.warning("هذا المريض مسجل بمعرّف تليجرام فقط")

            with col2:
                # رابط تليجرام (يعمل بالمعرّف أو الرقم)
                tg_url = f"https://t.me/{p_info['contact_info']}?text={msg_encoded}"
                st.markdown(f'<a href="{tg_url}" target="_blank" style="background-color: #0088cc; color: white; padding: 15px; text-decoration: none; border-radius: 10px; display: block; text-align: center;">✈️ إرسال Telegram</a>', unsafe_allow_html=True)
