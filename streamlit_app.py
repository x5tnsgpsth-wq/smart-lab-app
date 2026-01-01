import streamlit as st
import pandas as pd
import os
import random
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# --- 1. إعدادات المنصة الاحترافية ---
st.set_page_config(page_title="BioLab Pro | Enterprise Edition", page_icon="🧬", layout="wide")

# إعدادات خادم البريد (SMTP)
# ملاحظة: ضع بياناتك الحقيقية هنا ليعمل الإرسال
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "your-email@gmail.com"  # بريدك الإلكتروني
SENDER_PASSWORD = "your-app-password"  # كلمة مرور التطبيقات من جوجل

# دالة إرسال البريد الإلكتروني الحقيقية
def send_otp_email(receiver_email, otp_code):
    try:
        msg = MIMEMultipart()
        msg['From'] = f"BioLab Pro Security <{SENDER_EMAIL}>"
        msg['To'] = receiver_email
        msg['Subject'] = "Your BioLab Security Code"

        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; text-align: center; color: #333;">
                <div style="padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                    <h2 style="color: #2563eb;">BioLab Pro Authentication</h2>
                    <p>Your security code to access the lab system is:</p>
                    <h1 style="background: #f1f5f9; padding: 10px; border-radius: 5px; letter-spacing: 5px;">{otp_code}</h1>
                    <p style="font-size: 0.8rem; color: #666;">This code will expire shortly. Do not share it with anyone.</p>
                </div>
            </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        st.error(f"فشل في إرسال البريد: {str(e)}")
        return False

# CSS مخصص للواجهة العصري
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .auth-card { background: white; padding: 3rem; border-radius: 20px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); text-align: center; border-top: 6px solid #2563eb; }
    .stButton>button { border-radius: 8px; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# --- 2. إدارة الجلسة ---
if 'step' not in st.session_state: st.session_state.step = 'gate'
if 'user_type' not in st.session_state: st.session_state.user_type = None
if 'email' not in st.session_state: st.session_state.email = ""

# --- 3. بوابة الدخول ---
def show_gate():
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("""<div class="auth-card"><h1>BioLab <span style='color: #2563eb;'>Pro</span></h1><p>نظام إدارة البيانات المخبرية السحابي</p></div>""", unsafe_allow_html=True)
        st.write("")
        c1, c2 = st.columns(2)
        if c1.button("👤 أنا زائر", use_container_width=True):
            st.session_state.user_type, st.session_state.user_id, st.session_state.step = 'guest', 'Guest_User', 'app'
            st.rerun()
        if c2.button("🔐 تسجيل دخول الأعضاء", use_container_width=True):
            st.session_state.step = 'otp_request'
            st.rerun()

# --- 4. نظام التحقق بالبريد الفعلي ---
def show_otp_logic():
    _, col, _ = st.columns([1, 1, 1])
    with col:
        if st.session_state.step == 'otp_request':
            st.subheader("تسجيل الدخول")
            email = st.text_input("أدخل بريدك الإلكتروني لاستلام الرمز", placeholder="example@mail.com")
            if st.button("إرسال رمز التحقق إلى بريدي"):
                if email and "@" in email:
                    with st.spinner('جاري الاتصال بخادم البريد وإرسال الرمز...'):
                        otp = str(random.randint(100000, 999999))
                        if send_otp_email(email, otp):
                            st.session_state.otp = otp
                            st.session_state.email = email
                            st.session_state.step = 'otp_verify'
                            st.success("تم إرسال الرمز بنجاح! تفقد بريدك الوارد.")
                            time.sleep(1.5)
                            st.rerun()
                else: st.warning("يرجى إدخال بريد إلكتروني صحيح")
        
        elif st.session_state.step == 'otp_verify':
            st.subheader("التحقق من البريد")
            st.info(f"الرمز أُرسل إلى: {st.session_state.email}")
            otp_input = st.text_input("أدخل الرمز المكون من 6 أرقام")
            if st.button("تأكيد ودخول"):
                if otp_input == st.session_state.otp:
                    st.session_state.user_type, st.session_state.user_id, st.session_state.step = 'member', st.session_state.email, 'app'
                    st.rerun()
                else: st.error("الرمز غير صحيح")
            if st.button("رجوع"):
                st.session_state.step = 'gate'
                st.rerun()

# --- 5. لوحة التحكم (الدوال الأصلية مع ربط البيانات) ---
def show_app():
    st.markdown(f'<div style="background: white; padding: 15px; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); display: flex; justify-content: space-between;"><b>🔬 BioLab Pro</b><span>👤 {st.session_state.user_id} ({st.session_state.user_type})</span></div>', unsafe_allow_html=True)
    
    safe_name = "".join(x for x in st.session_state.user_id if x.isalnum())
    db_path = f"store_{safe_name}.csv"
    
    if 'data' not in st.session_state:
        st.session_state.data = pd.read_csv(db_path) if os.path.exists(db_path) else pd.DataFrame(columns=["التاريخ", "المريض", "الفحص", "النتيجة", "الحالة"])

    tab1, tab2 = st.tabs(["📊 السجلات", "➕ إضافة فحص"])
    with tab1:
        st.dataframe(st.session_state.data, use_container_width=True)
    with tab2:
        with st.form("entry"):
            name = st.text_input("اسم المريض")
            test = st.selectbox("الفحص", ["Glucose", "CBC", "HbA1c"])
            res = st.number_input("النتيجة")
            if st.form_submit_button("حفظ"):
                new = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), name, test, res, "Normal"]], columns=st.session_state.data.columns)
                st.session_state.data = pd.concat([st.session_state.data, new], ignore_index=True)
                st.session_state.data.to_csv(db_path, index=False)
                st.success("تم الحفظ!")

    if st.sidebar.button("خروج"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()

# --- التوجيه ---
if st.session_state.step == 'gate': show_gate()
elif st.session_state.step in ['otp_request', 'otp_verify']: show_otp_logic()
elif st.session_state.step == 'app': show_app()
