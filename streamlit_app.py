import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime
import plotly.express as px
import io

# --- 1. إعدادات المنصة ---
st.set_page_config(page_title="BioLab Pro", page_icon="🧬", layout="wide")

# --- 2. محرك القفل العميق (Deep Lock) لمنع التحديث ---
st.markdown("""
    <style>
    /* منع الارتداد في المتصفح بالكامل */
    html, body {
        overscroll-behavior-y: none !important;
        overscroll-behavior: none !important;
        height: 100% !important;
        width: 100% !important;
        position: fixed !important;
        overflow: hidden !important;
    }

    /* إنشاء حاوية تمرير مستقلة تماماً عن المتصفح */
    .stApp {
        height: 100vh !important;
        overflow-y: auto !important;
        -webkit-overflow-scrolling: touch;
        /* إضافة هامش وهمي يمنع المتصفح من الوصول للحافة العلوية */
        padding-top: 1px !important; 
    }

    /* إخفاء العناصر التي تسبب عدم استقرار في الحركة */
    header, footer, #MainMenu {visibility: hidden !important;}
    
    /* تنسيق البطاقات الاحترافي */
    .patient-card {
        background: white;
        padding: 16px;
        border-radius: 12px;
        margin-bottom: 12px;
        border-right: 6px solid #1e3a8a;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        color: #1e293b;
    }
    </style>

    <script>
    // جافا سكريبت لمنع المتصفح من التعامل مع سحب الإصبع لأسفل
    var lastTouchY = 0;
    var maybePrevent = false;

    window.addEventListener('touchstart', function(e) {
        if (e.touches.length !== 1) return;
        lastTouchY = e.touches[0].clientY;
        maybePrevent = window.pageYOffset === 0;
    }, {passive: false});

    window.addEventListener('touchmove', function(e) {
        var touchY = e.touches[0].clientY;
        var touchYDelta = touchY - lastTouchY;
        lastTouchY = touchY;

        if (maybePrevent && touchYDelta > 0) {
            maybePrevent = false;
            e.preventDefault();
            return;
        }
    }, {passive: false});
    </script>
""", unsafe_allow_html=True)

# --- 3. إدارة الجلسة والبيانات ---
if 'user_code' not in st.session_state:
    st.session_state.user_code = None

def load_settings():
    safe_id = "".join(x for x in (st.session_state.user_code or "admin") if x.isalnum())
    p = f"config_{safe_id}.json"
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8") as f: return json.load(f)
    return {"lab_name": "SmartLab Pro", "doctor_name": "Admin"}

# --- 4. شاشة الدخول ---
if st.session_state.user_code is None:
    _, col, _ = st.columns([0.1, 0.8, 0.1])
    with col:
        st.markdown("<div style='height:100px'></div>", unsafe_allow_html=True)
        st.image("https://cdn-icons-png.flaticon.com/512/3063/3063205.png", width=80)
        st.title("BioLab Ultra")
        st.caption("نظام إدارة المختبرات - دخول آمن")
        u_code = st.text_input("ادخل الرمز السري", type="password")
        if st.button("دخول", use_container_width=True, type="primary"):
            st.session_state.user_code = u_code
            st.rerun()
else:
    # --- 5. التطبيق الرئيسي ---
    user_settings = load_settings()
    safe_id = "".join(x for x in st.session_state.user_code if x.isalnum())
    db_file = f"private_db_{safe_id}.csv"
    
    if 'df' not in st.session_state:
        st.session_state.df = pd.read_csv(db_file) if os.path.exists(db_file) else pd.DataFrame(columns=["ID", "التاريخ", "المريض", "الفحص", "النتيجة", "الحالة", "الهاتف"])

    # واجهة التطبيق
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); padding:25px; border-radius:20px; color:white; margin-bottom:20px;">
            <h2 style="margin:0; font-size:24px;">{user_settings.get('lab_name')}</h2>
            <p style="margin:0; opacity:0.8;">د. {user_settings.get('doctor_name')}</p>
        </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📋 السجلات", "🧪 فحص جديد", "⚙️ الإعدادات"])

    with tab1:
        search = st.text_input("🔍 بحث...", placeholder="اكتب اسم المريض...")
        df_to_show = st.session_state.df
        if search:
            df_to_show = df_to_show[df_to_show['المريض'].str.contains(search, na=False)]
        
        for idx, row in df_to_show.iloc[::-1].head(10).iterrows():
            st.markdown(f"""
                <div class="patient-card">
                    <b>👤 {row['المريض']}</b><br>
                    <small>📅 {row['التاريخ']} | {row['الفحص']}</small><br>
                    <div style="margin-top:8px;">النتيجة: <b>{row['النتيجة']}</b> <span style="float:left;">{row['الحالة']}</span></div>
                </div>
            """, unsafe_allow_html=True)

    with tab2:
        with st.form("new_test", clear_on_submit=True):
            name = st.text_input("اسم المريض")
            test = st.selectbox("نوع الفحص", ["CBC", "HbA1c", "Glucose", "TSH", "Urea"])
            res = st.number_input("النتيجة", step=0.1)
            if st.form_submit_button("حفظ النتيجة ✅", use_container_width=True):
                if name:
                    new_data = pd.DataFrame([[datetime.now().strftime("%H%M"), datetime.now().strftime("%Y-%m-%d"), name, test, res, "Normal", ""]], columns=st.session_state.df.columns)
                    st.session_state.df = pd.concat([st.session_state.df, new_data], ignore_index=True)
                    st.session_state.df.to_csv(db_file, index=False)
                    st.toast("تم الحفظ بنجاح")
                else: st.error("أدخل الاسم!")

    with tab3:
        if st.button("تسجيل الخروج 🚪", use_container_width=True):
            st.session_state.user_code = None
            st.rerun()

    st.markdown("<br><center style='color:gray; font-size:12px;'>BioLab Stable Build 2026</center>", unsafe_allow_html=True)
