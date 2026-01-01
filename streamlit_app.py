import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import io

# --- 1. هندسة الواجهة والمنع المطلق للتحديث ---
st.set_page_config(page_title="BioLab Intelligence Pro", page_icon="🧬", layout="wide")

st.markdown("""
    <style>
    @media print {
        .no-print { display: none !important; }
        .print-only { display: block !important; }
        [data-testid="stHeader"], [data-testid="stSidebar"], .stTabs { display: none !important; }
    }
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
    .status-card {
        padding: 15px; border-radius: 12px; margin-bottom: 10px;
        border-right: 8px solid; transition: transform 0.3s;
    }
    .status-card:hover { transform: scale(1.01); }
    .critical-red { background: #fef2f2; border-right-color: #ef4444; color: #991b1b; }
    .warning-yellow { background: #fffbeb; border-right-color: #f59e0b; color: #92400e; }
    .normal-green { background: #f0fdf4; border-right-color: #10b981; color: #065f46; }
    
    .critical-alert-box {
        background: #7f1d1d; color: white; padding: 20px; border-radius: 15px;
        border: 4px solid #f87171; animation: blinker 1.5s linear infinite;
        margin: 10px 0; text-align: center; font-weight: bold;
    }
    @keyframes blinker { 50% { opacity: 0.5; } }

    .report-paper {
        background: white; border: 2px solid #334155; padding: 40px;
        border-radius: 5px; color: black; font-family: 'Arial', sans-serif;
        box-shadow: 0 0 20px rgba(0,0,0,0.1); margin: 20px auto; max-width: 800px;
    }
    .report-header { border-bottom: 3px solid #1e40af; padding-bottom: 20px; margin-bottom: 30px; }
    .report-table { width: 100%; border-collapse: collapse; margin-top: 20px; }
    .report-table th, .report-table td { border-bottom: 1px solid #e2e8f0; padding: 12px; text-align: right; }
    .report-table th { background-color: #f8fafc; color: #1e40af; }

    .patient-info-box {
        background: #f8fafc; border: 1px solid #e2e8f0; padding: 25px;
        border-radius: 20px; border-left: 8px solid #1e40af; margin-bottom: 25px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .header-style {
        background: linear-gradient(135deg, #0f172a 0%, #1e40af 100%);
        padding: 35px; border-radius: 25px; color: white;
        margin-bottom: 30px; box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    }
    header { visibility: hidden !important; }
    </style>
""", unsafe_allow_html=True)

# --- 2. نظام الهوية الثابتة ---
OWNER_INFO = {
    "PERMANENT_LAB_NAME": "مختبر النخبة التخصصي",
    "PERMANENT_DOC_NAME": "د. أحمد المصطفى",
    "SYSTEM_VERSION": "v23.0 Pro Printing Edition",
    "LICENSE_KEY": "PREMIUM-2026-X"
}

# --- 3. الموسوعة الطبية الشاملة ---
LAB_CATALOG = {
    "Hematology (أمراض الدم)": {
        "DefaultTube": "Purple (EDTA) 🟣", "Stability": 24,
        "Tests": {
            "CBC": (12, 16, "g/dL", 15), "HGB": (12, 18, "g/dL", 10), "PLT": (150, 450, "10^3/uL", 12),
            "WBC": (4, 11, "10^3/uL", 10), "ESR": (0, 20, "mm/hr", 8), "PCV": (37, 52, "%", 10),
            "PT": (11, 13.5, "sec", 15), "PTT": (25, 35, "sec", 15), "Blood Group": (0, 0, "Type", 5)
        },
        "Criticals": {"HGB": (7, 20), "PLT": (50, 800)}
    },
    "Biochemistry (الكيمياء الحيوية)": {
        "DefaultTube": "Yellow (Gel) 🟡", "Stability": 48,
        "Tests": {
            "Glucose (Fasting)": (70, 100, "mg/dL", 5), "HbA1c": (4, 5.6, "%", 25), "Urea": (15, 45, "mg/dL", 10),
            "Creatinine": (0.6, 1.2, "mg/dL", 15), "Albumin": (3.4, 5.4, "g/dL", 12), "Total Protein": (6.4, 8.3, "g/dL", 10)
        },
        "Criticals": {"Glucose (Fasting)": (45, 350), "Creatinine": (0.2, 5.0)}
    }
}
TUBE_TYPES = ["Purple (EDTA) 🟣", "Yellow (Gel) 🟡", "Red (Plain) 🔴", "Blue (Citrate) 🔵"]

# --- 4. وظائف تصدير التقارير ---
def export_to_excel(patient_df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        patient_df.to_excel(writer, index=False, sheet_name='Medical_Report')
    return output.getvalue()

def get_file_path(extension):
    user_id = "".join(x for x in (st.session_state.get('user_code', 'default')) if x.isalnum())
    return f"biolab_data_{user_id}.{extension}"

def load_user_profile():
    path = get_file_path("json")
    if os.path.exists(path): return json.load(open(path, "r", encoding="utf-8"))
    return {"lab_name": OWNER_INFO["PERMANENT_LAB_NAME"], "doc_name": OWNER_INFO["PERMANENT_DOC_NAME"], "currency": "$", "daily_target": 1000}

def get_result_analysis(cat, test, val):
    data = LAB_CATALOG[cat]["Tests"][test]
    low, high = data[0], data[1]
    if low == 0 and high == 0: return "طبيعي 🟢", "normal-green"
    if val < low: return "منخفض 🔵", "critical-red"
    if val > high: return "مرتفع 🔴", "critical-red"
    return "طبيعي 🟢", "normal-green"

# --- 5. منطق واجهة المستخدم الرئيسي ---
if 'user_code' not in st.session_state: st.session_state.user_code = None

if st.session_state.user_code is None:
    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        st.markdown("<br><h1 style='text-align:center;'>🧬 BioLab Intelligence</h1>", unsafe_allow_html=True)
        code_input = st.text_input("أدخل رمز الوصول الخاص بك", type="password")
        if st.button("فتح النظام الآمن", use_container_width=True, type="primary"):
            st.session_state.user_code = code_input; st.rerun()
else:
    profile = load_user_profile()
    db_path, inv_path = get_file_path("csv"), get_file_path("inv.csv")
    db_cols = ["PID", "Date", "Timestamp", "Patient", "Age", "Gender", "Category", "Test", "Result", "Unit", "Status", "Price", "Tube", "LabName", "DoctorName"]
    df = pd.read_csv(db_path) if os.path.exists(db_path) else pd.DataFrame(columns=db_cols)
    inv_df = pd.read_csv(inv_path) if os.path.exists(inv_path) else pd.DataFrame(columns=["Item", "Stock", "Expiry", "Unit"])

    st.markdown(f"""<div class="header-style no-print"><div style="display:flex; justify-content:space-between;"><div><h1>{profile['lab_name']}</h1><p>{profile['doc_name']}</p></div><div style="text-align:right;"><h3>{datetime.now().strftime('%Y-%m-%d')}</h3></div></div></div>""", unsafe_allow_html=True)

    tabs = st.tabs(["📊 الإحصائيات", "🧪 تسجيل فحص", "👤 ملف المريض", "📄 ورقة الطباعة", "📂 الأرشيف", "📦 المخزون", "🧠 تحليل AI", "💰 المالية", "⚙️ الإعدادات"])

    with tabs[1]: # تسجيل فحص
        with st.form("entry_form", clear_on_submit=True):
            ca, cb, cc = st.columns([2, 1, 1])
            p_name = ca.text_input("اسم المريض")
            p_age = cb.number_input("العمر", 1, 120, 25)
            p_gender = cc.selectbox("الجنس", ["ذكر", "أنثى"])
            p_id = st.text_input("PID", value=datetime.now().strftime("%H%M%S"))
            cd, ce = st.columns(2)
            cat_sel = cd.selectbox("القسم", list(LAB_CATALOG.keys()))
            test_sel = ce.selectbox("التحليل", list(LAB_CATALOG[cat_sel]["Tests"].keys()))
            res_val = st.number_input(f"النتيجة", format="%.2f")
            
            crit_data = LAB_CATALOG[cat_sel].get("Criticals", {}).get(test_sel)
            if crit_data and (res_val < crit_data[0] or res_val > crit_data[1]):
                st.markdown(f"""<div class="critical-alert-box">⚠️ تنبيه قيمة حرجة: {res_val}!</div>""", unsafe_allow_html=True)

            if st.form_submit_button("حفظ النتيجة 🚀", use_container_width=True):
                status, _ = get_result_analysis(cat_sel, test_sel, res_val)
                new_row = [p_id, datetime.now().strftime("%Y-%m-%d"), datetime.now().strftime("%Y-%m-%d %H:%M"), p_name, p_age, p_gender, cat_sel, test_sel, res_val, LAB_CATALOG[cat_sel]["Tests"][test_sel][2], status, LAB_CATALOG[cat_sel]["Tests"][test_sel][3], LAB_CATALOG[cat_sel]["DefaultTube"], profile['lab_name'], profile['doc_name']]
                df = pd.concat([df, pd.DataFrame([new_row], columns=df.columns)], ignore_index=True)
                df.to_csv(db_path, index=False); st.success("تم الحفظ!")

    with tabs[2]: # ملف المريض
        if not df.empty:
            p_pick = st.selectbox("اختر المريض لاستعراض ملفه", df['Patient'].unique(), key="patient_sel_main")
            p_hist = df[df['Patient'] == p_pick]
            st.dataframe(p_hist[['Timestamp', 'Test', 'Result', 'Status']], use_container_width=True)
            excel_data = export_to_excel(p_hist)
            st.download_button(label="📥 تحميل السجل الكامل (Excel)", data=excel_data, file_name=f"Report_{p_pick}.xlsx", mime="application/vnd.ms-excel")

    with tabs[3]: # ورقة الطباعة (الميزة الجديدة المطلوبة)
        st.subheader("🖨️ تجهيز ورقة التحليل النهائية")
        if not df.empty:
            target_patient = st.selectbox("اختر المريض للطباعة", df['Patient'].unique(), key="print_sel")
            target_data = df[df['Patient'] == target_patient]
            latest = target_data.iloc[-1]
            
            # عرض الورقة بشكل يحاكي الحقيقة
            st.markdown(f"""
            <div class="report-paper">
                <div class="report-header">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div style="text-align:right;">
                            <h2 style="color:#1e40af; margin:0;">{profile['lab_name']}</h2>
                            <p style="margin:2px;">إشراف: {profile['doc_name']}</p>
                        </div>
                        <div style="text-align:left; font-size:0.9em; color:#64748b;">
                            <p style="margin:2px;">التاريخ: {latest['Date']}</p>
                            <p style="margin:2px;">الوقت: {latest['Timestamp'].split(' ')[1]}</p>
                            <p style="margin:2px;">رقم الملف: {latest['PID']}</p>
                        </div>
                    </div>
                </div>
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:20px; background:#f1f5f9; padding:15px; border-radius:8px; margin-bottom:20px;">
                    <div><b>الاسم:</b> {latest['Patient']}</div>
                    <div><b>العمر:</b> {latest['Age']}</div>
                    <div><b>الجنس:</b> {latest['Gender']}</div>
                    <div><b>الحالة:</b> مراجع خارجي</div>
                </div>
                <table class="report-table">
                    <thead>
                        <tr>
                            <th>التحليل (Test Name)</th>
                            <th>النتيجة (Result)</th>
                            <th>الوحدة (Unit)</th>
                            <th>المدى الطبيعي (Normal Range)</th>
                        </tr>
                    </thead>
                    <tbody>
                        {"".join([f"<tr><td>{r['Test']}</td><td><b>{r['Result']}</b></td><td>{r['Unit']}</td><td>{LAB_CATALOG.get(r['Category'], {}).get('Tests', {}).get(r['Test'], (0,0))[0]} - {LAB_CATALOG.get(r['Category'], {}).get('Tests', {}).get(r['Test'], (0,0))[1]}</td></tr>" for _, r in target_data.iterrows()])}
                    </tbody>
                </table>
                <div style="margin-top:50px; display:flex; justify-content:space-between; font-size:0.8em; border-top: 1px solid #e2e8f0; padding-top:10px;">
                    <p>توقيع الطبيب المختص: _________________</p>
                    <p>ختم المختبر الرسمي</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🖨️ طباعة التقرير"):
                st.write("يرجى استخدام Ctrl+P (أو Cmd+P على Mac) لاختيار الطابعة وحفظ التقرير.")
        else:
            st.warning("لا توجد بيانات متاحة للطباعة حالياً.")

    with tabs[0]: # الإحصائيات
        c1, c2, c3 = st.columns(3)
        c1.metric("إجمالي المرضى", len(df['Patient'].unique()))
        c2.metric("دخل اليوم", f"{df[df['Date']==datetime.now().strftime('%Y-%m-%d')]['Price'].sum()} {profile['currency']}")
        c3.metric("الفحوصات المنفذة", len(df))

    with tabs[5]: # المخزن
        st.subheader("📦 إدارة المخزون")
        st.dataframe(inv_df, use_container_width=True)

    with tabs[8]: # الإعدادات
        if st.button("تسجيل الخروج"): st.session_state.user_code = None; st.rerun()

    st.markdown(f"<center style='opacity:0.2;'>{OWNER_INFO['SYSTEM_VERSION']}</center>", unsafe_allow_html=True)

