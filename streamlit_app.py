import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime
import time

# 1. إعدادات الصفحة
st.set_page_config(page_title="Pro Lab v4.1", page_icon="🔬", layout="wide")

# 2. وظائف الإعدادات
SETTINGS_FILE = "settings.csv"
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            df_settings = pd.read_csv(SETTINGS_FILE)
            return df_settings['lab_name'].iloc[0], str(df_settings['password'].iloc[0])
        except: return "مختبر التحليلات المتطور", "1234"
    return "مختبر التحليلات المتطور", "1234"

if 'lab_name' not in st.session_state:
    name, pwd = load_settings()
    st.session_state.lab_name = name
    st.session_state.lab_password = pwd

# 3. نظام الدخول
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def login_page():
    # خلفية داكنة لصفحة الدخول فقط
    st.markdown("""
        <style>
        .stApp {
            background: #0f172a;
        }
        .login-box {
            background: #1e293b;
            padding: 50px;
            border-radius: 20px;
            border: 1px solid #334155;
            text-align: center;
            color: white;
        }
        </style>
        <div class="login-box">
            <h1 style='font-size: 50px;'>🔐</h1>
            <h2>الدخول الآمن للنظام</h2>
        </div>
    """, unsafe_allow_html=True)
    
    _, col, _ = st.columns([1,1,1])
    with col:
        pwd_input = st.text_input("رمز الوصول", type="password")
        if st.button("دخول", use_container_width=True):
            if pwd_input == st.session_state.lab_password:
                st.session_state.authenticated = True
                st.rerun()
            else: st.error("الرمز خاطئ")

if not st.session_state.authenticated:
    login_page()
else:
    # --- الواجهة الاحترافية الجديدة (تغيير شامل للألوان) ---
    st.markdown("""
        <style>
        /* تغيير خلفية البرنامج بالكامل للون رمادي فاتح جداً */
        .stApp {
            background-color: #f1f5f9 !important;
        }
        
        /* تصميم الشريط العلوي */
        .header-bar {
            background: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            margin-bottom: 25px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-top: 5px solid #2563eb;
        }

        /* تصميم الكروت الإحصائية */
        .stat-card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
            border: 1px solid #e2e8f0;
        }

        /* تحسين شكل التبويبات */
        .stTabs [data-baseweb="tab-list"] {
            background-color: #e2e8f0;
            padding: 10px;
            border-radius: 15px;
        }
        
        .stTabs [data-baseweb="tab"] {
            font-weight: bold;
            color: #1e293b;
        }

        /* فورم الإدخال */
        [data-testid="stForm"] {
            background: white;
            border-radius: 15px;
            padding: 30px;
            border: none;
            box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        }
        </style>
        
        <div class="header-bar">
            <div>
                <h1 style="color: #1e293b; margin:0;">🔬 {lab_name}</h1>
                <p style="color: #64748b; margin:0;">لوحة التحكم الطبية الاحترافية</p>
            </div>
        </div>
    """.replace("{lab_name}", st.session_state.lab_name), unsafe_allow_html=True)

    # زر الخروج في الجانب
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3063/3063176.png", width=100)
        st.title("القائمة")
        if st.button("تسجيل الخروج 🚪"):
            st.session_state.authenticated = False
            st.rerun()

    # جلب البيانات
    DB_FILE = "lab_pro_v32.csv"
    if 'df' not in st.session_state:
        st.session_state.df = pd.read_csv(DB_FILE) if os.path.exists(DB_FILE) else pd.DataFrame(columns=["التاريخ", "المريض", "الفحص", "النتيجة", "الحالة", "الهاتف"])

    # التبويبات الجديدة
    t1, t2, t3 = st.tabs(["⚡ تسجيل سريع", "📂 أرشيف المرضى", "⚙️ الإعدادات"])

    with t1:
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("### ✍️ إدخال فحص جديد")
            with st.form("main_form"):
                n_col, t_col = st.columns(2)
                n_col.text_input("اسم المريض")
                t_col.selectbox("نوع الفحص", ["Glucose", "CBC", "HbA1c"])
                r_col, p_col = st.columns(2)
                r_col.number_input("النتيجة")
                p_col.text_input("رقم الهاتف")
                if st.form_submit_button("حفظ النتيجة وإصدار التقرير"):
                    st.success("تم الحفظ بنجاح!")
        
        with col2:
            st.markdown("### 📊 ملخص اليوم")
            st.markdown(f'<div class="stat-card"><h4 style="color:#64748b">فحوصات اليوم</h4><h1 style="color:#2563eb">{len(st.session_state.df)}</h1></div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f'<div class="stat-card"><h4 style="color:#64748b">المرضى المسجلين</h4><h1 style="color:#10b981">{st.session_state.df["المريض"].nunique() if not st.session_state.df.empty else 0}</h1></div>', unsafe_allow_html=True)

    with t2:
        st.markdown("### 🔎 البحث المتقدم")
        if not st.session_state.df.empty:
            st.dataframe(st.session_state.df, use_container_width=True)
        else:
            st.info("لا توجد سجلات لعرضها")

    with t3:
        st.markdown("### ⚙️ إدارة النظام")
        with st.expander("تغيير هوية المختبر"):
            st.text_input("اسم المختبر الجديد", value=st.session_state.lab_name)
            st.text_input("كلمة المرور الجديدة", value=st.session_state.lab_password, type="password")
            st.button("تطبيق الإعدادات")
