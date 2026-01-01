import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime
import plotly.express as px
import io

# --- 1. القفل النووي المزدوج (Anti-Pull-to-Refresh) ---
st.set_page_config(page_title="BioLab Ultra Pro", page_icon="🧬", layout="wide")

st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] {
        overflow: hidden !important;
        position: fixed !important;
        width: 100% !important; height: 100% !important;
        overscroll-behavior-y: none !important;
        touch-action: none !important;
    }
    [data-testid="stMainViewContainer"] {
        overflow-y: auto !important;
        height: 100vh !important;
        -webkit-overflow-scrolling: touch !important;
        touch-action: pan-y !important;
        overscroll-behavior-y: contain !important;
    }
    .main-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
        padding: 25px; border-radius: 20px; color: white;
        margin-bottom: 25px; border-bottom: 4px solid #3b82f6;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    .patient-card {
        background: white; padding: 20px; border-radius: 15px;
        border-right: 6px solid #3b82f6; margin-bottom: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    header { visibility: hidden !important; }
    </style>
""", unsafe_allow_html=True)

# --- 2. الموسوعة الشاملة للتحاليل (أكثر من 80 فحص) ---
LAB_CATALOG = {
    "Hematology (أمراض الدم)": {
        "CBC": (12, 16), "HGB": (12, 18), "PLT": (150, 450), "WBC": (4, 11), "ESR": (0, 20), "PCV": (37, 52), "Reticulocytes": (0.5, 2.5), "PT": (11, 13.5)
    },
    "Biochemistry (الكيمياء الحيوية)": {
        "Glucose (Fasting)": (70, 100), "HbA1c": (4, 5.6), "Urea": (15, 45), "Creatinine": (0.6, 1.2), "Uric Acid": (3.5, 7.2), "ALT": (7, 56), "AST": (10, 40), "ALP": (44, 147), "Total Bilirubin": (0.1, 1.2), "Direct Bilirubin": (0, 0.3), "Albumin": (3.4, 5.4), "Amylase": (30, 110)
    },
    "Lipids (الدهون)": {
        "Total Cholesterol": (125, 200), "Triglycerides": (50, 150), "HDL": (40, 60), "LDL": (0, 100), "VLDL": (2, 30)
    },
    "Hormones & Tumors (الهرمونات والأورام)": {
        "TSH": (0.4, 4.0), "Free T4": (0.8, 1.8), "Free T3": (2.3, 4.2), "Prolactin": (4, 23), "PSA (Total)": (0, 4), "CEA": (0, 3), "CA 125": (0, 35), "AFP": (0, 8), "Cortisol (AM)": (5, 23), "Testosterone": (300, 1000)
    },
    "Vitamins & Minerals (الفيتامينات والمعادن)": {
        "Vitamin D3": (30, 100), "Vitamin B12": (200, 900), "Serum Iron": (60, 170), "Ferritin": (20, 250), "Calcium": (8.5, 10.5), "Potassium": (3.5, 5.1), "Sodium": (135, 145), "Magnesium": (1.7, 2.2), "Zinc": (60, 120)
    },
    "Immunology & Virology (المناعة والفيروسات)": {
        "CRP": (0, 5), "RF": (0, 20), "ASO": (0, 200), "HBsAg": (0, 0), "HCV Ab": (0, 0), "HIV": (0, 0), "Anti-CCP": (0, 20), "ANA": (0, 0)
    },
    "Urine & Stool (الأدوات والشوائب)": {
        "Urine Pus Cells": (0, 5), "Urine RBCs": (0, 3), "Stool Amoeba": (0, 0), "H-Pylori (Stool)": (0, 0)
    }
}

# --- 3. محرك الإعدادات والبيانات ---
def load_settings():
    safe_id = "".join(x for x in (st.session_state.get('user_code', 'default')) if x.isalnum())
    path = f"settings_{safe_id}.json"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f: return json.load(f)
    return {"lab_name": "SmartLab Pro", "doc_name": "Admin"}

def save_settings(s):
    safe_id = "".join(x for x in (st.session_state.get('user_code', 'default')) if x.isalnum())
    with open(f"settings_{safe_id}.json", "w", encoding="utf-8") as f: json.dump(s, f, ensure_ascii=False)

def check_status(test_name, res):
    for cat in LAB_CATALOG.values():
        if test_name in cat:
            low, high = cat[test_name]
            if res < low: return "🔴 Low", "#fee2e2"
            if res > high: return "🟡 High", "#fef9c3"
            return "🟢 Normal", "#dcfce7"
    return "⚪ N/A", "#f1f5f9"

# --- 4. واجهة التطبيق ---
if 'user_code' not in st.session_state: st.session_state.user_code = None

if st.session_state.user_code is None:
    _, col, _ = st.columns([0.1, 0.8, 0.1])
    with col:
        st.markdown("<br><br><center><h1>🧬 BioLab Ultra</h1></center>", unsafe_allow_html=True)
        u_code = st.text_input("رمز الدخول", type="password")
        if st.button("دخول", use_container_width=True, type="primary"):
            st.session_state.user_code = u_code
            st.rerun()
else:
    settings = load_settings()
    safe_id = "".join(x for x in st.session_state.user_code if x.isalnum())
    db_file = f"db_{safe_id}.csv"
    df = pd.read_csv(db_file) if os.path.exists(db_file) else pd.DataFrame(columns=["ID", "Date", "Patient", "Category", "Test", "Result", "Status"])

    # الهيدر القابل للتخصيص
    st.markdown(f"""
        <div class="main-header">
            <h1 style="margin:0;">{settings['lab_name']}</h1>
            <p style="margin:0; opacity:0.8;">بإشراف: د. {settings['doc_name']}</p>
        </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["📋 السجلات", "🧪 فحص جديد", "📊 الإحصائيات", "⚙️ الإعدادات"])

    with tab1:
        search = st.text_input("🔍 بحث عن مريض...")
        filtered = df[df['Patient'].str.contains(search, na=False)] if search else df
        for _, r in filtered.iloc[::-1].head(15).iterrows():
            st.markdown(f"""
                <div class="patient-card">
                    <div style="display:flex; justify-content:space-between;"><b>{r['Patient']}</b><small>{r['Date']}</small></div>
                    <div style="margin-top:10px;">{r['Test']}: <b>{r['Result']}</b> <span style="float:left; background:{check_status(r['Test'], r['Result'])[1]}; padding:2px 10px; border-radius:10px;">{r['Status']}</span></div>
                </div>
            """, unsafe_allow_html=True)

    with tab2:
        with st.form("lab_form", clear_on_submit=True):
            p_name = st.text_input("اسم المريض")
            cat_choice = st.selectbox("التصنيف", list(LAB_CATALOG.keys()))
            test_choice = st.selectbox("الفحص", list(LAB_CATALOG[cat_choice].keys()))
            res_val = st.number_input("النتيجة", format="%.2f")
            if st.form_submit_button("حفظ ✅", use_container_width=True):
                if p_name:
                    status, _ = check_status(test_choice, res_val)
                    new_data = pd.DataFrame([[datetime.now().strftime("%H%M"), datetime.now().strftime("%Y-%m-%d"), p_name, cat_choice, test_choice, res_val, status]], columns=df.columns)
                    df = pd.concat([df, new_data], ignore_index=True)
                    df.to_csv(db_file, index=False)
                    st.toast("تم الحفظ!")
                else: st.error("أدخل اسم المريض")

    with tab3:
        if not df.empty:
            st.plotly_chart(px.pie(df, names='Status', title="توزيع الحالات الصحية", hole=0.4), use_container_width=True)
            st.plotly_chart(px.bar(df, x='Category', title="أكثر الأقسام طلباً"), use_container_width=True)

    with tab4:
        st.subheader("🛠️ إعدادات المختبر")
        new_lab = st.text_input("اسم المختبر", value=settings['lab_name'])
        new_doc = st.text_input("اسم الدكتور المسؤول", value=settings['doc_name'])
        if st.button("حفظ الإعدادات 💾"):
            save_settings({"lab_name": new_lab, "doc_name": new_doc})
            st.success("تم تحديث البيانات")
            st.rerun()
        
        if st.button("خروج 🚪"):
            st.session_state.clear()
            st.rerun()
