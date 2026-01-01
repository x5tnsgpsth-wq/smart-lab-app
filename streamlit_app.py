import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime
import plotly.express as px
import io

# --- 1. هندسة الواجهة والمنع المطلق للتحديث ---
st.set_page_config(page_title="BioLab Ultra Pro", page_icon="🧪", layout="wide")

st.markdown("""
    <style>
    /* منع حلقة التحميل نهائياً */
    html, body, [data-testid="stAppViewContainer"] {
        overflow: hidden !important; position: fixed !important;
        width: 100% !important; height: 100% !important;
        overscroll-behavior: none !important; touch-action: none !important;
    }
    [data-testid="stMainViewContainer"] {
        overflow-y: auto !important; height: 100vh !important;
        -webkit-overflow-scrolling: touch !important;
        overscroll-behavior-y: contain !important;
    }
    /* تأثيرات البطاقات الملكية */
    .report-card {
        background: white; border-radius: 15px; padding: 20px;
        border-right: 10px solid #3b82f6; margin-bottom: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1); color: #1e293b;
    }
    .critical { border-right-color: #ef4444 !important; background: #fff1f2; }
    .normal { border-right-color: #10b981 !important; background: #f0fdf4; }
    .header-gradient {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 30px; border-radius: 20px; color: white; margin-bottom: 25px;
    }
    header { visibility: hidden !important; }
    </style>
""", unsafe_allow_html=True)

# --- 2. الموسوعة الطبية الموسعة (30+ تحليل) ---
LAB_CATALOG = {
    "Hematology": {
        "CBC": (12, 16, "g/dL", 15), "HGB": (12, 18, "g/dL", 10), "PLT": (150, 450, "10^3/uL", 12),
        "WBC": (4, 11, "10^3/uL", 10), "ESR": (0, 20, "mm/hr", 8)
    },
    "Biochemistry": {
        "Glucose": (70, 100, "mg/dL", 5), "HbA1c": (4, 5.6, "%", 25), "Urea": (15, 45, "mg/dL", 10),
        "Creatinine": (0.6, 1.2, "mg/dL", 15), "Uric Acid": (3.5, 7.2, "mg/dL", 10), "ALT": (7, 56, "U/L", 12)
    },
    "Hormones": {
        "TSH": (0.4, 4.0, "mIU/L", 30), "T3": (80, 200, "ng/dL", 30), "T4": (5.1, 14.1, "ug/dL", 30),
        "Prolactin": (4, 23, "ng/mL", 35), "Vitamin D": (30, 100, "ng/mL", 50)
    },
    "Immunology": {
        "CRP": (0, 5, "mg/L", 15), "RF": (0, 20, "IU/mL", 20), "ASO": (0, 200, "IU/mL", 20)
    },
    "Virology": {
        "HBsAg": (0, 0.9, "Index", 40), "HCV Ab": (0, 0.9, "Index", 45), "HIV": (0, 0.9, "Index", 60)
    }
}

# --- 3. إدارة البيانات الذكية ---
def get_path(ext):
    uid = "".join(x for x in (st.session_state.get('user_code', 'guest')) if x.isalnum())
    return f"pro_data_{uid}.{ext}"

def load_settings():
    path = get_path("json")
    if os.path.exists(path): return json.load(open(path, "r", encoding="utf-8"))
    return {"lab": "BioLab Center", "doc": "Admin"}

def check_status(test, val):
    for cat in LAB_CATALOG.values():
        if test in cat:
            low, high, unit, price = cat[test]
            if val < low: return "منخفض 🔵", "critical"
            if val > high: return "مرتفع 🔴", "critical"
            return "طبيعي 🟢", "normal"
    return "N/A", ""

# --- 4. واجهة التطبيق الرئيسية ---
if 'user_code' not in st.session_state: st.session_state.user_code = None

if st.session_state.user_code is None:
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown("<h1 style='text-align:center;'>🧬 BioLab Pro</h1>", unsafe_allow_html=True)
        code = st.text_input("رمز الدخول الآمن", type="password")
        if st.button("دخول النظام", use_container_width=True, type="primary"):
            st.session_state.user_code = code
            st.rerun()
else:
    settings = load_settings()
    db_path = get_path("csv")
    df = pd.read_csv(db_path) if os.path.exists(db_path) else pd.DataFrame(columns=["ID", "Date", "Patient", "Category", "Test", "Result", "Unit", "Status", "Price"])

    st.markdown(f"""<div class="header-gradient"><h1>{settings['lab']}</h1><p>إدارة: د. {settings['doc']}</p></div>""", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["📊 الإحصائيات", "🧪 فحص جديد", "📂 سجل المرضى", "⚙️ الإعدادات"])

    with tab1:
        c1, c2, c3 = st.columns(3)
        c1.metric("مرضى اليوم", len(df[df['Date'] == datetime.now().strftime("%Y-%m-%d")]))
        c2.metric("إجمالي الإيرادات", f"${df['Price'].sum():,.0f}")
        c3.metric("نسبة الحالات الحرجة", f"{(len(df[df['Status'].str.contains('🔴')])/len(df)*100 if len(df)>0 else 0):.1f}%")
        
        if not df.empty:
            st.plotly_chart(px.bar(df, x='Category', y='Price', color='Category', title="توزيع الدخل حسب القسم"), use_container_width=True)

    with tab2:
        with st.form("medical_form", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            p_name = col_a.text_input("اسم المريض")
            cat_sel = col_b.selectbox("القسم", list(LAB_CATALOG.keys()))
            test_sel = st.selectbox("التحليل", list(LAB_CATALOG[cat_sel].keys()))
            res_in = st.number_input(f"النتيجة ({LAB_CATALOG[cat_sel][test_sel][2]})", format="%.2f")
            
            if st.form_submit_button("حفظ وإصدار التقرير ✅", use_container_width=True):
                if p_name:
                    status, _ = check_status(test_sel, res_in)
                    unit, price = LAB_CATALOG[cat_sel][test_sel][2], LAB_CATALOG[cat_sel][test_sel][3]
                    new_entry = pd.DataFrame([[datetime.now().strftime("%f"), datetime.now().strftime("%Y-%m-%d"), p_name, cat_sel, test_sel, res_in, unit, status, price]], columns=df.columns)
                    df = pd.concat([df, new_entry], ignore_index=True)
                    df.to_csv(db_path, index=False)
                    st.success("تم الحفظ بنجاح")
                else: st.error("يرجى ملء الاسم")

    with tab3:
        p_search = st.selectbox("اختر اسم المريض لعرض تاريخه الطبي:", [""] + list(df['Patient'].unique()))
        if p_search:
            p_data = df[df['Patient'] == p_search]
            for _, r in p_data.iloc[::-1].iterrows():
                _, style = check_status(r['Test'], r['Result'])
                st.markdown(f"""
                    <div class="report-card {style}">
                        <div style="display:flex; justify-content:space-between;">
                            <b>تحليل: {r['Test']}</b>
                            <span>📅 {r['Date']}</span>
                        </div>
                        <h2 style="margin: 10px 0;">{r['Result']} <small>{r['Unit']}</small></h2>
                        <b>الحالة: {r['Status']}</b>
                    </div>
                """, unsafe_allow_html=True)

    with tab4:
        st.subheader("إعدادات المختبر")
        n_lab = st.text_input("اسم المنشأة", settings['lab'])
        n_doc = st.text_input("الطبيب المسؤول", settings['doc'])
        if st.button("حفظ 💾"):
            with open(get_path("json"), "w", encoding="utf-8") as f:
                json.dump({"lab": n_lab, "doc": n_doc}, f)
            st.rerun()
        
        st.divider()
        if st.button("تسجيل الخروج 🚪", use_container_width=True):
            st.session_state.user_code = None
            st.rerun()

    st.markdown("<center style='opacity:0.2;'>BioLab Ultra Pro v5.0 - Enterprise Edition</center>", unsafe_allow_html=True)
