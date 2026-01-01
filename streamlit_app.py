import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import io

# --- 1. القفل النووي لحلقة التحميل (Anti-Pull-to-Refresh) ---
st.set_page_config(page_title="BioLab Ultra Pro", page_icon="🧬", layout="wide")

st.markdown("""
    <style>
    /* تجميد المتصفح تماماً لمنع حلقة التحميل */
    html, body, [data-testid="stAppViewContainer"] {
        overflow: hidden !important;
        position: fixed !important;
        width: 100% !important; height: 100% !important;
        overscroll-behavior: none !important;
        touch-action: none !important;
    }
    /* منطقة العمل الداخلية فقط هي التي تتحرك */
    [data-testid="stMainViewContainer"] {
        overflow-y: auto !important;
        height: 100vh !important;
        -webkit-overflow-scrolling: touch !important;
        touch-action: pan-y !important;
        overscroll-behavior-y: contain !important;
    }
    .patient-card {
        background: #f8fafc; padding: 20px; border-radius: 15px;
        border-right: 8px solid #3b82f6; margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    .status-badge { padding: 4px 12px; border-radius: 20px; font-weight: bold; font-size: 12px; }
    header { visibility: hidden !important; }
    </style>
""", unsafe_allow_html=True)

# --- 2. موسوعة التحاليل المخبرية الشاملة (جميع التحاليل) ---
LAB_CATALOG = {
    "Hematology": {
        "CBC (Complete Blood Count)": (12, 16), "HGB": (12, 18), "PLT": (150, 450), "WBC": (4, 11),
        "ESR": (0, 20), "PCV": (37, 52)
    },
    "Biochemistry": {
        "Glucose (Fasting)": (70, 100), "HbA1c": (4, 5.6), "Urea": (15, 45), "Creatinine": (0.6, 1.2),
        "Uric Acid": (3.5, 7.2), "ALT (GPT)": (7, 56), "AST (GOT)": (10, 40), "ALP": (44, 147),
        "Bilirubin (Total)": (0.1, 1.2), "Albumin": (3.4, 5.4), "Total Protein": (6, 8.3)
    },
    "Lipid Profile": {
        "Cholesterol": (125, 200), "Triglycerides": (50, 150), "HDL": (40, 60), "LDL": (0, 100)
    },
    "Hormones & Vitamins": {
        "TSH": (0.4, 4.0), "Free T4": (0.8, 1.8), "Vitamin D3": (30, 100), "Vitamin B12": (200, 900),
        "Ferritin": (20, 250), "PSA": (0, 4), "Cortisol": (5, 23)
    },
    "Electrolytes & Minerals": {
        "Calcium": (8.5, 10.5), "Potassium": (3.5, 5.1), "Sodium": (135, 145), "Magnesium": (1.7, 2.2)
    },
    "Immunology": {
        "CRP": (0, 5), "Rheumatoid Factor": (0, 20), "ASO Titer": (0, 200)
    }
}

# --- 3. محرك الوظائف الذكي ---
def check_status(test_name, result):
    for cat in LAB_CATALOG.values():
        if test_name in cat:
            low, high = cat[test_name]
            if result < low: return "🔴 Low", "#fee2e2"
            if result > high: return "🟡 High", "#fef9c3"
            return "🟢 Normal", "#dcfce7"
    return "⚪ Not Set", "#f1f5f9"

def load_data():
    safe_id = "".join(x for x in (st.session_state.get('user_code', 'guest')) if x.isalnum())
    db = f"ultra_db_{safe_id}.csv"
    if os.path.exists(db): return pd.read_csv(db)
    return pd.DataFrame(columns=["ID", "Date", "Patient", "Category", "Test", "Result", "Status", "Phone"])

# --- 4. واجهة التطبيق ---
if 'user_code' not in st.session_state: st.session_state.user_code = None

if st.session_state.user_code is None:
    _, col, _ = st.columns([0.1, 0.8, 0.1])
    with col:
        st.markdown("<br><br><br><br><center><h1 style='font-size:50px;'>🧬</h1></center>", unsafe_allow_html=True)
        st.title("BioLab Ultra Pro")
        st.caption("نظام الإدارة المخبرية الفائق - الإصدار السحابي 2026")
        code = st.text_input("رمز الدخول السري", type="password")
        if st.button("دخول آمن للمختبر", use_container_width=True, type="primary"):
            st.session_state.user_code = code
            st.rerun()
else:
    df = load_data()
    
    # الهيدر الفائق
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1e293b 0%, #334155 100%); padding:30px; border-radius:20px; color:white; margin-bottom:25px; border-bottom: 5px solid #3b82f6;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div><h2 style="margin:0;">BioLab Control Center</h2><p style="margin:0; opacity:0.6;">نظام التحليل والبيانات المتكامل</p></div>
                <div style="text-align: right;"><h4 style="margin:0;">{datetime.now().strftime('%Y-%m-%d')}</h4></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["📋 الأرشيف الذكي", "🧪 إضافة تحليل", "📈 لوحة الإحصائيات", "⚙️ الإعدادات"])

    with tab1:
        search = st.text_input("🔍 ابحث عن مريض أو تحليل أو تاريخ...", placeholder="اكتب هنا للبحث الفوري...")
        filtered = df
        if search:
            filtered = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)]

        for _, r in filtered.iloc[::-1].iterrows():
            st.markdown(f"""
                <div class="patient-card">
                    <div style="display: flex; justify-content: space-between;">
                        <b>👤 {r['Patient']}</b>
                        <span>📅 {r['Date']}</span>
                    </div>
                    <div style="margin-top:15px; display: flex; align-items: center; gap: 15px;">
                        <span style="background:#e2e8f0; padding:4px 10px; border-radius:8px;">{r['Test']}</span>
                        <span style="font-size:20px;"><b>{r['Result']}</b></span>
                        <span class="status-badge" style="background:{check_status(r['Test'], r['Result'])[1]};">
                            {r['Status']}
                        </span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    with tab2:
        st.markdown("### 📥 تسجيل فحص جديد")
        with st.form("ultra_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            p_name = c1.text_input("اسم المريض الثلاثي")
            p_phone = c2.text_input("رقم هاتف المريض")
            
            cat_choice = st.selectbox("تصنيف التحليل", list(LAB_CATALOG.keys()))
            test_choice = st.selectbox("اسم التحليل المحدد", list(LAB_CATALOG[cat_choice].keys()))
            
            p_result = st.number_input("النتيجة الرقمية", format="%.2f")
            
            if st.form_submit_button("إرسال للبيانات وإصدار النتيجة 🚀", use_container_width=True):
                if p_name:
                    status, _ = check_status(test_choice, p_result)
                    new_entry = pd.DataFrame([[
                        datetime.now().strftime("%H%M%S"), datetime.now().strftime("%Y-%m-%d"),
                        p_name, cat_choice, test_choice, p_result, status, p_phone
                    ]], columns=df.columns)
                    df = pd.concat([df, new_entry], ignore_index=True)
                    df.to_csv(f"ultra_db_{''.join(x for x in st.session_state.user_code if x.isalnum())}.csv", index=False)
                    st.toast(f"تم تسجيل تحليل {test_choice} للمريض {p_name}", icon="✅")
                else: st.error("يرجى ملء الاسم")

    with tab3:
        if not df.empty:
            col_a, col_b = st.columns(2)
            with col_a:
                fig1 = px.sunburst(df, path=['Category', 'Test', 'Status'], title="توزيع الفحوصات والحالات")
                st.plotly_chart(fig1, use_container_width=True)
            with col_b:
                fig2 = px.histogram(df, x="Date", color="Status", barmode="group", title="تطور الحالات زمنياً")
                st.plotly_chart(fig2, use_container_width=True)
        else: st.info("لا توجد بيانات كافية للتحليل حالياً")

    with tab4:
        if st.button("🚪 تسجيل الخروج من النظام", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    st.markdown("<p style='text-align:center; opacity:0.3; margin-top:50px;'>BioLab Ultra Pro - Secured Infrastructure</p>", unsafe_allow_html=True)
