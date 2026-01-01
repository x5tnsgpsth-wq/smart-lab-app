import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime
import time

# 1. إعدادات الصفحة
st.set_page_config(page_title="Smart Lab System", page_icon="🔬", layout="wide")

# 2. نظام التحقق من الدخول (Login System)
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# دالة واجهة الدخول الجميلة
def login_page():
    st.markdown("""
        <style>
        .login-container {
            background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
            padding: 50px;
            border-radius: 20px;
            text-align: center;
            color: white;
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            margin-top: 50px;
        }
        .stButton>button {
            background-color: #ffffff;
            color: #1e3a8a;
            font-weight: bold;
            border-radius: 10px;
            width: 100%;
            height: 50px;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background-color: #f0f0f0;
            transform: scale(1.02);
        }
        </style>
        <div class="login-container">
            <h1 style='font-size: 50px;'>🔬</h1>
            <h2>مرحباً بكم في نظام المختبر الذكي</h2>
            <p>يرجى إدخال رمز الوصول للمتابعة إلى لوحة التحكم</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        password = st.text_input("رمز الدخول", type="password", placeholder="أدخل الرمز هنا...")
        if st.button("دخول إلى المختبر"):
            if password == "1234": # يمكنك تغيير الرمز هنا
                st.session_state.authenticated = True
                with st.spinner('جاري تهيئة النظام الطبي...'):
                    time.sleep(1.5)
                st.rerun()
            else:
                st.error("رمز الدخول غير صحيح، يرجى المحاولة مرة أخرى.")

# 3. إدارة البيانات (تستمر فقط بعد الدخول)
if not st.session_state.authenticated:
    login_page()
else:
    # زر تسجيل الخروج في الشريط الجانبي
    if st.sidebar.button("تسجيل الخروج 🚪"):
        st.session_state.authenticated = False
        st.rerun()

    DB_FILE = "lab_pro_v32.csv"
    SETTINGS_FILE = "settings.csv"

    @st.cache_data
    def get_nr():
        return {"Glucose": [70, 126], "CBC": [12, 16], "HbA1c": [4, 5.6], "Urea": [15, 45]}

    def load_settings():
        if os.path.exists(SETTINGS_FILE):
            try: return pd.read_csv(SETTINGS_FILE)['lab_name'].iloc[0]
            except: return "مختبر التحليلات الافتراضي"
        return "مختبر التحليلات الافتراضي"

    if 'lab_name' not in st.session_state:
        st.session_state.lab_name = load_settings()

    if 'df' not in st.session_state:
        st.session_state.df = pd.read_csv(DB_FILE) if os.path.exists(DB_FILE) else pd.DataFrame(columns=["التاريخ", "المريض", "الفحص", "النتيجة", "الحالة", "المحلل", "الهاتف", "ملاحظات"])

    # واجهة البرنامج الرئيسية (بعد الدخول)
    st.markdown(f"""
        <div style="background-color: #f8fafc; padding: 20px; border-radius: 10px; border-right: 10px solid #1e3a8a; margin-bottom: 20px;">
            <h1 style="color: #1e3a8a; margin: 0;">🔬 {st.session_state.lab_name}</h1>
            <p style="color: #64748b;">نظام الإدارة المخبرية المتكامل</p>
        </div>
    """, unsafe_allow_html=True)

    tabs = st.tabs(["📝 إدخال البيانات", "📄 عرض التقرير", "📊 الإحصائيات", "⚙️ الإعدادات"])

    # --- التبويب 1: إدخال البيانات ---
    with tabs[0]:
        NR = get_nr()
        with st.form("entry_form"):
            c1, c2 = st.columns(2)
            with c1:
                p_phone = st.text_input("رقم هاتف المريض")
                p_name = st.text_input("اسم المريض بالكامل")
            with c2:
                p_test = st.selectbox("نوع الفحص المطلوبة", list(NR.keys()))
                p_res = st.number_input("النتيجة المخبرية", step=0.01, format="%.2f")
            
            if st.form_submit_button("حفظ البيانات في السجل"):
                status = "طبيعي"
                if p_res < NR[p_test][0]: status = "منخفض"
                elif p_res > NR[p_test][1]: status = "مرتفع"
                new_row = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), p_name, p_test, p_res, status, "المختبر", p_phone, ""]], columns=st.session_state.df.columns)
                st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
                st.session_state.df.to_csv(DB_FILE, index=False)
                st.toast("✅ تم الحفظ بنجاح")

    # --- التبويب 2: التقرير ---
    with tabs[1]:
        if not st.session_state.df.empty:
            target = st.selectbox("اختر المريض:", st.session_state.df['المريض'].unique())
            data = st.session_state.df[st.session_state.df['المريض'] == target].iloc[-1]
            st.markdown(f"""
            <div style="border: 2px solid #1e3a8a; padding: 30px; border-radius: 15px; background: white;">
                <h2 style="text-align:center;">{st.session_state.lab_name}</h2>
                <hr>
                <p><b>الاسم:</b> {data['المريض']}</p>
                <p><b>الفحص:</b> {data['الفحص']}</p>
                <p style="font-size: 30px; color: red;"><b>النتيجة: {data['النتيجة']}</b></p>
            </div>
            """, unsafe_allow_html=True)

    # --- التبويب 4: الإعدادات ---
    with tabs[3]:
        new_name = st.text_input("تعديل اسم المختبر:", value=st.session_state.lab_name)
        if st.button("حفظ التغييرات"):
            pd.DataFrame({'lab_name': [new_name]}).to_csv(SETTINGS_FILE, index=False)
            st.session_state.lab_name = new_name
            st.success("تم تحديث الاسم!")
            st.rerun()
