import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime
import plotly.express as px
import time

# --- 1. نظام إدارة الإعدادات (Persistent Settings) ---
def load_settings():
    safe_id = "".join(x for x in st.session_state.user_code if x.isalnum())
    config_path = f"config_{safe_id}.json"
    default_settings = {
        "lab_name": "BioLab Pro",
        "doctor_name": "Admin User",
        "language": "العربية",
        "theme": "Light",
        "currency": "USD"
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
st.set_page_config(page_title="BioLab Enterprise", page_icon="🔬", layout="wide")

# --- 3. إدارة الجلسة ---
if 'user_code' not in st.session_state: st.session_state.user_code = None

# --- 4. بوابة الدخول ---
def login_screen():
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown('<div style="text-align:center; padding:40px; background:white; border-radius:20px; box-shadow:0 10px 25px rgba(0,0,0,0.1);"><h1>🔐</h1><h2>BioLab Login</h2></div>', unsafe_allow_html=True)
        u_code = st.text_input("رمز الوصول الشخصي", type="password")
        if st.button("دخول", use_container_width=True, type="primary"):
            if u_code:
                st.session_state.user_code = u_code
                st.rerun()

# --- 5. التطبيق الرئيسي ---
def main_app():
    # تحميل إعدادات المستخدم والبيانات
    user_settings = load_settings()
    db_file = f"private_db_{''.join(x for x in st.session_state.user_code if x.isalnum())}.csv"
    
    # تطبيق الثيم (Theme Logic) عبر CSS
    theme_bg = "#f0f2f6" if user_settings['theme'] == "Light" else "#0e1117"
    card_bg = "#ffffff" if user_settings['theme'] == "Light" else "#161b22"
    text_color = "#1e3a8a" if user_settings['theme'] == "Light" else "#58a6ff"

    st.markdown(f"""
        <style>
        .stApp {{ background-color: {theme_bg}; }}
        .main-header {{
            background: linear-gradient(90deg, #1e3a8a 0%, #2563eb 100%);
            padding: 25px; border-radius: 20px; color: white; margin-bottom: 30px;
        }}
        .stat-card {{
            background-color: {card_bg}; padding: 20px; border-radius: 15px;
            border: 1px solid #30363d; color: {text_color};
        }}
        </style>
    """, unsafe_allow_html=True)

    # تحميل البيانات
    if 'df' not in st.session_state:
        st.session_state.df = pd.read_csv(db_file) if os.path.exists(db_file) else pd.DataFrame(columns=["ID", "التاريخ", "المريض", "الفحص", "النتيجة", "الحالة", "الهاتف"])

    # الهيدر الديناميكي (يستخدم اسم المختبر من الإعدادات)
    st.markdown(f"""
        <div class="main-header">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h1 style="margin:0;">🔬 {user_settings['lab_name']}</h1>
                    <p style="margin:0;">المسؤول: د. {user_settings['doctor_name']}</p>
                </div>
                <div style="text-align:left;"><code>Access Key: {st.session_state.user_code}</code></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # التبويبات (أضفنا خانة الإعدادات)
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 السجلات", "➕ فحص جديد", "📈 تحليلات", "⚙️ الإعدادات", "🛠️ الإدارة"])

    with tab1:
        st.markdown("### 🔍 سجلات المرضى")
        st.dataframe(st.session_state.df, use_container_width=True)

    with tab2:
        with st.form("add_form", clear_on_submit=True):
            st.subheader("تسجيل بيانات")
            c1, c2 = st.columns(2)
            name = c1.text_input("المريض")
            test = c2.selectbox("الفحص", ["Glucose", "CBC", "Urea"])
            res = c1.number_input("النتيجة")
            phone = c2.text_input("الهاتف")
            if st.form_submit_button("حفظ"):
                new_data = pd.DataFrame([[str(int(time.time())), datetime.now().strftime("%Y-%m-%d"), name, test, res, "Normal", phone]], columns=st.session_state.df.columns)
                st.session_state.df = pd.concat([st.session_state.df, new_data], ignore_index=True)
                st.session_state.df.to_csv(db_file, index=False)
                st.success("تم الحفظ")

    with tab3:
        if not st.session_state.df.empty:
            st.plotly_chart(px.pie(st.session_state.df, names='الفحص', title="توزيع الفحوصات"))

    with tab4:
        st.markdown("### ⚙️ إعدادات المنصة")
        with st.expander("🏨 هوية المختبر", expanded=True):
            new_lab_name = st.text_input("اسم المختبر", value=user_settings['lab_name'])
            new_doc_name = st.text_input("اسم المسؤول / الطبيب", value=user_settings['doctor_name'])
        
        with st.expander("🎨 المظهر والتفضيلات"):
            col_th1, col_th2 = st.columns(2)
            new_theme = col_th1.radio("وضع العرض (Theme)", ["Light", "Dark"], index=0 if user_settings['theme'] == "Light" else 1)
            new_lang = col_th2.selectbox("لغة النظام", ["العربية", "English"], index=0 if user_settings['language'] == "العربية" else 1)
            new_curr = st.selectbox("العملة الافتراضية", ["IQD", "USD", "SAR", "EGP"], index=1)

        if st.button("💾 حفظ الإعدادات وتطبيق التغييرات"):
            updated_settings = {
                "lab_name": new_lab_name,
                "doctor_name": new_doc_name,
                "language": new_lang,
                "theme": new_theme,
                "currency": new_curr
            }
            save_settings(updated_settings)
            st.success("✅ تم حفظ الإعدادات بنجاح!")
            time.sleep(1)
            st.rerun()

    with tab5:
        st.markdown("### 🛠️ أدوات النظام")
        if st.button("تسجيل الخروج 🚪"):
            for key in list(st.session_state.keys()): del st.session_state[key]
            st.rerun()
        if st.button("⚠️ مسح كافة البيانات الشخصية", type="secondary"):
            if os.path.exists(db_file): os.remove(db_file)
            st.rerun()

# --- التشغيل ---
if st.session_state.user_code is None:
    login_screen()
else:
    main_app()
