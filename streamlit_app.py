import streamlit as st
import pandas as pd
import os
from datetime import datetime
import time
import random

# 1. إعدادات الصفحة
st.set_page_config(page_title="Pro Lab System", page_icon="🔬", layout="wide")

# 2. إدارة الجلسة (Session State)
if 'auth_status' not in st.session_state:
    st.session_state.auth_status = None  # None, 'guest', 'logged_in'
if 'otp_sent' not in st.session_state:
    st.session_state.otp_sent = False
if 'generated_otp' not in st.session_state:
    st.session_state.generated_otp = None

# --- واجهة الدخول والاختيار ---
def login_screen():
    st.markdown("""
        <style>
        .stApp { background: #0f172a; }
        .main-card {
            background: #1e293b; padding: 40px; border-radius: 20px;
            text-align: center; color: white; border: 1px solid #334155;
        }
        .stButton>button { border-radius: 10px; height: 50px; font-weight: bold; }
        </style>
        <div class="main-card">
            <h1 style='font-size: 50px;'>🔬</h1>
            <h2>مرحباً بك في نظام المختبر الذكي</h2>
            <p style='color: #94a3b8;'>يرجى اختيار طريقة الدخول للمتابعة</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    
    # خيار الزائر
    with col1:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("👤 الدخول كـ زائر", use_container_width=True):
            st.session_state.auth_status = 'guest'
            st.rerun()

    # خيار تسجيل الدخول
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("🔐 تسجيل دخول (أعضاء)", expanded=st.session_state.otp_sent):
            if not st.session_state.otp_sent:
                contact = st.text_input("البريد الإلكتروني أو رقم الهاتف")
                if st.button("إرسال رمز التأكيد"):
                    if contact:
                        # محاكاة إرسال الرمز
                        st.session_state.generated_otp = str(random.randint(1000, 9999))
                        st.session_state.otp_sent = True
                        st.session_state.user_contact = contact
                        st.info(f"تم إرسال الرمز (تجريبي): {st.session_state.generated_otp}")
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error("يرجى إدخال البيانات")
            else:
                st.write(f"الرمز أُرسل إلى: {st.session_state.user_contact}")
                otp_input = st.text_input("أدخل الرمز المكون من 4 أرقام")
                if st.button("تأكيد الرمز والدخول"):
                    if otp_input == st.session_state.generated_otp:
                        st.session_state.auth_status = 'logged_in'
                        st.success("تم التحقق بنجاح")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("الرمز غير صحيح")
                if st.button("إلغاء"):
                    st.session_state.otp_sent = False
                    st.rerun()

# --- تشغيل منطق البرنامج ---
if st.session_state.auth_status is None:
    login_screen()
else:
    # تحديد ملف البيانات بناءً على نوع المستخدم
    if st.session_state.auth_status == 'guest':
        DB_FILE = "data_guest_temp.csv"
        user_label = "زائر"
    else:
        # ملف خاص لكل مستخدم بناءً على بريده أو هاتفه
        clean_contact = "".join(filter(str.isalnum, st.session_state.user_contact))
        DB_FILE = f"db_{clean_contact}.csv"
        user_label = st.session_state.user_contact

    # تحميل البيانات
    if 'df' not in st.session_state:
        st.session_state.df = pd.read_csv(DB_FILE) if os.path.exists(DB_FILE) else pd.DataFrame(columns=["التاريخ", "المريض", "الفحص", "النتيجة", "الحالة"])

    # الواجهة الرئيسية
    st.markdown(f"""
        <style>
        .stApp {{ background-color: #f1f5f9 !important; }}
        .header {{
            background: white; padding: 20px; border-radius: 15px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05); margin-bottom: 20px;
            border-right: 5px solid #2563eb; display: flex; justify-content: space-between;
        }}
        </style>
        <div class="header">
            <div>
                <h2 style="margin:0;">🔬 مختبر التحليلات</h2>
                <p style="color: #64748b; margin:0;">حساب: {user_label}</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.write(f"نوع الدخول: **{st.session_state.auth_status}**")
        if st.button("تسجيل الخروج 🚪"):
            for key in list(st.session_state.keys()): del st.session_state[key]
            st.rerun()

    # التبويبات
    t1, t2 = st.tabs(["📝 العمليات", "📂 أرشيف البيانات"])

    with t1:
        if st.session_state.auth_status == 'guest':
            st.warning("⚠️ تنبيه: أنت تدخل كزائر. البيانات التي تدخلها قد تظهر لزوار آخرين أو تُمسح دورياً.")
        
        with st.form("main_form"):
            c1, c2 = st.columns(2)
            name = c1.text_input("اسم المريض")
            test = c1.selectbox("الفحص", ["Glucose", "CBC", "Urea"])
            res = c2.number_input("النتيجة", format="%.2f")
            phone = c2.text_input("الهاتف")
            
            if st.form_submit_button("حفظ البيانات"):
                new_row = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), name, test, res, "طبيعي"]], 
                                      columns=st.session_state.df.columns)
                st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
                st.session_state.df.to_csv(DB_FILE, index=False)
                st.success("تم الحفظ بنجاح!")

    with t2:
        st.markdown(f"### سجلات {user_label}")
        if not st.session_state.df.empty:
            st.dataframe(st.session_state.df, use_container_width=True)
        else:
            st.info("لا توجد سجلات حالياً.")
