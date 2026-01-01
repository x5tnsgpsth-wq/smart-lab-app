import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime
import plotly.express as px
import time

# --- 1. محرك الإعدادات المتقدم ---
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

# --- 2. إعدادات المنصة والبصرية ---
st.set_page_config(page_title="BioLab Pro Enterprise", page_icon="🧬", layout="wide")

# --- 3. إدارة الجلسة ---
if 'user_code' not in st.session_state: st.session_state.user_code = None
# إضافة متغير للتحكم في عرض الصفحات الفرعية
if 'view' not in st.session_state: st.session_state.view = "main"

# --- 4. شاشة الدخول الاحترافية ---
def login_screen():
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.write("")
        st.markdown("""
            <div style="background: white; padding: 50px; border-radius: 30px; text-align: center; border: 1px solid #eee;">
                <img src="https://cdn-icons-png.flaticon.com/512/822/822118.png" width="100">
                <h1 style="color: #1e3a8a; margin-top: 20px;">BioLab Cloud</h1>
            </div>
        """, unsafe_allow_html=True)
        u_code = st.text_input("🔑 رمز الوصول الخاص بك", type="password")
        if st.button("تسجيل الدخول", use_container_width=True, type="primary"):
            if u_code:
                st.session_state.user_code = u_code
                st.rerun() # هذه الوحيدة اللازمة للانتقال من الدخول للتطبيق

# --- 5. التطبيق الرئيسي ---
def main_app():
    user_settings = load_settings()
    db_file = f"private_db_{''.join(x for x in st.session_state.user_code if x.isalnum())}.csv"
    
    # تحميل البيانات لمرة واحدة
    if 'df' not in st.session_state:
        st.session_state.df = pd.read_csv(db_file) if os.path.exists(db_file) else pd.DataFrame(columns=["ID", "التاريخ", "المريض", "الفحص", "النتيجة", "الحالة", "الهاتف"])

    # تنسيق CSS
    theme_bg = "#f8fafc" if user_settings.get('theme') == "Light" else "#0f172a"
    st.markdown(f"<style>.stApp {{ background-color: {theme_bg}; }}</style>", unsafe_allow_html=True)

    # الهيدر مع زر "رجوع" ديناميكي
    col_h1, col_h2 = st.columns([4, 1])
    with col_h1:
        st.title(f"🧬 {user_settings.get('lab_name')}")
    with col_h2:
        if st.button("⬅️ رجوع للخلف", use_container_width=True, help="العودة للصفحة السابقة دون تحديث"):
            st.session_state.view = "main" # العودة للحالة الرئيسية صامتاً

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 السجلات", "➕ إضافة فحص", "📈 التحليلات", "⚙️ الإعدادات", "🛠️ الأدوات"])

    with tab1:
        st.markdown("### 🔍 أرشيف المرضى")
        # عرض البيانات فوراً من الجلسة
        st.dataframe(st.session_state.df, use_container_width=True)

    with tab2:
        st.markdown("### ✍️ تسجيل فحص جديد")
        with st.form("add_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            name = c1.text_input("اسم المريض")
            test = c2.selectbox("نوع الفحص", ["Glucose", "CBC", "Urea", "Lipid Profile"])
            res = c1.number_input("النتيجة المخبرية")
            phone = c2.text_input("رقم التواصل")
            
            # تم إلغاء st.rerun هنا
            if st.form_submit_button("حفظ السجل"):
                if name:
                    new_row = pd.DataFrame([[str(int(time.time())), datetime.now().strftime("%Y-%m-%d"), name, test, res, "Normal", phone]], columns=st.session_state.df.columns)
                    # التحديث في الذاكرة والملف فوراً
                    st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
                    st.session_state.df.to_csv(db_file, index=False)
                    st.toast("✅ تم الحفظ بنجاح!") # إشعار جانبي بدل إعادة تحميل الصفحة
                else:
                    st.error("يرجى إدخال اسم المريض")

    with tab3:
        if not st.session_state.df.empty:
            fig = px.bar(st.session_state.df, x='التاريخ', y='النتيجة', color='الفحص')
            st.plotly_chart(fig, use_container_width=True)

    with tab4:
        st.markdown("### ⚙️ مركز التحكم")
        with st.container():
            col_s1, col_s2 = st.columns(2)
            new_lab_name = col_s1.text_input("اسم المختبر", value=user_settings.get('lab_name'))
            new_doc_name = col_s1.text_input("الطبيب المسؤول", value=user_settings.get('doctor_name'))
            new_theme = col_s2.radio("المظهر", ["Light", "Dark"], index=0 if user_settings.get('theme') == "Light" else 1)
            
            # تم إلغاء st.rerun هنا واستخدام التحديث الصامت
            if st.button("💾 حفظ الإعدادات", use_container_width=True):
                updated_settings = {
                    "lab_name": new_lab_name,
                    "doctor_name": new_doc_name,
                    "theme": new_theme,
                    "language": user_settings.get('language'),
                    "currency": user_settings.get('currency'),
                    "report_footer": user_settings.get('report_footer'),
                    "auto_save": True
                }
                save_settings(updated_settings)
                st.toast("⚙️ تم تحديث الإعدادات!")

    with tab5:
        if st.button("تسجيل الخروج 🚪", use_container_width=True):
            st.session_state.user_code = None
            st.rerun()

# --- التشغيل ---
if st.session_state.user_code is None:
    login_screen()
else:
    main_app()
