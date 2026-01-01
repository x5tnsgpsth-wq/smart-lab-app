import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime
import time

# 1. إعدادات الصفحة
st.set_page_config(page_title="Smart Lab System", page_icon="🔬", layout="wide")

# 2. وظائف إدارة الإعدادات (الاسم وكلمة المرور)
SETTINGS_FILE = "settings.csv"

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            df_settings = pd.read_csv(SETTINGS_FILE)
            name = df_settings['lab_name'].iloc[0]
            pwd = str(df_settings['password'].iloc[0])
            return name, pwd
        except:
            return "مختبر التحليلات الافتراضي", "1234"
    return "مختبر التحليلات الافتراضي", "1234"

# تحميل الإعدادات في جلسة العمل
if 'lab_name' not in st.session_state or 'lab_password' not in st.session_state:
    name, pwd = load_settings()
    st.session_state.lab_name = name
    st.session_state.lab_password = pwd

# 3. نظام التحقق من الدخول
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def login_page():
    st.markdown("""
        <style>
        .login-container {
            background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
            padding: 60px;
            border-radius: 30px;
            text-align: center;
            color: white;
            box-shadow: 0 20px 50px rgba(0,0,0,0.3);
            margin-top: 50px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .stButton>button {
            background: #3b82f6;
            color: white;
            font-weight: bold;
            border-radius: 12px;
            width: 100%;
            height: 50px;
            border: none;
        }
        </style>
        <div class="login-container">
            <div style="font-size: 60px; margin-bottom: 10px;">🧬</div>
            <h1 style='font-size: 35px; margin-bottom: 5px;'>نظام الإدارة المخبرية</h1>
            <p style='opacity: 0.8;'>أهلاً بك في بوابة الدخول الآمنة</p>
        </div>
    """, unsafe_allow_html=True)
    
    _, col2, _ = st.columns([1,1.5,1])
    with col2:
        st.write("")
        input_pwd = st.text_input("أدخل رمز الوصول الخاص بالمختبر", type="password")
        if st.button("فتح النظام"):
            if input_pwd == st.session_state.lab_password:
                st.session_state.authenticated = True
                st.success("تم التحقق بنجاح")
                time.sleep(1)
                st.rerun()
            else:
                st.error("رمز الدخول غير صحيح")

# 4. تشغيل البرنامج
if not st.session_state.authenticated:
    login_page()
else:
    # الشريط الجانبي لتسجيل الخروج
    st.sidebar.markdown(f"### 👨‍نيابة عن: \n**{st.session_state.lab_name}**")
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.authenticated = False
        st.rerun()

    DB_FILE = "lab_pro_v32.csv"
    if 'df' not in st.session_state:
        st.session_state.df = pd.read_csv(DB_FILE) if os.path.exists(DB_FILE) else pd.DataFrame(columns=["التاريخ", "المريض", "الفحص", "النتيجة", "الحالة", "المحلل", "الهاتف", "ملاحظات"])

    # واجهة البرنامج الرئيسية
    st.markdown(f"""
        <div style="background-color: white; padding: 25px; border-radius: 15px; border-left: 8px solid #3b82f6; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); margin-bottom: 25px;">
            <h1 style="color: #1e3a8a; margin: 0; display: inline-block;">🔬 {st.session_state.lab_name}</h1>
            <span style="float: left; color: #94a3b8;">{datetime.now().strftime('%Y-%m-%d')}</span>
        </div>
    """, unsafe_allow_html=True)

    tabs = st.tabs(["📝 العمليات", "📄 التقارير", "⚙️ الإعدادات"])

    with tabs[0]: # إدخال البيانات
        with st.form("lab_form"):
            c1, c2 = st.columns(2)
            with c1:
                p_name = st.text_input("اسم المريض")
                p_test = st.selectbox("الفحص", ["Glucose", "CBC", "HbA1c", "Urea"])
            with c2:
                p_res = st.number_input("النتيجة", format="%.2f")
                p_phone = st.text_input("رقم الهاتف")
            
            if st.form_submit_button("حفظ"):
                new_row = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), p_name, p_test, p_res, "طبيعي", "المختبر", p_phone, ""]], columns=st.session_state.df.columns)
                st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
                st.session_state.df.to_csv(DB_FILE, index=False)
                st.toast("تم الحفظ!")

    with tabs[1]: # عرض التقارير
        if not st.session_state.df.empty:
            target = st.selectbox("اختر المريض:", st.session_state.df['المريض'].unique())
            data = st.session_state.df[st.session_state.df['المريض'] == target].iloc[-1]
            st.info(f"عرض آخر فحص لـ: {target}")
            st.write(data)

    with tabs[2]: # الإعدادات (تغيير الاسم وكلمة المرور)
        st.subheader("⚙️ إعدادات النظام")
        new_name = st.text_input("تعديل اسم المختبر:", value=st.session_state.lab_name)
        new_pwd = st.text_input("تعيين رمز دخول جديد (Password):", value=st.session_state.lab_password, type="password")
        
        if st.button("حفظ الإعدادات"):
            # حفظ في ملف csv
            pd.DataFrame({'lab_name': [new_name], 'password': [new_pwd]}).to_csv(SETTINGS_FILE, index=False)
            st.session_state.lab_name = new_name
            st.session_state.lab_password = new_pwd
            st.success("✅ تم تحديث بيانات المختبر ورمز الدخول!")
            time.sleep(1)
            st.rerun()
