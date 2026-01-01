import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime
import plotly.express as px
import io

# --- 1. القفل النووي لحلقة التحميل (يجب أن يكون أول شيء) ---
st.set_page_config(page_title="BioLab Ultra", page_icon="🧬", layout="wide")

# هذا الجزء هو "المبيد" الحقيقي لحلقة التحميل
st.markdown("""
    <style>
    /* 1. تجميد المتصفح تماماً ومنع الارتداد */
    html, body, [data-testid="stAppViewContainer"] {
        overflow: hidden !important;
        position: fixed !important;
        width: 100% !important;
        height: 100% !important;
        overscroll-behavior-y: none !important;
        overscroll-behavior: none !important;
        touch-action: none !important; /* تعطيل اللمس على الطبقة الخارجية */
    }

    /* 2. إعادة تفعيل اللمس فقط داخل منطقة العمل الداخلية */
    [data-testid="stMainViewContainer"] {
        overflow-y: auto !important;
        height: 100vh !important;
        -webkit-overflow-scrolling: touch !important;
        touch-action: pan-y !important; /* السماح بالتحرك للأعلى والأسفل فقط داخلياً */
        overscroll-behavior-y: contain !important;
    }
    
    /* إخفاء الهيدر الذي تستخدمه الحلقة للظهور */
    header { visibility: hidden !important; }
    </style>

    <script>
    // جافا سكريبت تعترض الحدث قبل أن يراه المتصفح
    document.addEventListener('touchmove', function(e) {
        if (window.scrollY <= 1) {
            // إذا حاول المستخدم السحب وهو في الأعلى، نوقف العملية تماماً
            e.stopPropagation();
        }
    }, { passive: false });
    </script>
""", unsafe_allow_html=True)

# --- 2. محرك البيانات والإعدادات ---
def load_settings():
    safe_id = "".join(x for x in (st.session_state.get('user_code', 'admin')) if x.isalnum())
    p = f"config_{safe_id}.json"
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8") as f: return json.load(f)
    return {"lab_name": "SmartLab Pro", "doctor_name": "Admin"}

if 'user_code' not in st.session_state: st.session_state.user_code = None

# --- 3. شاشة الدخول ---
if st.session_state.user_code is None:
    _, col, _ = st.columns([0.1, 0.8, 0.1])
    with col:
        st.markdown("<br><br><center><img src='https://cdn-icons-png.flaticon.com/512/3063/3063205.png' width='80'></center>", unsafe_allow_html=True)
        st.title("BioLab Ultra")
        u = st.text_input("رمز الدخول", type="password")
        if st.button("دخول للنظام", use_container_width=True, type="primary"):
            st.session_state.user_code = u
            st.rerun()
else:
    # --- 4. التطبيق الرئيسي ---
    user_settings = load_settings()
    safe_id = "".join(x for x in st.session_state.user_code if x.isalnum())
    db_file = f"private_db_{safe_id}.csv"
    
    if 'df' not in st.session_state:
        st.session_state.df = pd.read_csv(db_file) if os.path.exists(db_file) else pd.DataFrame(columns=["ID", "التاريخ", "المريض", "الفحص", "النتيجة", "الحالة", "الهاتف"])

    # الواجهة الاحترافية
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); padding:20px; border-radius:15px; color:white; margin-bottom:15px;">
            <h3 style="margin:0;">{user_settings.get('lab_name')}</h3>
            <p style="margin:0; opacity:0.8;">د. {user_settings.get('doctor_name')}</p>
        </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📋 السجلات", "🧪 فحص جديد", "⚙️ الإعدادات"])

    with tab1:
        search = st.text_input("🔍 بحث...")
        df_display = st.session_state.df
        if search:
            df_display = df_display[df_display['المريض'].str.contains(search, na=False)]
        
        for idx, row in df_display.iloc[::-1].head(10).iterrows():
            st.markdown(f"""
                <div style="background:white; padding:12px; border-radius:10px; margin-bottom:8px; border-right:5px solid #1e3a8a; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                    <b>👤 {row['المريض']}</b><br>
                    <small>{row['الفحص']} - {row['التاريخ']}</small><br>
                    النتيجة: <b>{row['النتيجة']}</b>
                </div>
            """, unsafe_allow_html=True)

    with tab2:
        with st.form("lab_form", clear_on_submit=True):
            name = st.text_input("اسم المريض")
            test = st.selectbox("التحليل", ["CBC", "HbA1c", "Glucose"])
            val = st.number_input("النتيجة")
            if st.form_submit_button("حفظ ✅", use_container_width=True):
                new_row = pd.DataFrame([[datetime.now().strftime("%H%M"), datetime.now().strftime("%Y-%m-%d"), name, test, val, "Normal", ""]], columns=st.session_state.df.columns)
                st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
                st.session_state.df.to_csv(db_file, index=False)
                st.toast("تم الحفظ!")

    with tab3:
        if st.button("تسجيل الخروج 🚪", use_container_width=True):
            st.session_state.user_code = None
            st.rerun()
