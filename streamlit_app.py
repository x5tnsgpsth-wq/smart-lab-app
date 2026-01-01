import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import io

# --- 1. هندسة الواجهة والمنع المطلق للتحديث (النسخة الاحترافية) ---
st.set_page_config(page_title="BioLab Intelligence Pro", page_icon="🧬", layout="wide")

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
    /* تصميم البطاقات الذكية */
    .status-card {
        padding: 15px; border-radius: 12px; margin-bottom: 10px;
        border-right: 8px solid; transition: transform 0.3s;
    }
    .status-card:hover { transform: scale(1.01); }
    .critical-red { background: #fef2f2; border-right-color: #ef4444; color: #991b1b; }
    .warning-yellow { background: #fffbeb; border-right-color: #f59e0b; color: #92400e; }
    .normal-green { background: #f0fdf4; border-right-color: #10b981; color: #065f46; }
    
    .header-style {
        background: linear-gradient(135deg, #0f172a 0%, #1e40af 100%);
        padding: 35px; border-radius: 25px; color: white;
        margin-bottom: 30px; box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    }
    header { visibility: hidden !important; }
    </style>
""", unsafe_allow_html=True)

# --- 2. الموسوعة الطبية الموسعة (قاعدة بيانات معيارية) ---
LAB_CATALOG = {
    "Hematology": {
        "CBC": (12, 16, "g/dL", 15), "HGB": (12, 18, "g/dL", 10), "PLT": (150, 450, "10^3/uL", 12),
        "WBC": (4, 11, "10^3/uL", 10), "ESR": (0, 20, "mm/hr", 8), "PCV": (37, 52, "%", 10)
    },
    "Biochemistry": {
        "Glucose (Fasting)": (70, 100, "mg/dL", 5), "HbA1c": (4, 5.6, "%", 25), "Urea": (15, 45, "mg/dL", 10),
        "Creatinine": (0.6, 1.2, "mg/dL", 15), "Uric Acid": (3.5, 7.2, "mg/dL", 10), "ALT (GPT)": (7, 56, "U/L", 12),
        "AST (GOT)": (10, 40, "U/L", 12), "ALP": (44, 147, "U/L", 15), "Albumin": (3.4, 5.4, "g/dL", 12)
    },
    "Hormones": {
        "TSH": (0.4, 4.0, "mIU/L", 30), "Free T4": (0.8, 1.8, "ng/dL", 30), "Prolactin": (4, 23, "ng/mL", 35),
        "Vitamin D3": (30, 100, "ng/mL", 50), "Ferritin": (20, 250, "ng/mL", 25), "PSA": (0, 4, "ng/mL", 40)
    },
    "Immunology": {
        "CRP": (0, 5, "mg/L", 15), "RF": (0, 20, "IU/mL", 20), "ASO": (0, 200, "IU/mL", 20)
    }
}

# --- 3. إدارة البيانات الذكية ---
def get_file_path(extension):
    user_id = "".join(x for x in (st.session_state.get('user_code', 'default')) if x.isalnum())
    return f"biolab_intel_{user_id}.{extension}"

def load_lab_settings():
    path = get_file_path("json")
    if os.path.exists(path): return json.load(open(path, "r", encoding="utf-8"))
    return {"lab_name": "مركز التحاليل الذكي", "doc_name": "المشرف العام", "currency": "$"}

def get_result_analysis(test, val):
    for cat in LAB_CATALOG.values():
        if test in cat:
            low, high, unit, price = cat[test]
            if val < low: return "منخفض 🔵", "critical-red"
            if val > high: return "مرتفع 🔴", "critical-red"
            return "طبيعي 🟢", "normal-green"
    return "غير محدد", "warning-yellow"

# --- 4. واجهة المستخدم الرسومية ---
if 'user_code' not in st.session_state: st.session_state.user_code = None

if st.session_state.user_code is None:
    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        st.markdown("<br><br><h1 style='text-align:center;'>🧬 BioLab Intelligence</h1>", unsafe_allow_html=True)
        code_input = st.text_input("رمز التشفير للدخول", type="password")
        if st.button("فتح النظام الآمن", use_container_width=True, type="primary"):
            st.session_state.user_code = code_input
            st.rerun()
else:
    settings = load_lab_settings()
    db_path = get_file_path("csv")
    df = pd.read_csv(db_path) if os.path.exists(db_path) else pd.DataFrame(columns=["PID", "Date", "Patient", "Category", "Test", "Result", "Unit", "Status", "Price"])

    # الهيدر الاحترافي
    st.markdown(f"""
        <div class="header-style">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div><h1 style="margin:0;">{settings['lab_name']}</h1><p style="margin:0; opacity:0.8;">إدارة الدكتور: {settings['doc_name']}</p></div>
                <div style="text-align:right;"><h3>{datetime.now().strftime('%Y-%m-%d')}</h3><p style="margin:0;">نظام النسخة السحابية 2026</p></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 لوحة الإدارة", "🧪 تسجيل فحص", "📂 أرشيف المرضى", "💰 المالية", "⚙️ الإعدادات"])

    with tab1:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("إجمالي المرضى", len(df['Patient'].unique()))
        c2.metric("فحوصات اليوم", len(df[df['Date'] == datetime.now().strftime("%Y-%m-%d")]))
        c3.metric("إيرادات الشهر", f"{settings['currency']}{df['Price'].sum():,.0f}")
        c4.metric("حالات حرجة", len(df[df['Status'].str.contains("🔴|🔵")]))
        
        st.divider()
        if not df.empty:
            col_graph1, col_graph2 = st.columns(2)
            with col_graph1:
                fig_pie = px.sunburst(df, path=['Category', 'Status'], title="توزيع الفحوصات والحالة")
                st.plotly_chart(fig_pie, use_container_width=True)
            with col_graph2:
                fig_line = px.area(df.groupby('Date').sum().reset_index(), x='Date', y='Price', title="نمو الإيرادات اليومي")
                st.plotly_chart(fig_line, use_container_width=True)

    with tab2:
        with st.form("professional_entry", clear_on_submit=True):
            c_a, c_b = st.columns(2)
            p_name = c_a.text_input("اسم المريض الثلاثي")
            p_id = c_b.text_input("رقم الهوية / الكود", value=datetime.now().strftime("%y%m%d%H%S"))
            
            cat_sel = st.selectbox("تصنيف الفحص", list(LAB_CATALOG.keys()))
            test_sel = st.selectbox("نوع التحليل المطلوب", list(LAB_CATALOG[cat_sel].keys()))
            
            res_val = st.number_input(f"النتيجة الرقمية ({LAB_CATALOG[cat_sel][test_sel][2]})", format="%.2f")
            
            if st.form_submit_button("اعتماد النتيجة وإضافتها للسجل 🚀", use_container_width=True):
                if p_name:
                    status, _ = get_result_analysis(test_sel, res_val)
                    unit, price = LAB_CATALOG[cat_sel][test_sel][2], LAB_CATALOG[cat_sel][test_sel][3]
                    new_data = pd.DataFrame([[p_id, datetime.now().strftime("%Y-%m-%d"), p_name, cat_sel, test_sel, res_val, unit, status, price]], columns=df.columns)
                    df = pd.concat([df, new_data], ignore_index=True)
                    df.to_csv(db_path, index=False)
                    st.success(f"تم تسجيل {test_sel} للمريض {p_name} بنجاح")
                else: st.error("يرجى إدخال اسم المريض")

    with tab3:
        search_all = st.text_input("🔍 ابحث بالاسم، التاريخ، أو نوع الفحص...")
        f_df = df[df.astype(str).apply(lambda x: x.str.contains(search_all, case=False)).any(axis=1)] if search_all else df
        
        for _, row in f_df.iloc[::-1].iterrows():
            _, card_style = get_result_analysis(row['Test'], row['Result'])
            st.markdown(f"""
                <div class="status-card {card_style}">
                    <div style="display:flex; justify-content:space-between;">
                        <b>👤 {row['Patient']} (ID: {row['PID']})</b>
                        <span>📅 {row['Date']}</span>
                    </div>
                    <div style="margin-top:10px; display:flex; align-items:center; gap:20px;">
                        <span style="font-size:18px;">فحص: <b>{row['Test']}</b></span>
                        <span style="font-size:22px;">النتيجة: <b>{row['Result']} {row['Unit']}</b></span>
                        <span style="font-weight:bold;">[{row['Status']}]</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    with tab4:
        st.subheader("📊 التقارير المالية التفصيلية")
        st.dataframe(df[["Date", "Patient", "Test", "Price"]], use_container_width=True)
        col_ex1, col_ex2 = st.columns(2)
        if st.button("تصدير نسخة احتياطية (CSV)"):
            st.download_button("تحميل الملف الآن", df.to_csv(index=False).encode('utf-8-sig'), "Backup_Lab.csv", "text/csv")

    with tab5:
        st.subheader("🛠️ تخصيص هوية النظام")
        new_l = st.text_input("اسم المختبر", settings['lab_name'])
        new_d = st.text_input("الطبيب المسؤول", settings['doc_name'])
        new_c = st.selectbox("العملة", ["$", "IQD", "EGP", "SAR"])
        if st.button("حفظ الإعدادات الفنية 💾"):
            with open(get_file_path("json"), "w", encoding="utf-8") as f:
                json.dump({"lab_name": new_l, "doc_name": new_d, "currency": new_c}, f)
            st.rerun()
        
        st.divider()
        if st.button("خروج آمن 🚪", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    st.markdown("<center style='opacity:0.2; margin-top:40px;'>BioLab Intelligence v6.0 - 2026 Powered AI System</center>", unsafe_allow_html=True)
