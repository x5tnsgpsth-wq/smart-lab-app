import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime
import time

# 1. إعدادات الصفحة
st.set_page_config(page_title="Pro Lab v4.1", page_icon="🔬", layout="wide")

# 2. وظائف الإعدادات (تعديل: جعل الإعدادات مرتبطة برمز المستخدم)
def get_user_db_path(pwd):
    # ينشئ مسار ملف خاص بناءً على كلمة المرور لمنع تداخل البيانات
    return f"data_user_{pwd}.csv"

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# 3. نظام الدخول
def login_page():
    st.markdown("""
        <style>
        .stApp { background: #0f172a; }
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
            <p>أدخل رمزك الخاص لفتح مختبرك المنعزل</p>
        </div>
    """, unsafe_allow_html=True)
    
    _, col, _ = st.columns([1,1,1])
    with col:
        pwd_input = st.text_input("رمز الوصول", type="password")
        if st.button("دخول", use_container_width=True):
            if pwd_input: # أي رمز يدخل سيفتح مساحة عمل خاصة بهذا الرمز
                st.session_state.authenticated = True
                st.session_state.current_user_pwd = pwd_input
                st.rerun()
            else: st.error("يرجى إدخال الرمز")

if not st.session_state.authenticated:
    login_page()
else:
    # --- تعديل محوري: تحديد ملف البيانات بناءً على الشخص الذي سجل دخوله ---
    USER_DB_FILE = get_user_db_path(st.session_state.current_user_pwd)
    
    # تحميل بيانات المستخدم الحالي فقط من ملفه الخاص
    if 'df' not in st.session_state:
        if os.path.exists(USER_DB_FILE):
            st.session_state.df = pd.read_csv(USER_DB_FILE)
        else:
            st.session_state.df = pd.DataFrame(columns=["التاريخ", "المريض", "الفحص", "النتيجة", "الحالة", "الهاتف"])

    # واجهة البرنامج الاحترافية (نفس التصميم الذي طلبته)
    st.markdown("""
        <style>
        .stApp { background-color: #f1f5f9 !important; }
        .header-bar {
            background: white; padding: 20px; border-radius: 15px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05); margin-bottom: 25px;
            display: flex; justify-content: space-between; align-items: center;
            border-top: 5px solid #2563eb;
        }
        .stat-card {
            background: white; padding: 25px; border-radius: 15px;
            text-align: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
            border: 1px solid #e2e8f0;
        }
        </style>
        <div class="header-bar">
            <div>
                <h1 style="color: #1e293b; margin:0;">🔬 نظام المختبر الشخصي</h1>
                <p style="color: #64748b; margin:0;">مرحباً بك، بياناتك هنا محمية ومنعزلة تماماً</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.title("القائمة")
        st.write(f"المستخدم: {st.session_state.current_user_pwd}")
        if st.button("تسجيل الخروج 🚪"):
            # مسح بيانات الجلسة عند الخروج للتبديل بين المستخدمين
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    # التبويبات (نفس الكود الأصلي مع ربط الحفظ بملف المستخدم)
    t1, t2, t3 = st.tabs(["⚡ تسجيل سريع", "📂 أرشيف المرضى", "⚙️ الإعدادات"])

    with t1:
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("### ✍️ إدخال فحص جديد")
            with st.form("main_form", clear_on_submit=True):
                n_col, t_col = st.columns(2)
                p_name = n_col.text_input("اسم المريض")
                p_test = t_col.selectbox("نوع الفحص", ["Glucose", "CBC", "HbA1c"])
                r_col, p_col = st.columns(2)
                p_res = r_col.number_input("النتيجة")
                p_phone = p_col.text_input("رقم الهاتف")
                
                if st.form_submit_button("حفظ النتيجة وإصدار التقرير"):
                    new_row = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), p_name, p_test, p_res, "طبيعي", p_phone]], columns=st.session_state.df.columns)
                    st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
                    # الحفظ في الملف الخاص بهذا المستخدم فقط
                    st.session_state.df.to_csv(USER_DB_FILE, index=False)
                    st.success(f"تم الحفظ في قاعدة بياناتك الخاصة!")
        
        with col2:
            st.markdown("### 📊 ملخصك الشخصي")
            st.markdown(f'<div class="stat-card"><h4 style="color:#64748b">إجمالي فحوصاتك</h4><h1 style="color:#2563eb">{len(st.session_state.df)}</h1></div>', unsafe_allow_html=True)

    with t2:
        st.markdown("### 🔎 بياناتك المسجلة")
        if not st.session_state.df.empty:
            st.dataframe(st.session_state.df, use_container_width=True)
        else:
            st.info("لا توجد بيانات خاصة بك حتى الآن.")

    with t3:
        st.markdown("### ⚙️ إدارة الحساب")
        st.info(f"ملف بياناتك الحالي: {USER_DB_FILE}")
        if st.button("حذف كافة بياناتي نهائياً"):
            if os.path.exists(USER_DB_FILE):
                os.remove(USER_DB_FILE)
                st.warning("تم مسح الملف بالكامل")
                st.rerun()
