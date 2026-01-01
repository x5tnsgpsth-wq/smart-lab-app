import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import io

# --- 1. هندسة الواجهة والمنع المطلق للتحديث وسلاسة الحركة ---
st.set_page_config(page_title="BioLab Intelligence Pro", page_icon="🧬", layout="wide")

st.markdown("""
    <script>
    window.onbeforeunload = function() { return "تحذير: قد تفقد البيانات غير المحفوظة!"; };
    </script>
    <style>
    /* حذف حلقة التحميل نهائياً */
    [data-testid="stStatusWidget"], [data-testid="stHeader"], .stDeployButton { display: none !important; }
    
    /* منع التمرير العشوائي وسلاسة الواجهة */
    html, body, [data-testid="stAppViewContainer"] {
        overflow: hidden !important; position: fixed !important;
        width: 100% !important; height: 100% !important;
    }
    [data-testid="stMainViewContainer"] {
        overflow-y: auto !important; height: 100vh !important;
    }

    /* صناديق التنبيهات الحرجة والـ AI */
    .critical-alert-card {
        background: #7f1d1d; color: white; padding: 20px; border-radius: 15px;
        border: 4px solid #f87171; animation: blinker 1.5s linear infinite;
        margin: 10px 0; text-align: center; font-weight: bold;
    }
    @keyframes blinker { 50% { opacity: 0.6; } }

    .ai-insight-box {
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        border-right: 10px solid #2563eb; padding: 20px; border-radius: 15px;
        margin: 15px 0; box-shadow: 0 4px 12px rgba(37, 99, 235, 0.1);
    }

    .status-card {
        padding: 15px; border-radius: 12px; margin-bottom: 10px;
        border-right: 8px solid; transition: transform 0.2s;
    }
    .critical-red { background: #fef2f2; border-right-color: #ef4444; color: #991b1b; }
    .normal-green { background: #f0fdf4; border-right-color: #10b981; color: #065f46; }
    
    .stability-timer {
        padding: 8px 12px; border-radius: 20px; font-weight: bold; font-size: 0.85em;
    }
    .timer-safe { background: #dcfce7; color: #16a34a; }
    .timer-warning { background: #fef9c3; color: #a16207; }
    .timer-expired { background: #fee2e2; color: #dc2626; border: 1px solid #dc2626; }

    .report-paper {
        background: white; border: 2px solid #334155; padding: 40px;
        border-radius: 5px; color: black; font-family: 'Arial', sans-serif;
        box-shadow: 0 0 20px rgba(0,0,0,0.1); margin: 20px auto; max-width: 800px;
    }
    .header-style {
        background: linear-gradient(135deg, #0f172a 0%, #1e40af 100%);
        padding: 30px; border-radius: 20px; color: white; margin-bottom: 25px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. نظام الهوية الثابتة ---
OWNER_INFO = {
    "PERMANENT_LAB_NAME": "مختبر النخبة التخصصي",
    "PERMANENT_DOC_NAME": "د. أحمد المصطفى",
    "SYSTEM_VERSION": "v31.0 Final Recovery",
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

# --- 4. الوظائف التحليلية المستعادة بالكامل ---
def render_radar_chart(p_df):
    tests = p_df['Test'].tolist()
    normalized = []
    for _, r in p_df.iterrows():
        l, h = LAB_CATALOG[r['Category']]['Tests'][r['Test']][:2]
        normalized.append((r['Result']-l)/(h-l) if h!=l else 1)
    fig = go.Figure(data=go.Scatterpolar(r=normalized, theta=tests, fill='toself', line_color='#1e40af'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=False, range=[0, 2])), showlegend=False, height=350)
    return fig

def check_sample_stability(ts, cat):
    try:
        draw = datetime.strptime(ts, "%Y-%m-%d %H:%M")
        rem = (draw + timedelta(hours=LAB_CATALOG[cat]["Stability"])) - datetime.now()
        hrs = rem.total_seconds() / 3600
        if hrs <= 0: return "منتهية ❌", "timer-expired"
        return (f"صالحة ({int(hrs)}س) ✅", "timer-safe") if hrs > 2 else (f"تحذير ({int(hrs*60)}د) ⚠️", "timer-warning")
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
        patient_df.to_excel(writer, index=False)
    return output.getvalue()

def get_file_path(ext):
    uid = "".join(x for x in (st.session_state.get('user_code', 'default')) if x.isalnum())
    return f"biolab_{uid}.{ext}"

# --- 5. منطق الواجهة الرئيسي ---
if 'user_code' not in st.session_state: st.session_state.user_code = None

if st.session_state.user_code is None:
    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        st.title("🧬 BioLab Intelligence")
        code = st.text_input("رمز الوصول الآمن", type="password")
        if st.button("دخول النظام"): st.session_state.user_code = code; st.rerun()
else:
    db_p, inv_p = get_file_path("csv"), get_file_path("inv.csv")
    db_cols = ["PID", "Date", "Timestamp", "Patient", "Age", "Gender", "Category", "Test", "Result", "Unit", "Status", "Price", "Tube", "LabName", "DoctorName"]
    df = pd.read_csv(db_p) if os.path.exists(db_p) else pd.DataFrame(columns=db_cols)
    inv_df = pd.read_csv(inv_p) if os.path.exists(inv_p) else pd.DataFrame(columns=["Item", "Stock", "Expiry", "Unit"])

    st.markdown(f'<div class="header-style"><h1>{OWNER_INFO["PERMANENT_LAB_NAME"]}</h1></div>', unsafe_allow_html=True)

    tabs = st.tabs(["📊 الإحصائيات", "🧪 تسجيل فحص", "👤 ملف المريض", "📄 الطباعة", "📂 الأرشيف", "📦 المخزون", "🧠 AI", "💰 المالية", "⚙️ الإعدادات"])

    with tabs[1]: # التسجيل الكامل (تمت استعادة كافة الحقول)
        with st.form("entry_form", clear_on_submit=True):
            c1, c2, c3 = st.columns([2, 1, 1])
            name, age, gender = c1.text_input("اسم المريض"), c2.number_input("العمر", 1, 120, 25), c3.selectbox("الجنس", ["ذكر", "أنثى"])
            pid = st.text_input("PID", value=datetime.now().strftime("%H%M%S"))
            cat = st.selectbox("القسم", list(LAB_CATALOG.keys()))
            test = st.selectbox("التحليل", list(LAB_CATALOG[cat]["Tests"].keys()))
            val = st.number_input("النتيجة", format="%.2f")
            if st.form_submit_button("حفظ الفحص 🚀"):
                low, high = LAB_CATALOG[cat]["Tests"][test][:2]
                status = "مرتفع 🔴" if val > high else ("منخفض 🔵" if val < low else "طبيعي 🟢")
                new_row = [pid, datetime.now().strftime("%Y-%m-%d"), datetime.now().strftime("%Y-%m-%d %H:%M"), name, age, gender, cat, test, val, LAB_CATALOG[cat]["Tests"][test][2], status, LAB_CATALOG[cat]["Tests"][test][3], LAB_CATALOG[cat]["DefaultTube"], OWNER_INFO["PERMANENT_LAB_NAME"], OWNER_INFO["PERMANENT_DOC_NAME"]]
                df = pd.concat([df, pd.DataFrame([new_row], columns=df.columns)], ignore_index=True)
                df.to_csv(db_p, index=False); st.toast("تم الحفظ!"); st.rerun()

    with tabs[2]: # ملف المريض
        if not df.empty:
            p = st.selectbox("اختر مريضاً", df['Patient'].unique())
            p_df = df[df['Patient'] == p]
            c_a, c_b = st.columns(2)
            with c_a: st.plotly_chart(render_radar_chart(p_df), use_container_width=True)
            with c_b: st.dataframe(p_df[['Date', 'Test', 'Result', 'Status']], use_container_width=True)
            st.download_button("📥 تحميل Excel", export_to_excel(p_df), f"{p}.xlsx")

    with tabs[3]: # الطباعة
        if not df.empty:
            target = st.selectbox("مريض الطباعة", df['Patient'].unique(), key="print_tab")
            t_df = df[df['Patient'] == target]
            l = t_df.iloc[-1]
            st.markdown(f'<div class="report-paper"><h3>{OWNER_INFO["PERMANENT_LAB_NAME"]}</h3><hr>'
                        f'<b>الاسم:</b> {target} | <b>PID:</b> {l["PID"]} | <b>التاريخ:</b> {l["Date"]}<table style="width:100%; margin-top:20px; border-collapse:collapse;">'
                        f'<tr style="background:#eee;"><th>الفحص</th><th>النتيجة</th><th>الوحدة</th><th>المدى</th></tr>'
                        + "".join([f"<tr><td>{r['Test']}</td><td>{r['Result']}</td><td>{r['Unit']}</td><td>{LAB_CATALOG[r['Category']]['Tests'][r['Test']][0]}-{LAB_CATALOG[r['Category']]['Tests'][r['Test']][1]}</td></tr>" for _, r in t_df.iterrows()])
                        + '</table><br><br>توقيع الطبيب: ____________</div>', unsafe_allow_html=True)

    with tabs[6]: # نظام الـ AI (مستعاد)
        if not df.empty:
            ai_p = st.selectbox("تحليل AI للمريض", df['Patient'].unique(), key="ai_select")
            for ins in ai_diagnostic_logic(df[df['Patient'] == ai_p]):
                st.markdown(f'<div class="ai-insight-box">{ins}</div>', unsafe_allow_html=True)

    with tabs[0]: # الإحصائيات
        critical_cases = df[df['Status'].str.contains("🔴|🔵")]
        if not critical_cases.empty:
            st.markdown(f'<div class="critical-alert-card">⚠️ يوجد {len(critical_cases)} نتائج خارج المدى الطبيعي!</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.metric("المرضى", len(df['Patient'].unique()))
        c2.metric("دخل اليوم", f"{df[df['Date']==datetime.now().strftime('%Y-%m-%d')]['Price'].sum()} $")
        c3.metric("الفحوصات", len(df))

    with tabs[4]: # الأرشيف
        for _, r in df.tail(10).iterrows():
            timer, cls = check_sample_stability(r['Timestamp'], r['Category'])
            st.markdown(f'<div style="padding:10px; border:1px solid #eee; margin-bottom:5px; border-radius:10px; display:flex; justify-content:space-between;">'
                        f'<span>{r["Patient"]} - {r["Test"]}</span><span class="stability-timer {cls}">{timer}</span></div>', unsafe_allow_html=True)

    with tabs[5]: st.dataframe(inv_df, use_container_width=True)
    with tabs[7]: st.info(f"إجمالي الأرباح الكلي: {df['Price'].sum()} $")
    with tabs[8]:
        if st.button("خروج"): st.session_state.user_code = None; st.rerun()

    st.markdown(f"<center style='opacity:0.2;'>{OWNER_INFO['SYSTEM_VERSION']}</center>", unsafe_allow_html=True)

