import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import urllib.parse

# إعداد الصفحة
st.set_page_config(page_title="مختبرك الذكي - النسخة الشاملة", layout="wide")
st.markdown("""<style> * { direction: rtl; text-align: right; } .stButton>button { width: 100%; } </style>""", unsafe_allow_html=True)

# قاعدة البيانات
conn = sqlite3.connect("lab_final_v4.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS patients 
               (id INTEGER PRIMARY KEY, name TEXT, contact TEXT, test TEXT, result REAL, status TEXT, date TEXT)""")
conn.commit()

# القائمة الجانبية
menu = st.sidebar.selectbox("القائمة", ["إدخال بيانات", "السجل والإرسال"])

if menu == "إدخال بيانات":
    st.header("📝 تسجيل فحص جديد")
    with st.form("entry_form"):
        name = st.text_input("اسم المريض")
        contact = st.text_input("رقم الهاتف أو معرّف التليجرام (بدون @)")
        test = st.selectbox("نوع الفحص", ["Glucose", "HbA1c", "Urea", "Creatinine"])
        res = st.number_input("النتيجة")
        
        if st.form_submit_button("حفظ البيانات"):
            if name and contact:
                status = "طبيعي" if res < 120 else "مرتفع ⚠️"
                dt = datetime.now().strftime("%Y-%m-%d %H:%M")
                cursor.execute("INSERT INTO patients (name, contact, test, result, status, date) VALUES (?,?,?,?,?,?)", 
                               (name, contact, test, res, status, dt))
                conn.commit()
                st.success(f"تم الحفظ بنجاح")

else:
    st.header("🔍 سجل المرضى")
    df = pd.read_sql("SELECT * FROM patients", conn)
    
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        st.divider()
        
        selected_p = st.selectbox("اختر مريضاً لإرسال نتيجته:", df['name'].unique())
        
        if selected_p:
            p_info = df[df['name'] == selected_p].iloc[-1]
            
            # نص الرسالة
            raw_msg = f"مرحباً {p_info['name']}، نتيجتك لفحص {p_info['test']} هي {p_info['result']} ({p_info['status']})."
            msg_encoded = urllib.parse.quote(raw_msg)
            
            st.subheader(f"إرسال إلى: {p_info['name']}")
            col1, col2 = st.columns(2)
            
            with col1:
                # زر واتساب
                wa_url = f"https://wa.me/{p_info['contact']}?text={msg_encoded}"
                st.markdown(f'''<a href="{wa_url}" target="_blank" style="text-decoration:none;">
                    <div style="background-color:#25D366; color:white; padding:15px; border-radius:10px; text-align:center; font-weight:bold;">
                        📱 واتساب (رقم هاتف)
                    </div></a>''', unsafe_allow_html=True)

            with col2:
                # زر تليجرام (تم تحديث الرابط ليعمل كـ Share لضمان وصول النص)
                # إذا كان contact يبدأ برقم فهو سيبحث عن الرقم، وإذا كان نصاً سيبحث عن المعرف
                tg_url = f"https://t.me/share/url?url={msg_encoded}&text={p_info['contact']}"
                # رابط بديل للمعرف المباشر:
                tg_direct = f"https://t.me/{p_info['contact']}"
                
                st.markdown(f'''<a href="{tg_url}" target="_blank" style="text-decoration:none;">
                    <div style="background-color:#0088cc; color:white; padding:15px; border-radius:10px; text-align:center; font-weight:bold;">
                        ✈️ تليجرام (رقم أو معرف)
                    </div></a>''', unsafe_allow_html=True)
