import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime
import plotly.express as px
import io

# --- 1. محرك الإعدادات ---
def get_status(test, result):
    ranges = {
        "Glucose (Fasting)": (70, 100),
        "HbA1c": (4, 5.7),
        "Uric Acid": (3.5, 7.2),
        "Calcium": (8.5, 10.5)
    }
    if test in ranges:
        low, high = ranges[test]
        if result < low: return "🔴 Low"
        if result > high: return "🟡 High"
        return "🟢 Normal"
    return "⚪ Not Set"

def load_settings():
    if 'user_code' not in st.session_state or not st.session_state.user_code: return {}
    safe_id = "".join(x for x in st.session_state.user_code if x.isalnum())
    config_path = f"config_{safe_id}.json"
    default_settings = {"lab_name": "SmartLab Pro", "doctor_name": "Admin", "theme": "Dark"}
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return {**default_settings, **json.load(f)}
    return default_settings

def save_settings(settings):
    safe_id = "".join(x for x in st.session_state.user_code if x.isalnum())
    config_path = f"config_{safe_id}.json"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False)

# --- 2. الحل الجذري لمنع تحديث الصفحة (Anti-Pull-to-Refresh) ---
st.set_page_config(page_title="BioLab Ultra", page_icon="🧬", layout="wide")

st.markdown("""
    <style>
    /* 1. منع خاصية السحب للتحديث في الأندرويد والآيفون نهائياً */
    html, body, [data-testid="stAppViewContainer"], .main {
        overscroll-behavior-y: contain !important;
        overscroll-behavior: none !important;
        position: fixed;
        width: 100%;
        height: 100%;
        overflow-y: auto;
        -webkit-overflow-scrolling: touch;
    }

    /* 2. تحسين تصميم البطاقات */
    .patient-card {
        background: #ffffff; padding: 15px; border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 10px;
        border-right: 5px solid #1e3a8a; color: #1e293b;
    }
    
    /* 3. إخفاء أي هوامش تسبب قفز الصفحة */
    .block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; }
    header { visibility: hidden; } /* إخفاء هيدر ستريمليت الافتراضي */
    </style>
""", unsafe_allow_html=True)

if 'user_code' not in st.session_state: st.session_state.user_code = None

# --- 3. شاشة الدخول ---
if st.session_state.user_code is None:
    _, col, _ = st.columns([0.1, 0.8, 0.1])
    with col:
        st.image("https://cdn-icons-png.flaticon.com/512/3063/3063205.png", width=80)
        st.title("BioLab Ultra")
        u_code = st.text_input("رمز الدخول", type="password", key="login_key")
        if st.button("دخول للنظام", use_container_width=True, type="primary"):
            st.session_state.user_code = u_code
            st.rerun()
else:
    # --- 4. التطبيق الرئيسي ---
    user_settings = load_settings()
    db_file = f"private_db_{''.join(x for x in st.session_state.user_code if x.isalnum())}.csv"
    
    if 'df' not in st.session_state:
        st.session_state.df = pd.read_csv(db_file) if os.path.exists(db_file) else pd.DataFrame(columns=["ID", "التاريخ", "المريض", "الفحص", "النتيجة", "الحالة", "الهاتف"])

    # الهيدر الاحترافي
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); padding:20px; border-radius:20px; color:white; margin-bottom:20px;">
            <h2 style="margin:0;">{user_settings.get('lab_name')}</h2>
            <p style="margin:0; opacity:0.8;">د. {user_settings.get('doctor_name')}</p>
        </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["📋 السجلات", "🧪 إضافة فحص", "📈 إحصائيات", "⚙️ الإعدادات"])

    with tab1:
        search = st.text_input("🔍 ابحث هنا...", placeholder="اسم المريض أو الرقم", key="search_input")
        filtered = st.session_state.df
        if search:
            filtered = filtered[filtered['المريض'].str.contains(search, na=False) | filtered['الهاتف'].str.contains(search, na=False)]

        # عرض البطاقات
        for index, row in filtered.iloc[::-1].head(15).iterrows():
            st.markdown(f"""
                <div class="patient-card">
                    <div style="display: flex; justify-content: space-between;"><b>👤 {row['المريض']}</b><small>{row['التاريخ']}</small></div>
                    <div style="margin-top:5px;">{row['الفحص']}: <b>{row['النتيجة']}</b> <span style="float:left;">{row['الحالة']}</span></div>
                </div>
            """, unsafe_allow_html=True)
            
        if not st.session_state.df.empty:
            buffer = io.BytesIO()
            st.session_state.df.to_excel(buffer, index=False)
            st.download_button("📥 تحميل قاعدة البيانات (Excel)", data=buffer.getvalue(), file_name="lab_data.xlsx", use_container_width=True)

    with tab2:
        # استخدام st.container لضمان ثبات العناصر عند الإدخال
        with st.container():
            st.markdown("### ✍️ إدخال عينة")
            with st.form("ultra_form_no_refresh", clear_on_submit=True):
                c1, c2 = st.columns(2)
                name = c1.text_input("اسم المريض")
                phone = c2.text_input("رقم الهاتف")
                test = st.selectbox("نوع الفحص", ["Glucose (Fasting)", "HbA1c", "CBC", "Uric Acid", "TSH", "Creatinine", "Urea"])
                result = st.number_input("النتيجة", step=0.01)
                
                if st.form_submit_button("حفظ البيانات ✅", use_container_width=True):
                    if name:
                        status = get_status(test, result)
                        new_data = pd.DataFrame([[datetime.now().strftime("%H%M%S"), datetime.now().strftime("%Y-%m-%d"), name, test, result, status, phone]], columns=st.session_state.df.columns)
                        st.session_state.df = pd.concat([st.session_state.df, new_data], ignore_index=True)
                        st.session_state.df.to_csv(db_file, index=False)
                        st.toast(f"تم الحفظ بنجاح: {status}")
                    else: st.error("يرجى كتابة الاسم")

    with tab3:
        if not st.session_state.df.empty:
            st.plotly_chart(px.pie(st.session_state.df, names='الحالة', hole=0.4), use_container_width=True)
            st.plotly_chart(px.histogram(st.session_state.df, x='الفحص'), use_container_width=True)

    with tab4:
        st.markdown("### ⚙️ الإعدادات")
        n_lab = st.text_input("اسم المختبر", value=user_settings.get('lab_name'))
        n_doc = st.text_input("الطبيب المشرف", value=user_settings.get('doctor_name'))
        if st.button("💾 حفظ الإعدادات", use_container_width=True):
            save_settings({"lab_name": n_lab, "doctor_name": n_doc})
            st.toast("تم التحديث!")
        
        if st.button("تسجيل الخروج 🚪", use_container_width=True):
            st.session_state.clear()
            st.rerun()
