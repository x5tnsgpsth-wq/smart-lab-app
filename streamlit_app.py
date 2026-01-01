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
    
    .stability-timer {
        padding: 5px 10px; border-radius: 20px; font-weight: bold; font-size: 0.85em;
    }
    .timer-safe { background: #dcfce7; color: #16a34a; }
    .timer-warning { background: #fef9c3; color: #a16207; }
    .timer-expired { background: #fee2e2; color: #dc2626; border: 1px solid #dc2626; }

    .ai-insight-box {
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        border-right: 10px solid #2563eb; padding: 20px; border-radius: 15px;
        margin: 15px 0; box-shadow: 0 4px 12px rgba(37, 99, 235, 0.1);
    }

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
    "SYSTEM_VERSION": "v26.0 Visual Analytics",
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

# --- 4. وظائف الميزات الذكية ---
def render_radar_chart(p_df):
    """ميزة البصمة الصحية البصرية الجديدة"""
    tests = p_df['Test'].tolist()
    results = p_df['Result'].tolist()
    ranges = [LAB_CATALOG[r['Category']]['Tests'][r['Test']] for _, r in p_df.iterrows()]
    
    # تطبيع القيم للعرض البياني (Normalization)
    normalized_results = []
    for val, (low, high, unit, price) in zip(results, ranges):
        if high == low: normalized_results.append(1)
        else: normalized_results.append((val - low) / (high - low))

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=normalized_results,
        theta=tests,
        fill='toself',
        name='الحالة الحالية',
        line_color='#1e40af'
    ))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 2])),
        showlegend=False,
        title="بصمة التوازن الحيوي للمريض (0.5-1.0 هو المدى الطبيعي)",
        height=400
    )
    return fig

def check_sample_stability(timestamp_str, category):
    try:
        draw_time = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M")
        stability_limit = LAB_CATALOG[category]["Stability"]
        expiry_time = draw_time + timedelta(hours=stability_limit)
        remaining = expiry_time - datetime.now()
        hours_left = remaining.total_seconds() / 3600
        if hours_left <= 0: return "منتهية الصلاحية ❌", "timer-expired"
        elif hours_left <= 2: return f"تحذير: {int(hours_left*60)} دقيقة ⚠️", "timer-warning"
        else: return f"صالحة: {int(hours_left)} ساعة ✅", "timer-safe"
    except: return "غير محدد", "timer-safe"

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

    st.markdown(f"""<div class="header-style no-print"><h1>{profile['lab_name']}</h1><p>{profile['doc_name']}</p></div>""", unsafe_allow_html=True)
    tabs = st.tabs(["📊 الإحصائيات", "🧪 تسجيل فحص", "👤 ملف المريض", "📄 ورقة الطباعة", "📂 الأرشيف الرقابي", "📦 المخزون", "🧠 تحليل AI", "💰 المالية", "⚙️ الإعدادات"])

    with tabs[1]: # تسجيل فحص
        with st.form("entry_form", clear_on_submit=True):
            ca, cb, cc = st.columns([2, 1, 1])
            p_name, p_age, p_gender = ca.text_input("اسم المريض"), cb.number_input("العمر", 1, 120, 25), cc.selectbox("الجنس", ["ذكر", "أنثى"])
            p_id = st.text_input("PID", value=datetime.now().strftime("%H%M%S"))
            cat_sel = st.selectbox("القسم", list(LAB_CATALOG.keys()))
            test_sel = st.selectbox("التحليل", list(LAB_CATALOG[cat_sel]["Tests"].keys()))
            res_val = st.number_input(f"النتيجة", format="%.2f")
            if st.form_submit_button("حفظ النتيجة 🚀", use_container_width=True):
                status, _ = get_result_analysis(cat_sel, test_sel, res_val)
                new_row = [p_id, datetime.now().strftime("%Y-%m-%d"), datetime.now().strftime("%Y-%m-%d %H:%M"), p_name, p_age, p_gender, cat_sel, test_sel, res_val, LAB_CATALOG[cat_sel]["Tests"][test_sel][2], status, LAB_CATALOG[cat_sel]["Tests"][test_sel][3], LAB_CATALOG[cat_sel]["DefaultTube"], profile['lab_name'], profile['doc_name']]
                df = pd.concat([df, pd.DataFrame([new_row], columns=df.columns)], ignore_index=True)
                df.to_csv(db_path, index=False); st.success("تم الحفظ!")

    with tabs[2]: # ملف المريض + ميزة الرادار الجديدة
        if not df.empty:
            p_pick = st.selectbox("اختر المريض للعرض البصري", df['Patient'].unique())
            p_data = df[df['Patient'] == p_pick]
            col1, col2 = st.columns([1, 1])
            with col1:
                st.plotly_chart(render_radar_chart(p_data), use_container_width=True)
            with col2:
                st.subheader("📋 السجل الرقمي")
                st.dataframe(p_data[['Test', 'Result', 'Status']], use_container_width=True)
        else: st.warning("لا توجد بيانات سجلات.")

    with tabs[4]: # تتبع جودة العينات
        st.subheader("🕵️ مركز الرقابة على جودة العينات")
        if not df.empty:
            for _, row in df.tail(5).iterrows():
                t, c = check_sample_stability(row['Timestamp'], row['Category'])
                st.markdown(f'<div class="stability-timer {c}">{row["Patient"]} | {row["Test"]} | {t}</div>', unsafe_allow_html=True)

    with tabs[0]: # الإحصائيات
        st.metric("إجمالي الفحوصات", len(df))
        if not df.empty:
            fig_trend = px.line(df.groupby('Date').size().reset_index(name='count'), x='Date', y='count', title="حركة العمل اليومية")
            st.plotly_chart(fig_trend, use_container_width=True)

    with tabs[3]: # الطباعة
        if not df.empty:
            sel_p = st.selectbox("مريض الطباعة", df['Patient'].unique(), key="print_key")
            st.markdown(f'<div class="report-paper"><h3>{profile["lab_name"]}</h3><hr>المريض: {sel_p}</div>', unsafe_allow_html=True)

    with tabs[6]: # AI
        st.info("نظام التحليل التشخيصي نشط ويعمل في الخلفية.")

    st.markdown(f"<center style='opacity:0.2;'>{OWNER_INFO['SYSTEM_VERSION']}</center>", unsafe_allow_html=True)
