import streamlit as st
import pandas as pd
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import random
import time

# --- 1. إعدادات النظام المتقدمة ---
st.set_page_config(page_title="Professional Lab OS", page_icon="🔬", layout="wide")

# إعدادات البريد (تحتاج لإدخال بياناتك هنا ليعمل الإرسال الحقيقي)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "your-email@gmail.com"  # بريدك
SENDER_PASSWORD = "your-app-password"  # كلمة مرور التطبيقات من جوجل

def send_otp_email(receiver_email, otp_code):
    try:
        msg = MIMEText(f"كود التحقق الخاص بك للدخول إلى نظام المختبر هو: {otp_code}")
        msg['Subject'] = 'كود التحقق OTP'
        msg['From'] = SENDER_EMAIL
        msg['To'] = receiver_email
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        return False

# --- 2. إدارة حالة الجلسة ---
if 'page' not in st.session_state: st.session_state.page = 'gate'
if 'user_type' not in st.session_state: st.session_state.user_type = None # guest or member
if 'user_id' not in st.session_state: st.session_state.user_id = None
if 'otp_verified' not in st.session_state: st.session_state.otp_verified = False

# --- 3. واجهة بوابة الدخول (The Gate) ---
def show_gate():
    st.markdown("""
        <style>
        .stApp { background: linear-gradient(to bottom, #f8fafc, #e2e8f0); }
        .gate-card {
            background: white; padding: 50px; border-radius: 25px;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
            text-align: center; border-top: 8px solid #2563eb;
        }
        </style>
    """, unsafe_allow_html=True)
    
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown("""
            <div class="gate-card">
                <h1 style='color: #1e293b;'>🔬 Professional Lab System</h1>
                <p style='color: #64748b;'>نظام الإدارة المخبرية المتكامل - يرجى تحديد نوع الوصول</p>
            </div>
        """, unsafe_allow_html=True)
        st.write("")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("👤 الدخول كزائر", use_container_width=True):
                st.session_state.user_type = 'guest'
                st.session_state.user_id = 'public_guest'
                st.session_state.page = 'main'
                st.rerun()
                
        with c2:
            if st.button("🔐 تسجيل دخول الأعضاء", use_container_width=True):
                st.session_state.page = 'login'
                st.rerun()

# --- 4. واجهة التحقق بالبريد (OTP Login) ---
def show_login():
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.subheader("تسجيل دخول الأعضاء")
        email = st.text_input("أدخل البريد الإلكتروني الخاص بك")
        
        if 'generated_otp' not in st.session_state:
            if st.button("إرسال رمز التحقق OTP"):
                if email:
                    otp = str(random.randint(100000, 999999))
                    st.session_state.generated_otp = otp
                    st.session_state.temp_email = email
                    # ملاحظة: إذا لم تضع بيانات SMTP حقيقية، سيظهر الرمز هنا للتجربة
                    if send_otp_email(email, otp):
                        st.success("تم إرسال الرمز لبريدك الحقيقي")
                    else:
                        st.warning(f"فشل الإرسال التلقائي. الرمز التجريبي هو: {otp}")
                else: st.error("يرجى كتابة البريد")
        
        else:
            otp_in = st.text_input("أدخل الرمز الذي استلمته")
            if st.button("تأكيد الرمز"):
                if otp_in == st.session_state.generated_otp:
                    st.session_state.user_type = 'member'
                    st.session_state.user_id = st.session_state.temp_email
                    st.session_state.page = 'main'
                    st.rerun()
                else: st.error("الرمز غير صحيح")
            if st.button("إعادة إرسال"):
                del st.session_state.generated_otp
                st.rerun()

# --- 5. واجهة البرنامج الرئيسية ---
def show_main():
    # تصميم احترافي للرأس
    st.markdown(f"""
        <div style="background: white; padding: 20px; border-radius: 15px; border-bottom: 4px solid #2563eb; display: flex; justify-content: space-between; align-items: center;">
            <h2 style="margin:0;">🔬 لوحة تحكم المختبر</h2>
            <div style="text-align: left;">
                <span style="background: #dbeafe; color: #1e40af; padding: 5px 15px; border-radius: 20px; font-weight: bold;">
                    👤 {st.session_state.user_id}
                </span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # عزل البيانات: كل مستخدم له ملفه الخاص تماماً
    user_db = f"data_{st.session_state.user_id.replace('@', '_').replace('.', '_')}.csv"
    if 'df' not in st.session_state:
        st.session_state.df = pd.read_csv(user_db) if os.path.exists(user_db) else pd.DataFrame(columns=["التاريخ", "المريض", "الفحص", "النتيجة"])

    # المحتوى التفاعلي
    tab1, tab2 = st.tabs(["📝 إدخال جديد", "📋 السجلات الخاصة"])
    
    with tab1:
        with st.form("lab_form"):
            c1, c2 = st.columns(2)
            name = c1.text_input("اسم المريض")
            test = c2.selectbox("نوع التحليل", ["Glucose", "HbA1c", "CBC"])
            res = c1.number_input("النتيجة", step=0.01)
            if st.form_submit_button("حفظ البيانات"):
                new_data = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), name, test, res]], columns=st.session_state.df.columns)
                st.session_state.df = pd.concat([st.session_state.df, new_data], ignore_index=True)
                st.session_state.df.to_csv(user_db, index=False)
                st.success("تم الحفظ في مساحتك الخاصة")

    with tab2:
        st.dataframe(st.session_state.df, use_container_width=True)

    if st.sidebar.button("تسجيل الخروج 🚪"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()

# --- التوجيه (Routing) ---
if st.session_state.page == 'gate': show_gate()
elif st.session_state.page == 'login': show_login()
elif st.session_state.page == 'main': show_main()
