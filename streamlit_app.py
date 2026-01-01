import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime
import time

# 1. إعدادات الصفحة
st.set_page_config(page_title="Pro Lab System", page_icon="🧪", layout="wide")

# 2. وظائف الإعدادات
SETTINGS_FILE = "settings.csv"
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            df_settings = pd.read_csv(SETTINGS_FILE)
            return df_settings['lab_name'].iloc[0], str(df_settings['password'].iloc[0])
        except: return "مختبر التحليلات المتقدم", "1234"
    return "مختبر التحليلات المتقدم", "1234"

if 'lab_name' not in st.session_state:
    name, pwd = load_settings()
    st.session_state.lab_name = name
    st.session_state.lab_password = pwd

# 3. نظام الدخول
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def login_page():
    st.markdown("""
        <style>
        .login-card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 40px;
            border-radius: 25px;
            border: 1px solid rgba(255,255,255,0.2);
            text-align: center;
            color: white;
            margin-top: 100px;
        }
        .stApp {
            background: radial-gradient(circle at top right, #1e293b, #0f172a);
        }
        </style>
        <div class="login-card">
            <h1 style='font-size: 60px;'>🧪</h1>
            <h2 style='font-weight: 300;'>نظام الإدارة الطبية</h2>
            <p style='color: #94a3b8;'>الرجاء إدخال الرمز السري للولوج</p>
        </div>
    """, unsafe_allow_html=True)
    
    _, col, _ = st.columns([1,1.2,1])
    with col:
        pwd_input = st.text_input("", type="password", placeholder="رمز الدخول")
        if st.button("تسجيل الدخول", use_container_width=True):
            if pwd_input == st.session_state.lab_password:
                st.session_state.authenticated = True
                st.rerun()
            else: st.error("الرمز غير صحيح")

if not st.session_state.authenticated:
    login_page()
else:
    # --- الواجهة الاحترافية بعد الدخول ---
    
    # تحسين CSS الواجهة
    st.markdown("""
        <style>
        /* ستايل البطاقات الإحصائية */
        .metric-card {
            background-color: #ffffff;
            border-radius: 15px;
            padding: 20px;
            border-right: 5px solid #3b82f6;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            text-align: center;
        }
        /* ستايل التقرير الطبي */
        .medical-report {
            background: white;
            padding: 40px;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #1e293b;
        }
        .report-header {
            border-bottom: 2px solid #3b82f6;
            padding-bottom: 20px;
            margin-bottom: 20px;
            text-align: center;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            background-color: transparent;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            background-color: #f1f5f9;
            border-radius: 10px;
            padding: 10px 20px;
            color: #475569;
        }
        .stTabs [aria-selected="true"] {
            background-color: #3b82f6 !important;
            color: white !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # الهيدر العلوي
    with st.container():
        c1, c2 = st.columns([3, 1])
        with c1:
            st.markdown(f"## 🏥 {st.session_state.lab_name}")
            st.caption(f"تاريخ اليوم: {datetime.now().strftime('%Y-%m-%d')} | نظام المختبرات v4.0")
        with c2:
            if st.button("تسجيل خروج 🚪", use_container_width=True):
                st.session_state.authenticated = False
                st.rerun()

    st.divider()

    # جلب البيانات
    DB_FILE = "lab_pro_v32.csv"
    if 'df' not in st.session_state:
        st.session_state.df = pd.read_csv(DB_FILE) if os.path.exists(DB_FILE) else pd.DataFrame(columns=["التاريخ", "المريض", "الفحص", "النتيجة", "الحالة", "الهاتف"])

    # التبويبات الاحترافية
    t1, t2, t3, t4 = st.tabs(["➕ إضافة فحص", "📋 السجلات", "📊 لوحة التحليل", "⚙️ الإعدادات"])

    with t1:
        with st.container():
            st.markdown("### 📝 تسجيل مريض جديد")
            with st.form("pro_form", clear_on_submit=True):
                col_a, col_b = st.columns(2)
                with col_a:
                    p_name = st.text_input("اسم المريض الثلاثي")
                    p_test = st.selectbox("نوع التحليل", ["Glucose", "HbA1c", "CBC", "Urea", "Creatinine"])
                with col_b:
                    p_phone = st.text_input("رقم الجوال")
                    p_res = st.number_input("النتيجة المخبرية", format="%.2f")
                
                if st.form_submit_button("إعتماد النتيجة وحفظها"):
                    # تحديد الحالة برمجياً
                    status = "Normal"
                    if p_test == "Glucose" and p_res > 126: status = "High"
                    
                    new_entry = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), p_name, p_test, p_res, status, p_phone]], columns=st.session_state.df.columns)
                    st.session_state.df = pd.concat([st.session_state.df, new_entry], ignore_index=True)
                    st.session_state.df.to_csv(DB_FILE, index=False)
                    st.success(f"تم تسجيل نتيجة المريض {p_name} بنجاح")

    with t2:
        if not st.session_state.df.empty:
            st.markdown("### 📄 التقارير الطبية")
            selected_patient = st.selectbox("بحث عن مريض:", st.session_state.df['المريض'].unique())
            patient_data = st.session_state.df[st.session_state.df['المريض'] == selected_patient].iloc[-1]
            
            # تصميم تقرير ورقي احترافي
            st.markdown(f"""
            <div class="medical-report">
                <div class="report-header">
                    <h2>{st.session_state.lab_name}</h2>
                    <p>تقرير مختبري معتمد</p>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 30px;">
                    <div><b>اسم المريض:</b> {patient_data['المريض']}</div>
                    <div><b>التاريخ:</b> {patient_data['التاريخ']}</div>
                </div>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr style="background: #f8fafc; text-align: right;">
                        <th style="padding: 15px; border: 1px solid #e2e8f0;">الفحص</th>
                        <th style="padding: 15px; border: 1px solid #e2e8f0;">النتيجة</th>
                        <th style="padding: 15px; border: 1px solid #e2e8f0;">الحالة</th>
                    </tr>
                    <tr>
                        <td style="padding: 15px; border: 1px solid #e2e8f0;">{patient_data['الفحص']}</td>
                        <td style="padding: 15px; border: 1px solid #e2e8f0; font-weight: bold; color: #ef4444;">{patient_data['النتيجة']}</td>
                        <td style="padding: 15px; border: 1px solid #e2e8f0;">{patient_data['الحالة']}</td>
                    </tr>
                </table>
                <div style="margin-top: 50px; text-align: left; font-style: italic; color: #64748b;">
                    ختم المختبر الرسمي
                </div>
            </div>
            """, unsafe_allow_html=True)

    with t3:
        st.markdown("### 📊 إحصائيات المختبر")
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.markdown(f'<div class="metric-card"><h4>إجمالي الفحوصات</h4><h2>{len(st.session_state.df)}</h2></div>', unsafe_allow_html=True)
        with col_m2:
            today_count = len(st.session_state.df[st.session_state.df['التاريخ'] == datetime.now().strftime("%Y-%m-%d")])
            st.markdown(f'<div class="metric-card" style="border-right-color: #10b981;"><h4>فحوصات اليوم</h4><h2>{today_count}</h2></div>', unsafe_allow_html=True)
        with col_m3:
            st.markdown(f'<div class="metric-card" style="border-right-color: #f59e0b;"><h4>عدد المرضى</h4><h2>{st.session_state.df["المريض"].nunique()}</h2></div>', unsafe_allow_html=True)
        
        if not st.session_state.df.empty:
            fig = px.bar(st.session_state.df, x='التاريخ', title="حركة الفحوصات اليومية", template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)

    with t4:
        st.markdown("### ⚙️ الإعدادات المتقدمة")
        new_n = st.text_input("اسم المنشأة الطبية", value=st.session_state.lab_name)
        new_p = st.text_input("رمز الدخول الجديد", value=st.session_state.lab_password, type="password")
        if st.button("حفظ التغييرات"):
            pd.DataFrame({'lab_name': [new_n], 'password': [new_p]}).to_csv(SETTINGS_FILE, index=False)
            st.success("تم التحديث! سيتم تطبيق الإعدادات عند إعادة التشغيل")
