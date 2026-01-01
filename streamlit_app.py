import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime
import plotly.express as px
import time

# --- 1. محرك الإعدادات المتقدم ---
def load_settings():
    if 'user_code' not in st.session_state: return {}
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

# --- 4. شاشة الدخول الاحترافية ---
def login_screen():
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.write("")
        st.markdown("""
            <div style="background: white; padding: 50px; border-radius: 30px; shadow: 0 20px 40px rgba(0,0,0,0.1); text-align: center;">
                <img src="https://cdn-icons-png.flaticon.com/512/822/822118.png" width="100">
                <h1 style="color: #1e3a8a; margin-top: 20px;">BioLab Cloud</h1>
                <p style="color: #64748b;">نظام إدارة المختبرات الذكي</p>
            </div>
        """, unsafe_allow_html=True)
        u_code = st.text_input("🔑 رمز الوصول الخاص بك", type="password", placeholder="أدخل الرمز هنا...")
        if st.button("تسجيل الدخول الآمن", use_container_width=True, type="primary"):
            if u_code:
                st.session_state.user_code = u_code
                st.rerun()
            else: st.error("يرجى إدخال الرمز السري")

# --- 5. التطبيق الرئيسي ---
def main_app():
    user_settings = load_settings()
    db_file = f"private_db_{''.join(x for x in st.session_state.user_code if x.isalnum())}.csv"
    
    # تحسين الثيم عبر CSS
    theme_bg = "#f8fafc" if user_settings['theme'] == "Light" else "#0f172a"
    card_bg = "#ffffff" if user_settings['theme'] == "Light" else "#1e293b"
    text_main = "#1e293b" if user_settings['theme'] == "Light" else "#f8fafc"

    st.markdown(f"""
        <style>
        .stApp {{ background-color: {theme_bg}; color: {text_main}; }}
        .main-header {{
            background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
            padding: 30px; border-radius: 25px; color: white; margin-bottom: 30px;
            box-shadow: 0 10px 20px rgba(59, 130, 246, 0.2);
        }}
        .tab-content {{ background: {card_bg}; padding: 25px; border-radius: 20px; border: 1px solid #e2e8f0; }}
        </style>
    """, unsafe_allow_html=True)

    if 'df' not in st.session_state:
        st.session_state.df = pd.read_csv(db_file) if os.path.exists(db_file) else pd.DataFrame(columns=["ID", "التاريخ", "المريض", "الفحص", "النتيجة", "الحالة", "الهاتف"])

    # الهيدر
    st.markdown(f"""
        <div class="main-header">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h1 style="margin:0; font-size: 32px;">🧬 {user_settings['lab_name']}</h1>
                    <p style="margin:0; opacity: 0.9;">مرحباً دكتور/ {user_settings['doctor_name']}</p>
                </div>
                <img src="https://cdn-icons-png.flaticon.com/512/2785/2785482.png" width="60">
            </div>
        </div>
    """, unsafe_allow_html=True)

    # التبويبات الملونة بالأيقونات
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 السجلات", 
        "➕ إضافة فحص", 
        "📈 التحليلات", 
        "⚙️ الإعدادات", 
        "🛠️ الأدوات"
    ])

    with tab1:
        st.markdown("### 🔍 أرشيف المرضى")
        st.image("https://cdn-icons-png.flaticon.com/512/2693/2693507.png", width=50)
        st.dataframe(st.session_state.df, use_container_width=True)

    with tab2:
        st.markdown("### ✍️ تسجيل فحص جديد")
        st.image("https://cdn-icons-png.flaticon.com/512/4306/4306431.png", width=50)
        with st.form("add_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            name = c1.text_input("اسم المريض")
            test = c2.selectbox("نوع الفحص", ["Glucose", "CBC", "Urea", "Lipid Profile"])
            res = c1.number_input("النتيجة المخبرية")
            phone = c2.text_input("رقم التواصل")
            if st.form_submit_button("حفظ السجل"):
                new_row = pd.DataFrame([[str(int(time.time())), datetime.now().strftime("%Y-%m-%d"), name, test, res, "Normal", phone]], columns=st.session_state.df.columns)
                st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
                st.session_state.df.to_csv(db_file, index=False)
                st.balloons()
                st.success("تمت إضافة السجل بنجاح!")

    with tab3:
        st.markdown("### 📈 تحليلات ذكية")
        st.image("https://cdn-icons-png.flaticon.com/512/1728/1728773.png", width=50)
        if not st.session_state.df.empty:
            fig = px.bar(st.session_state.df, x='التاريخ', y='النتيجة', color='الفحص', title="متابعة النتائج الزمنية")
            st.plotly_chart(fig, use_container_width=True)

    with tab4:
        st.markdown("### ⚙️ مركز التحكم والإعدادات")
        st.image("https://cdn-icons-png.flaticon.com/512/3938/3938457.png", width=60)
        
        col_s1, col_s2 = st.columns(2)
        
        with col_s1:
            st.info("🏥 بيانات المختبر")
            new_lab_name = st.text_input("اسم المختبر المخصص", value=user_settings['lab_name'])
            new_doc_name = st.text_input("اسم الطبيب المسؤول", value=user_settings['doctor_name'])
            new_footer = st.text_area("تذييل التقارير (Footer)", value=user_settings['report_footer'])
            
        with col_s2:
            st.info("🎨 التخصيص واللغة")
            new_theme = st.radio("مظهر التطبيق", ["Light", "Dark"], index=0 if user_settings['theme'] == "Light" else 1, horizontal=True)
            new_lang = st.selectbox("لغة الواجهة", ["العربية", "English"], index=0 if user_settings['language'] == "العربية" else 1)
            new_curr = st.selectbox("العملة في الفواتير", ["USD", "IQD", "SAR", "EGP"], index=0)
            auto_save = st.toggle("تفعيل الحفظ التلقائي", value=user_settings.get('auto_save', True))

        if st.button("💾 حفظ كافة التغييرات", type="primary", use_container_width=True):
            save_settings({
                "lab_name": new_lab_name,
                "doctor_name": new_doc_name,
                "theme": new_theme,
                "language": new_lang,
                "currency": new_curr,
                "report_footer": new_footer,
                "auto_save": auto_save
            })
            st.toast("تم تحديث الإعدادات بنجاح!")
            time.sleep(1)
            st.rerun()

    with tab5:
        st.markdown("### 🛠️ صيانة النظام")
        st.image("https://cdn-icons-png.flaticon.com/512/2040/2040504.png", width=50)
        c_m1, c_m2 = st.columns(2)
        if c_m1.button("تسجيل الخروج الآمن 🚪", use_container_width=True):
            st.session_state.user_code = None
            st.rerun()
        if c_m2.button("🧹 مسح الذاكرة المؤقتة", use_container_width=True):
            st.cache_data.clear()
            st.success("تم مسح الكاش")

# --- التشغيل ---
if st.session_state.user_code is None:
    login_screen()
else:
    main_app()
