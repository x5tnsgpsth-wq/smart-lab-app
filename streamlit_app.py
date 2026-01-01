import streamlit as st
import pandas as pd
import os
import random
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# --- 1. إعدادات المنصة ---
st.set_page_config(page_title="BioLab Pro | Enterprise", page_icon="🧬", layout="wide")

# ⚠️ أدخل بياناتك هنا ليعمل إرسال البريد الحقيقي
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "your-email@gmail.com"        # بريدك الإلكتروني
SENDER_PASSWORD = "xxxx xxxx xxxx xxxx"      # الرمز المكون من 16 حرفاً الذي حصلت عليه

# دالة إرسال البريد الإلكتروني
def send_otp_email(receiver_email, otp_code):
    try:
        msg = MIMEMultipart()
        msg['From'] = f"BioLab Pro Security <{SENDER_EMAIL}>"
        msg['To'] = receiver_email
        msg['Subject'] = "كود التحقق الخاص بك - BioLab Pro"

        body = f"""
        <div style="font-family: Arial, sans-serif; text-align: center; border: 1px solid #e2e8f0; padding: 40px; border-radius: 15px;">
            <h2 style="color: #2563eb;">مرحباً بك في BioLab Pro</h2>
            <p style="color: #475569;">كود التحقق الخاص بدخولك هو:</p>
            <div style="background: #f1f5f9; padding: 20px; border-radius: 10px; font-size: 32px; font-weight: bold; letter-spacing: 10px; color: #1e293b;">
                {otp_code}
            </div>
            <p style="color: #94a3b8; font-size: 12px; margin-top: 20px;">هذا الكود صالح لمدة 10 دقائق. يرجى عدم مشاركته مع أحد.</p>
        </div>
        """
        msg.attach(MIMEText(body, 'html'))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        st.error(f"حدث خطأ أثناء الإرسال: {e}")
        return False

# CSS للواجهة الاحترافية
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .auth-card { background: white; padding: 3rem; border-radius: 20px; box-shadow: 0 10px 15px rgba(0,0,0,0.05); text-align: center; border-top: 6px solid #2563eb; }
    .main-header { background: white; padding: 1rem 2rem; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; }
    </style>
""", unsafe_allow_html=True)

# --- 2. إدارة منطق التنقل ---
if 'step' not in st.session_state: st.session_state.step = 'gate'
if 'user_id' not in st.session_state: st.session_state.user_id = None

# --- 3. الصفحات ---

def show_gate():
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown('<div class="auth-card"><h1>BioLab <span style="color:#2563eb">Pro</span></h1><p>منصة المختبرات السحابية المؤمّنة</p></div>', unsafe_allow_html=True)
        st.write("")
        if st.button("👤 الدخول كزائر (بدون حفظ)", use_container_width=True):
            st.session_state.user_id, st.session_state.step = "Guest_User", "app"
            st.rerun()
        if st.button("🔐 تسجيل دخول الأعضاء (البريد الإلكتروني)", use_container_width=True):
            st.session_state.step = "otp_request"
            st.rerun()

def show_login():
    _, col, _ = st.columns([1, 1, 1])
    with col:
        if st.session_state.step == "otp_request":
            email = st.text_input("البريد الإلكتروني")
            if st.button("إرسال رمز OTP"):
                if email and "@" in email:
                    otp = str(random.randint(100000, 999999))
                    with st.spinner("جاري إرسال الرمز..."):
                        if send_otp_email(email, otp):
                            st.session_state.otp, st.session_state.temp_email, st.session_state.step = otp, email, "otp_verify"
                            st.success("أرسلنا الرمز إلى بريدك!")
                            time.sleep(1)
                            st.rerun()
                else: st.warning("يرجى إدخال بريد صحيح")
        
        elif st.session_state.step == "otp_verify":
            st.write(f"الرمز أُرسل إلى: **{st.session_state.temp_email}**")
            otp_in = st.text_input("أدخل الرمز المكون من 6 أرقام")
            if st.button("تأكيد الدخول"):
                if otp_in == st.session_state.otp:
                    st.session_state.user_id, st.session_state.step = st.session_state.temp_email, "app"
                    st.rerun()
                else: st.error("الرمز غير صحيح")

def show_main_app():
    # الهيدر العلوي
    st.markdown(f'<div class="main-header"><div><h3 style="margin:0;">🧬 لوحة التحكم</h3></div><div style="color:#64748b">مرحباً: <b>{st.session_state.user_id}</b></div></div>', unsafe_allow_html=True)
    
    # عزل البيانات
    safe_db_name = "".join(x for x in st.session_state.user_id if x.isalnum())
    db_file = f"db_{safe_db_name}.csv"
    
    if 'data' not in st.session_state:
        st.session_state.data = pd.read_csv(db_file) if os.path.exists(db_file) else pd.DataFrame(columns=["التاريخ", "المريض", "الفحص", "النتيجة"])

    t1, t2 = st.tabs(["📊 البيانات", "➕ إضافة"])
    
    with t1:
        st.dataframe(st.session_state.data, use_container_width=True)
    
    with t2:
        with st.form("add"):
            c1, c2 = st.columns(2)
            name = c1.text_input("اسم المريض")
            test = c2.selectbox("الفحص", ["Glucose", "HbA1c", "CBC"])
            res = st.number_input("النتيجة")
            if st.form_submit_button("حفظ"):
                new_row = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), name, test, res]], columns=st.session_state.data.columns)
                st.session_state.data = pd.concat([st.session_state.data, new_row], ignore_index=True)
                st.session_state.data.to_csv(db_file, index=False)
                st.success("تم الحفظ بنجاح!")
                st.rerun()

    if st.sidebar.button("تسجيل الخروج 🚪"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()

# --- التوجيه ---
if st.session_state.step == 'gate': show_gate()
elif st.session_state.step in ['otp_request', 'otp_verify']: show_login()
elif st.session_state.step == 'app': show_main_app()
