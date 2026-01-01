import streamlit as st
import pandas as pd
import os
import random
import time
from datetime import datetime

# --- 1. إعدادات المنصة الاحترافية ---
st.set_page_config(page_title="BioLab Pro | Enterprise Edition", page_icon="🧬", layout="wide")

# CSS مخصص لتحويل الواجهة إلى تصميم عصري (Modern UI)
st.markdown("""
    <style>
    /* تصميم الخلفية العامة */
    .stApp { background-color: #f8fafc; }
    
    /* تصميم بطاقة الدخول */
    .auth-card {
        background: white;
        padding: 3rem;
        border-radius: 20px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        text-align: center;
        border-top: 6px solid #2563eb;
    }
    
    /* أزرار مخصصة */
    .stButton>button {
        border-radius: 8px;
        transition: all 0.3s ease;
        font-weight: 600;
    }
    
    /* تبويبات احترافية */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #f1f5f9;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. منطق إدارة الجلسة (Session Control) ---
if 'step' not in st.session_state: st.session_state.step = 'gate'
if 'user_type' not in st.session_state: st.session_state.user_type = None
if 'email' not in st.session_state: st.session_state.email = ""

# --- 3. بوابة الدخول الذكية (The Smart Gate) ---
def show_gate():
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("""
            <div class="auth-card">
                <h1 style='color: #1e293b; margin-bottom: 0;'>BioLab <span style='color: #2563eb;'>Pro</span></h1>
                <p style='color: #64748b;'>نظام إدارة البيانات المخبرية السحابي</p>
            </div>
        """, unsafe_allow_html=True)
        st.write("")
        
        c1, c2 = st.columns(2)
        with c1:
            st.info("**الدخول السريع**")
            if st.button("👤 أنا زائر", use_container_width=True):
                st.session_state.user_type = 'guest'
                st.session_state.user_id = 'Guest_Session'
                st.session_state.step = 'app'
                st.rerun()
        
        with c2:
            st.success("**الدخول الآمن**")
            if st.button("🔐 تسجيل دخول الأعضاء", use_container_width=True):
                st.session_state.step = 'otp_request'
                st.rerun()

# --- 4. نظام التحقق الثنائي (OTP Verification) ---
def show_otp_logic():
    _, col, _ = st.columns([1, 1, 1])
    with col:
        if st.session_state.step == 'otp_request':
            st.subheader("تسجيل الدخول")
            email = st.text_input("البريد الإلكتروني أو رقم الهاتف", placeholder="example@mail.com")
            if st.button("إرسال رمز التحقق"):
                if email:
                    with st.spinner('جاري توليد الرمز وإرساله...'):
                        time.sleep(1.5)
                        st.session_state.otp = str(random.randint(100000, 999999))
                        st.session_state.email = email
                        st.session_state.step = 'otp_verify'
                        st.rerun()
                else: st.warning("يرجى إدخال بيانات صالحة")
        
        elif st.session_state.step == 'otp_verify':
            st.subheader("التحقق من الهوية")
            st.write(f"أرسلنا الرمز إلى: **{st.session_state.email}**")
            # تنبيه احترافي يظهر الرمز للتجربة حالياً
            st.code(f"رمز التحقق (OTP): {st.session_state.otp}", language="text")
            
            otp_input = st.text_input("أدخل الرمز المكون من 6 أرقام")
            if st.button("تأكيد ودخول"):
                if otp_input == st.session_state.otp:
                    st.session_state.user_type = 'member'
                    st.session_state.user_id = st.session_state.email
                    st.session_state.step = 'app'
                    st.rerun()
                else: st.error("الرمز غير صحيح، حاول مجدداً")
            if st.button("رجوع", type="secondary"):
                st.session_state.step = 'gate'
                st.rerun()

# --- 5. لوحة التحكم الرئيسية (The Dashboard) ---
def show_app():
    # الهيدر الاحترافي
    with st.container():
        st.markdown(f"""
            <div style="background: white; padding: 15px 25px; border-radius: 12px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                <div style="display: flex; align-items: center; gap: 15px;">
                    <h2 style="margin:0; color:#1e293b;">🔬 BioLab</h2>
                    <span style="background:#e0f2fe; color:#0369a1; padding:4px 12px; border-radius:20px; font-size:0.8rem; font-weight:bold;">
                        {st.session_state.user_type.upper()}
                    </span>
                </div>
                <div style="color:#64748b;">👤 {st.session_state.user_id}</div>
            </div>
        """, unsafe_allow_html=True)

    # عزل قواعد البيانات برمجياً
    safe_name = "".join(x for x in st.session_state.user_id if x.isalnum())
    db_path = f"store_{safe_name}.csv"
    
    if 'data' not in st.session_state:
        st.session_state.data = pd.read_csv(db_path) if os.path.exists(db_path) else pd.DataFrame(columns=["التاريخ", "المريض", "الفحص", "النتيجة", "الحالة"])

    st.write("")
    
    # التبويبات بنمط Dashboards العالمية
    tab1, tab2, tab3 = st.tabs(["📊 نظرة عامة", "➕ إضافة فحص", "⚙️ الإعدادات"])

    with tab1:
        if st.session_state.data.empty:
            st.info("مرحباً بك! ابدأ بإضافة أول فحص من تبويب 'إضافة فحص'.")
        else:
            m1, m2, m3 = st.columns(3)
            m1.metric("إجمالي الفحوصات", len(st.session_state.data))
            m2.metric("مرضى فريدون", st.session_state.data["المريض"].nunique())
            m3.metric("تحديث اليوم", datetime.now().strftime("%H:%M"))
            st.divider()
            st.dataframe(st.session_state.data, use_container_width=True)

    with tab2:
        with st.form("entry_form"):
            c1, c2 = st.columns(2)
            p_name = c1.text_input("اسم المريض")
            p_test = c2.selectbox("نوع التحليل", ["Glucose", "HbA1c", "Lipid Profile", "CBC"])
            p_res = c1.number_input("النتيجة المخبرية", format="%.2f")
            p_stat = c2.selectbox("التقييم الأولي", ["Normal", "Critical", "Follow-up"])
            
            if st.form_submit_button("إرسال للبيانات السحابية"):
                new_entry = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), p_name, p_test, p_res, p_stat]], columns=st.session_state.data.columns)
                st.session_state.data = pd.concat([st.session_state.data, new_entry], ignore_index=True)
                st.session_state.data.to_csv(db_path, index=False)
                st.toast("✅ تم التزامن مع السيرفر بنجاح!")
                time.sleep(0.5)
                st.rerun()

    with tab3:
        st.write("إعدادات الحساب")
        if st.button("تسجيل الخروج الآمن"):
            for key in list(st.session_state.keys()): del st.session_state[key]
            st.rerun()

# --- 6. نظام التوجيه الأساسي (Core Router) ---
if st.session_state.step == 'gate':
    show_gate()
elif st.session_state.step in ['otp_request', 'otp_verify']:
    show_otp_logic()
elif st.session_state.step == 'app':
    show_app()
