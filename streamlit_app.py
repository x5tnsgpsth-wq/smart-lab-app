import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime
import plotly.express as px
import io

# --- 1. محرك الإعدادات ---
def get_status(test, result):
    ranges = {"Glucose (Fasting)": (70, 100), "HbA1c": (4, 5.7), "Uric Acid": (3.5, 7.2), "Calcium": (8.5, 10.5)}
    if test in ranges:
        l, h = ranges[test]
        return "🔴 Low" if result < l else "🟡 High" if result > h else "🟢 Normal"
    return "⚪ Not Set"

def load_settings():
    if 'user_code' not in st.session_state or not st.session_state.user_code: return {}
    safe_id = "".join(x for x in st.session_state.user_code if x.isalnum())
    p = f"config_{safe_id}.json"
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8") as f: return json.load(f)
    return {"lab_name": "SmartLab Pro", "doctor_name": "Admin"}

def save_settings(s):
    safe_id = "".join(x for x in st.session_state.user_code if x.isalnum())
    with open(f"config_{safe_id}.json", "w", encoding="utf-8") as f: json.dump(s, f, ensure_ascii=False)

# --- 2. إعدادات المنصة والقفل الجذري ---
st.set_page_config(page_title="BioLab Ultra", page_icon="🧬", layout="wide")

# هذا هو الكود الذي سيقتل حلقة التحميل نهائياً
st.markdown("""
    <style>
    /* 1. تجميد الصفحة الرئيسية للمتصفح تماماً */
    html, body, [data-testid="stAppViewContainer"] {
        overflow: hidden !important;
        position: fixed !important;
        width: 100% !important;
        height: 100% !important;
        overscroll-behavior: none !important;
    }

    /* 2. إنشاء منطقة تمرير داخلية لا يراها المتصفح كـ 'صفحة' */
    [data-testid="stMainViewContainer"] {
        overflow-y: auto !important;
        height: 100vh !important;
        -webkit-overflow-scrolling: touch;
        overscroll-behavior-y: contain !important;
    }

    /* 3. تنسيقات إضافية للجمالية */
    .patient-card {
        background: #ffffff; padding: 15px; border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 10px;
        border-right: 5px solid #1e3a8a; color: #1e293b;
    }
    header, footer { visibility: hidden !important; }
    </style>
    
    <script>
    // تعطيل أحداث السحب الافتراضية لمنع المتصفح من التدخل
    document.addEventListener('touchmove', function (e) {
        if (e.target.tagName !== 'INPUT' && e.target.tagName !== 'TEXTAREA') {
            // السماح بالتمرير فقط داخل حاوية ستريمليت
        }
    }, { passive: false });
    </script>
""", unsafe_allow_html=True)

if 'user_code' not in st.session_state: st.session_state.user_code = None

# --- 3. شاشة الدخول ---
if st.session_state.user_code is None:
    _, col, _ = st.columns([0.1, 0.8, 0.1])
    with col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.title("BioLab Ultra")
        u = st.text_input("رمز الدخول", type="password")
        if st.button("دخول", use_container_width=True, type="primary"):
            st.session_state.user_code = u
            st.rerun()
else:
    # --- 4. التطبيق الرئيسي ---
    user_settings = load_settings()
    safe_id = "".join(x for x in st.session_state.user_code if x.isalnum())
    db_file = f"private_db_{safe_id}.csv"
    
    if 'df' not in st.session_state:
        st.session_state.df = pd.read_csv(db_file) if os.path.exists(db_file) else pd.DataFrame(columns=["ID", "التاريخ", "المريض", "الفحص", "النتيجة", "الحالة", "الهاتف"])

    st.markdown(f"""<div style="background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); padding:20px; border-radius:20px; color:white; margin-bottom:20px;">
        <h2 style="margin:0;">{user_settings.get('lab_name')}</h2><p style="margin:0; opacity:0.8;">د. {user_settings.get('doctor_name')}</p></div>""", unsafe_allow_html=True)

    t1, t2, t3, t4 = st.tabs(["📋 السجلات", "🧪 إضافة", "📈 إحصائيات", "⚙️ الإعدادات"])

    with t1:
        search = st.text_input("🔍 بحث...", key="search_input")
        filtered = st.session_state.df
        if search: filtered = filtered[filtered['المريض'].str.contains(search, na=False)]
        
        for i, r in filtered.iloc[::-1].head(15).iterrows():
            st.markdown(f'<div class="patient-card"><b>👤 {r["المريض"]}</b><br>{r["الفحص"]}: {r["النتيجة"]} <span style="float:left;">{r["الحالة"]}</span></div>', unsafe_allow_html=True)

    with t2:
        with st.form("add_form", clear_on_submit=True):
            n = st.text_input("اسم المريض")
            test = st.selectbox("الفحص", ["CBC", "Glucose", "HbA1c", "Urea"])
            res = st.number_input("النتيجة", step=0.01)
            if st.form_submit_button("حفظ ✅", use_container_width=True):
                if n:
                    status = get_status(test, res)
                    new = pd.DataFrame([[datetime.now().strftime("%H%M%S"), datetime.now().strftime("%Y-%m-%d"), n, test, res, status, ""]], columns=st.session_state.df.columns)
                    st.session_state.df = pd.concat([st.session_state.df, new], ignore_index=True)
                    st.session_state.df.to_csv(db_file, index=False)
                    st.toast("تم الحفظ بنجاح")
                else: st.error("أدخل الاسم")

    with t3:
        if not st.session_state.df.empty:
            st.plotly_chart(px.pie(st.session_state.df, names='الحالة', hole=0.3), use_container_width=True)

    with t4:
        nl = st.text_input("اسم المختبر", value=user_settings.get('lab_name'))
        nd = st.text_input("الطبيب", value=user_settings.get('doctor_name'))
        if st.button("حفظ الإعدادات"):
            save_settings({"lab_name": nl, "doctor_name": nd})
            st.toast("تم التحديث")
        if st.button("خروج"):
            st.session_state.clear()
            st.rerun()
