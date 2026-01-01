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
    "SYSTEM_VERSION": "v26.5 Final All-In-One",
    "LICENSE_KEY": "PREMIUM-2026-X"
}

# --- 3. الموسوعة الطبية الشاملة (كاملة دون حذف) ---
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

# --- 4. الوظائف الذكية والتحليلية ---
def render_radar_chart(p_df):
    """رسم الرادار التشخيصي لمقارنة النتائج بالمدى الطبيعي"""
    tests = p_df['Test'].tolist()
    results = p_df['Result'].tolist()
    normalized_results = []
    for _, r in p_df.iterrows():
        low, high = LAB_CATALOG[r['Category']]['Tests'][r['Test']][:2]
        if high == low: normalized_results.append(1)
        else: normalized_results.append((r['Result'] - low) / (high - low) if (high-low) != 0 else 1)
    
    fig = go.Figure(data=go.Scatterpolar(r=normalized_results, theta=tests, fill='toself', line_color='#1e40af'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 2])), showlegend=False, height=350, title="بصمة التوازن الحيوي")
    return fig

def check_sample_stability(timestamp_str, category):
    try:
        draw_time = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M")
        limit = LAB_CATALOG[category]["Stability"]
        expiry = draw_time + timedelta(hours=limit)
        rem = expiry - datetime.now()
        hrs = rem.total_seconds() / 3600
        if hrs <= 0: return "منتهية ❌", "timer-expired"
        elif hrs <= 2: return f"تحذير ({int(hrs*60)}د) ⚠️", "timer-warning"
        return f"صالحة ({int(hrs)}س) ✅", "timer-safe"
    except: return "غير محدد", "timer-safe"

def ai_diagnostic_logic(patient_data):
    insights = []
    tests = dict(zip(patient_data['Test'], patient_data['Result']))
    if "Creatinine" in tests and "Urea" in tests:
        if tests["Creatinine"] > 1.2 and tests["Urea"] > 45: insights.append("⚠️ **الكلى:** ارتفاع متزامن في اليوريا والكرياتينين.")
    if "HGB" in tests and tests["HGB"] < 11: insights.append("🩸 **الأنيميا:** انخفاض الهيموجلوبين يتطلب متابعة.")
    return insights if insights else ["✅ لا توجد تنبيهات تشخيصية حالياً."]

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

    tabs = st.tabs(["📊 الإحصائيات", "🧪 تسجيل فحص", "👤 ملف المريض", "📄 ورقة الطباعة", "📂 الأرشيف الرقابي", "📦 المخزون", "🧠 تحليل AI", "💰 المالية", "⚙️ الإعدادات"])

    with tabs[1]: # تسجيل فحص (كامل)
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

    with tabs[2]: # ملف المريض + الرادار البصري
        if not df.empty:
            p_pick = st.selectbox("اختر المريض", df['Patient'].unique(), key="p_file_sel")
            p_data = df[df['Patient'] == p_pick]
            c1, c2 = st.columns([1, 1])
            with c1: st.plotly_chart(render_radar_chart(p_data), use_container_width=True)
            with c2: st.dataframe(p_data[['Date', 'Test', 'Result', 'Status']], use_container_width=True)
            st.download_button("📥 تحميل Excel", export_to_excel(p_data), f"{p_pick}.xlsx")

    with tabs[3]: # ورقة الطباعة الاحترافية (كاملة)
        if not df.empty:
            target_p = st.selectbox("مريض الطباعة", df['Patient'].unique(), key="print_sel")
            t_data = df[df['Patient'] == target_p]
            latest = t_data.iloc[-1]
            st.markdown(f"""<div class="report-paper">
                <div class="report-header"><h2>{profile['lab_name']}</h2><p>إشراف: {profile['doc_name']}</p></div>
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px; background:#f8fafc; padding:10px; margin-bottom:15px;">
                    <div><b>الاسم:</b> {latest['Patient']}</div><div><b>العمر:</b> {latest['Age']}</div><div><b>التاريخ:</b> {latest['Date']}</div><div><b>PID:</b> {latest['PID']}</div>
                </div>
                <table class="report-table"><thead><tr><th>التحليل</th><th>النتيجة</th><th>الوحدة</th><th>المدى الطبيعي</th></tr></thead><tbody>
                {"".join([f"<tr><td>{r['Test']}</td><td><b>{r['Result']}</b></td><td>{r['Unit']}</td><td>{LAB_CATALOG[r['Category']]['Tests'][r['Test']][0]}-{LAB_CATALOG[r['Category']]['Tests'][r['Test']][1]}</td></tr>" for _, r in t_data.iterrows()])}
                </tbody></table><div style="margin-top:40px;">توقيع الطبيب المختص: _________________</div></div>""", unsafe_allow_html=True)
            st.button("🖨️ تنفيذ الطباعة", on_click=lambda: st.write("اضغط Ctrl+P"))

    with tabs[4]: # الأرشيف والرقابة
        st.subheader("🕵️ تتبع جودة العينات (Stability Live)")
        if not df.empty:
            for _, row in df.tail(10).iterrows():
                timer, t_class = check_sample_stability(row['Timestamp'], row['Category'])
                st.markdown(f'<div class="stability-timer {t_class}">{row["Patient"]} | {row["Test"]} | {timer}</div>', unsafe_allow_html=True)

    with tabs[0]: # الإحصائيات (كاملة)
        c1, c2, c3 = st.columns(3)
        c1.metric("إجمالي المرضى", len(df['Patient'].unique()))
        c2.metric("دخل اليوم", f"{df[df['Date']==datetime.now().strftime('%Y-%m-%d')]['Price'].sum()} {profile['currency']}")
        c3.metric("الفحوصات", len(df))
        if not df.empty: st.plotly_chart(px.line(df.groupby('Date').size().reset_index(name='c'), x='Date', y='c', title="حركة المختبر"), use_container_width=True)

    with tabs[5]: # المخزن (كامل)
        st.subheader("📦 إدارة المخزون")
        st.dataframe(inv_df, use_container_width=True)
        if st.button("إضافة مادة تجريبية"):
            new_inv = pd.DataFrame([["Tubes", 500, "2027-01", "Unit"]], columns=inv_df.columns)
            pd.concat([inv_df, new_inv]).to_csv(inv_path, index=False); st.rerun()

    with tabs[6]: # تحليل AI (كامل)
        if not df.empty:
            ai_p = st.selectbox("تحليل AI للمريض", df['Patient'].unique(), key="ai_tab_sel")
            for ins in ai_diagnostic_logic(df[df['Patient'] == ai_p]):
                st.markdown(f'<div class="ai-insight-box">{ins}</div>', unsafe_allow_html=True)

    with tabs[7]: # المالية (كامل)
        st.subheader("💰 السجل المالي")
        st.dataframe(df[['Date', 'Patient', 'Test', 'Price']], use_container_width=True)
        st.success(f"إجمالي الأرباح المسجلة: {df['Price'].sum()} {profile['currency']}")

    with tabs[8]: # الإعدادات
        if st.button("تسجيل الخروج"): st.session_state.user_code = None; st.rerun()

    st.markdown(f"<center style='opacity:0.2;'>{OWNER_INFO['SYSTEM_VERSION']}</center>", unsafe_allow_html=True)

