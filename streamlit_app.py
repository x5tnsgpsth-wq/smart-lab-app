import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import urllib.parse

# إعداد الصفحة
st.set_page_config(page_title="مختبرك الذكي المطور", layout="wide")

# تصميم الواجهة
st.markdown("""<style> * { direction: rtl; text-align: right; font-family: 'Arial'; } </style>""", unsafe_allow_html=True)

# قاعدة البيانات
conn = sqlite3.connect("lab_final_v2.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS patients 
               (id INTEGER PRIMARY KEY, name TEXT, phone TEXT, test TEXT, result REAL, status TEXT, date TEXT)""")
conn.commit()

# القائمة الجانبية
menu = st.sidebar.selectbox("القائمة", ["إدخال بيانات", "السجل وإرسال النتائج"])

if menu == "إدخال بيانات":
    st.header("📝 تسجيل فحص جديد")
    with st.form("entry_form"):
        name = st.text_input("اسم المريض")
        phone = st.text_input("رقم الواتساب (مثال: 9647XXXXXXXX)")
        test = st.selectbox("نوع الفحص", ["Glucose", "HbA1c", "Urea", "Creatinine", "Vitamin D"])
        res = st.number_input("النتيجة")
        
        if st.form_submit_button("حفظ النتيجة"):
            if name and phone:
                status = "طبيعي" if res < 120 else "مرتفع ⚠️"
                dt = datetime.now().strftime("%Y-%m-%d %H:%M")
                cursor.execute("INSERT INTO patients (name, phone, test, result, status, date) VALUES (?,?,?,?,?,?)", 
                               (name, phone, test, res, status, dt))
                conn.commit()
                st.success(f"تم حفظ بيانات {name} بنجاح!")
            else:
                st.error("يرجى إدخال الاسم ورقم الهاتف")

else:
    st.header("🔍 سجل المرضى وإرسال النتائج")
    df = pd.read_sql("SELECT * FROM patients", conn)
    
    if not df.empty:
        st.dataframe(df[['name', 'phone', 'test', 'result', 'status', 'date']], use_container_width=True)
        
        st.divider()
        st.subheader("📤 إرسال النتيجة للمريض")
        selected_p = st.selectbox("اختر المريض:", df['name'].unique())
        
        if selected_p:
            p_info = df[df['name'] == selected_p].iloc[-1]
            
            # تجهيز رسالة الواتساب
            msg = f"""أهلاً {p_info['name']}، 
نتيجتك في فحص {p_info['test']} هي: {p_info['result']}
الحالة: {p_info['status']}
تاريخ الفحص: {p_info['date']}
شكراً لثقتك بمختبرنا."""
            
            msg_encoded = urllib.parse.quote(msg)
            # رابط الواتساب الرسمي
            whatsapp_url = f"https://wa.me/{p_info['phone']}?text={msg_encoded}"
            
            st.markdown(f'<a href="{whatsapp_url}" target="_blank" style="background-color: #25D366; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">📱 إرسال النتيجة عبر WhatsApp</a>', unsafe_allow_html=True)

   
