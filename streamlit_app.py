import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime
import plotly.express as px
import time

# --- 1. محرك الإعدادات ---
def load_settings():
    if 'user_code' not in st.session_state or not st.session_state.user_code: return {}
    safe_id = "".join(x for x in st.session_state.user_code if x.isalnum())
    config_path = f"config_{safe_id}.json"
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"lab_name": "Smartlab", "doctor_name": "Admin", "theme": "Light"}

def save_settings(settings):
    safe_id = "".join(x for x in st.session_state.user_code if x.isalnum())
    config_path = f"config_{safe_id}.json"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False)

# --- 2. إعدادات المنصة لمنع التحديث (مهم جداً للهواتف) ---
st.set_page_config(page_title="Smartlab Pro", page_icon="🔬", layout="wide")

# تعطيل خاصية السحب للتحديث في المتصفح عبر CSS
st.markdown("""
    <style>
    /* منع المتصفح من إعادة تحميل الصفحة عند السحب لأسفل */
    html, body {
        overscroll-behavior-y: contain;
        overflow: auto;
    }
    .stApp {
        overscroll-behavior-y: contain;
    }
    </style>
""", unsafe_allow_html=True)

if 'user_code' not in st.session_state: st.session_state.user_code = None

# --- 3. شاشة الدخول ---
def login_screen():
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown('<h1 style="text-align:center;">Access</h1>', unsafe_allow_html=True)
        u_code = st.text_input("رمز الدخول", type="password", key="login_field")
        if st.button("دخول", use_container_width=True):
            st.session_state.user_code = u_code
            st.rerun()

# --- 4. التطبيق الرئيسي المستقر ---
def main_app():
    user_settings = load_settings()
    db_file = f"private_db_{''.join(x for x in st.session_state.user_code if x.isalnum())}.csv"
    
    if 'df' not in st.session_state:
        st.session_state.df = pd.read_csv(db_file) if os.path.exists(db_file) else pd.DataFrame(columns=["ID", "التاريخ", "المريض", "الفحص", "النتيجة", "الحالة", "الهاتف"])

    # واجهة الهيدر
    st.markdown(f"""
        <div style="background:#111; padding:15px; border-radius:10px; color:white; margin-bottom:15px; text-align:center;">
            <h2 style="margin:0;">{user_settings.get('lab_name', 'Smartlab')}</h2>
        </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["📊 السجلات", "➕ إضافة", "📈 تحليلات", "⚙️ الإعدادات"])

    with tab1:
        st.dataframe(st.session_state.df, use_container_width=True)

    with tab2:
        # استخدام st.container لضمان استقرار العناصر
        with st.container():
            st.subheader("تسجيل جديد")
            with st.form("add_form", clear_on_submit=True):
                name = st.text_input("اسم المريض")
                test = st.selectbox("نوع الفحص", ["CBC", "Glucose", "HbA1c", "Urea", "TSH", "Lipid Profile", "Vitamin D"])
                res = st.number_input("النتيجة", format="%.2f")
                phone = st.text_input("الهاتف")
                
                # حفظ صامت بدون st.rerun
                if st.form_submit_button("حفظ"):
                    if name:
                        new_row = pd.DataFrame([[datetime.now().strftime("%H%M%S"), datetime.now().strftime("%Y-%m-%d"), name, test, res, "Normal", phone]], columns=st.session_state.df.columns)
                        st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
                        st.session_state.df.to_csv(db_file, index=False)
                        st.toast("✅ تم الحفظ بنجاح")
                    else:
                        st.error("يرجى كتابة الاسم")

    with tab3:
        if not st.session_state.df.empty:
            st.plotly_chart(px.bar(st.session_state.df, x='التاريخ', y='النتيجة', color='الفحص'), use_container_width=True)

    with tab4:
        st.subheader("الإعدادات")
        n_lab = st.text_input("اسم المختبر", value=user_settings.get('lab_name'))
        n_doc = st.text_input("اسم المسؤول", value=user_settings.get('doctor_name'))
        
        col_btn1, col_btn2 = st.columns(2)
        if col_btn1.button("💾 حفظ", use_container_width=True):
            save_settings({"lab_name": n_lab, "doctor_name": n_doc})
            st.toast("تم التحديث")
            
        if col_btn2.button("⬅️ رجوع", use_container_width=True):
            st.toast("أنت بالفعل في القائمة الرئيسية")

    if st.button("خروج 🚪"):
        st.session_state.clear()
        st.rerun()

# --- التشغيل ---
if st.session_state.user_code is None:
    login_screen()
else:
    main_app()
