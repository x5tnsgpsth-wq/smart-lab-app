import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime
import plotly.express as px

# --- 1. محرك الإعدادات ---
def load_settings():
    if 'user_code' not in st.session_state or not st.session_state.user_code: return {}
    safe_id = "".join(x for x in st.session_state.user_code if x.isalnum())
    config_path = f"config_{safe_id}.json"
    default_settings = {
        "lab_name": "BioLab Pro",
        "doctor_name": "Admin User",
        "language": "العربية",
        "theme": "Light",
        "currency": "USD",
        "report_footer": "نتمنى لكم دوام الصحة والعافية",
        "auto_save": True
    }
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return {**default_settings, **json.load(f)}
    return default_settings

def save_settings(settings):
    safe_id = "".join(x for x in st.session_state.user_code if x.isalnum())
    config_path = f"config_{safe_id}.json"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=4)

# --- 2. إعدادات المنصة ---
st.set_page_config(page_title="BioLab Pro Enterprise", page_icon="🧬", layout="wide")

if 'user_code' not in st.session_state: st.session_state.user_code = None

# --- 3. شاشة الدخول ---
def login_screen():
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.write("")
        st.markdown("""
            <div style="background: white; padding: 40px; border-radius: 30px; text-align: center; border: 1px solid #eee;">
                <img src="https://cdn-icons-png.flaticon.com/512/822/822118.png" width="80">
                <h2 style="color: #1e3a8a;">دخول النظام</h2>
            </div>
        """, unsafe_allow_html=True)
        u_code = st.text_input("🔑 رمز الوصول", type="password")
        if st.button("دخول", use_container_width=True, type="primary"):
            if u_code:
                st.session_state.user_code = u_code
                st.rerun()

# --- 4. التطبيق الرئيسي ---
def main_app():
    user_settings = load_settings()
    safe_id = "".join(x for x in st.session_state.user_code if x.isalnum())
    db_file = f"private_db_{safe_id}.csv"
    
    # تحميل البيانات لمرة واحدة في الجلسة
    if 'df' not in st.session_state:
        if os.path.exists(db_file):
            st.session_state.df = pd.read_csv(db_file)
        else:
            st.session_state.df = pd.DataFrame(columns=["ID", "التاريخ", "المريض", "الفحص", "النتيجة", "الحالة", "الهاتف"])

    # الثيم والتنسيق
    theme_bg = "#f8fafc" if user_settings.get('theme') == "Light" else "#0f172a"
    st.markdown(f"""
        <style>
        .stApp {{ background-color: {theme_bg}; }}
        .main-header {{
            background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
            padding: 20px; border-radius: 20px; color: white; margin-bottom: 20px;
        }}
        </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
        <div class="main-header">
            <h1 style="margin:0;">🧬 {user_settings.get('lab_name')}</h1>
            <p style="margin:0; opacity:0.8;">د. {user_settings.get('doctor_name')}</p>
        </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 السجلات", "➕ إضافة", "📈 تحليلات", "⚙️ الإعدادات", "🛠️ الأدوات"])

    with tab1:
        st.dataframe(st.session_state.df, use_container_width=True)

    with tab2:
        with st.form("add_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            name = c1.text_input("اسم المريض")
            test = c2.selectbox("الفحص", ["Glucose", "CBC", "Urea"])
            res = c1.number_input("النتيجة")
            phone = c2.text_input("الهاتف")
            if st.form_submit_button("حفظ"):
                if name:
                    new_row = pd.DataFrame([[datetime.now().strftime("%H%M%S"), datetime.now().strftime("%Y-%m-%d"), name, test, res, "Normal", phone]], columns=st.session_state.df.columns)
                    # تحديث مباشر في الجلسة والملف
                    st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
                    st.session_state.df.to_csv(db_file, index=False)
                    st.success("تم الحفظ بنجاح") # ستظهر وتختفي بسلاسة
                else:
                    st.error("يرجى إدخال اسم المريض")

    with tab3:
        if not st.session_state.df.empty:
            st.plotly_chart(px.bar(st.session_state.df, x='التاريخ', y='النتيجة', color='الفحص'), use_container_width=True)

    with tab4:
        st.subheader("⚙️ إعدادات النظام")
        col1, col2 = st.columns(2)
        with col1:
            new_lab = st.text_input("اسم المختبر", value=user_settings.get('lab_name'))
            new_doc = st.text_input("اسم المسؤول", value=user_settings.get('doctor_name'))
        with col2:
            new_theme = st.radio("المظهر", ["Light", "Dark"], index=0 if user_settings.get('theme') == "Light" else 1, horizontal=True)
            new_lang = st.selectbox("اللغة", ["العربية", "English"])

        if st.button("💾 حفظ الإعدادات", type="primary"):
            updated = {
                "lab_name": new_lab, "doctor_name": new_doc,
                "theme": new_theme, "language": new_lang,
                "report_footer": user_settings.get('report_footer'),
                "currency": user_settings.get('currency')
            }
            save_settings(updated)
            st.toast("تم التحديث!")
            # ملاحظة: لا نستخدم rerun هنا، التغييرات ستظهر في المرة القادمة تلقائياً أو عند الانتقال بين التبويبات

    with tab5:
        if st.button("خروج آمن 🚪"):
            st.session_state.user_code = None
            st.rerun() # الخروج هو الحالة الوحيدة التي تتطلب إعادة تحميل كاملة للشاشة

# --- التشغيل ---
if st.session_state.user_code is None:
    login_screen()
else:
    main_app()
