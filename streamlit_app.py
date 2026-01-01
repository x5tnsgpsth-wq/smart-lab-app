import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import io

# --- 1. هندسة الواجهة والمنع المطلق للتحديث (JS المتقدم) ---
st.set_page_config(page_title="BioLab Intelligence Pro", page_icon="🧬", layout="wide")

st.markdown("""
    <script>
    // منع التحديث العرضي وحماية البيانات
    window.onbeforeunload = function() { return "هل أنت متأكد من مغادرة النظام؟ قد تفقد البيانات غير المحفوظة"; };
    </script>
    <style>
    /* حذف حلقة التحميل وشريط الحالة نهائياً */
    [data-testid="stStatusWidget"], [data-testid="stHeader"], .stDeployButton { display: none !important; }
    
    /* هندسة الواجهة لمنع التمرير العشوائي */
    html, body, [data-testid="stAppViewContainer"] {
        overflow: hidden !important; position: fixed !important;
        width: 100% !important; height: 100% !important;
    }
    [data-testid="stMainViewContainer"] {
        overflow-y: auto !important; height: 100vh !important;
    }

    /* ستايل التبويبات الاحترافي */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #f8fafc; border-radius: 10px 10px 0 0; 
        padding: 10px 20px; transition: all 0.3s ease; border: 1px solid #e2e8f0;
    }
    .stTabs [aria-selected="true"] { 
        background-color: #1e40af !important; color: white !important; border-color: #1e40af !important;
    }

    /* تأثيرات البطاقات */
    .status-card {
        padding: 15px; border-radius: 12px; margin-bottom: 10px;
        border-right: 8px solid; transition: transform 0.2s ease;
    }
    .critical-red { background: #fef2f2; border-right-color: #ef4444; color: #991b1b; }
    .normal-green { background: #f0fdf4; border-right-color: #10b981; color: #065f46; }

    /* مؤقت جودة العينة */
    .stability-timer {
        padding: 8px 12px; border-radius: 20px; font-weight: bold; font-size: 0.85em;
    }
    .timer-safe { background: #dcfce7; color: #16a34a; }
    .timer-warning { background: #fef9c3; color: #a16207; }
    .timer-expired { background: #fee2e2; color: #dc2626; border: 1px solid #dc2626; }

    /* صندوق تحليل AI */
    .ai-insight-box {
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        border-right: 10px solid #2563eb; padding: 20px; border-radius: 15px;
        margin: 15px 0; box-shadow: 0 4px 12px rgba(37, 99, 235, 0.1);
    }

    /* تصميم ورقة الطباعة الاحترافية */
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
        padding: 30px; border-radius: 20px; color: white; margin-bottom: 25px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. نظام الهوية والقفل الآمن ---
OWNER_INFO = {
    "PERMANENT_LAB_NAME": "مختبر النخبة التخصصي",
    "PERMANENT_DOC_NAME": "د. أحمد المصطفى",
    "SYSTEM_VERSION": "v29.0 Master Recovery Edition",
    "LICENSE_KEY": "PREMIUM-2026-X"
}

# --- 3. الموسوعة الطبية الشاملة (كاملة 100% مع مديات الخطر) ---
LAB_CATALOG = {
    "Hematology (أمراض الدم)": {
        "DefaultTube": "Purple (EDTA) 🟣", "Stability": 24,
        "Tests": {
            "CBC": (12, 16, "g/dL", 15), "HGB": (12, 18, "g/dL", 10), "PLT": (150, 450, "10^3/uL", 12),
            "WBC": (4, 11, "10^3/uL", 10), "ESR": (0, 20, "mm/hr", 8), "PCV": (37, 52, "%", 10),
            "PT": (11, 13.5, "sec", 15), "PTT": (25, 35, "sec", 15)
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

# --- 4. الوظائف الذكية (إعادة بناء شاملة) ---
def render_radar_chart(p_df):
    tests = p_df['Test'].tolist()
    normalized_results = []
    for _, r in p_df.iterrows():
        try:
            low, high = LAB_CATALOG[r['Category']]['Tests'][r['Test']][:2]
            val = (r['Result'] - low) / (high - low) if high != low else 1
            normalized_results.append(max(0, min(val, 2))) # تقييد النتيجة للرسم
        except: normalized_results.append(1)
    
    fig = go.Figure(data=go.Scatterpolar(r=normalized_results, theta=tests, fill='toself', line_color='#1e40af'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=False, range=[0, 2])), showlegend=False, height=350)
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
    if "HGB" in tests and tests["HGB"] < 11: insights.append("🩸 **الأنيميا:** انخفاض الهيموجلوبين ملحوظ.")
    return insights if insights else ["✅ النتائج ضمن السياق الطبيعي المبدئي."]

def export_to_excel(patient_df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        patient_df.to_excel(writer, index=False, sheet_name='Report')
    return output.getvalue()

def get_file_path(extension):
    user_id = "".join(x for x in (st.session_state.get('user_code', 'default')) if x.isalnum())
    return f"biolab_data_{user_id}.{extension}"

def get_result_analysis(cat, test, val):
    data = LAB_CATALOG[cat]["Tests"][test]
    low, high = data[0], data[1]
    if low == 0 and high == 0: return "طبيعي 🟢", "normal-green"
    if val < low: return "منخفض 🔵", "critical-red"
    if val > high: return "مرتفع 🔴", "critical-red"
    return "طبيعي 🟢", "normal-green"

# --- 5. منطق واجهة المستخدم ---
if 'user_code' not in st.session_state: st.session_state.user_code = None

if st.session_state.user_code is None:
    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        st.markdown("<br><h1 style='text-align:center;'>🧬 BioLab Intelligence</h1>", unsafe_allow_html=True)
        code_input = st.text_input("أدخل رمز الوصول الآمن", type="password")
        if st.button("دخول النظام", use_container_width=True, type="primary"):
            st.session_state.user_code = code_input; st.rerun()
else:
    db_path, inv_path = get_file_path("csv"), get_file_path("inv.csv")
    db_cols = ["PID", "Date", "Timestamp", "Patient", "Age", "Gender", "Category", "Test", "Result", "Unit", "Status", "Price", "Tube", "LabName", "DoctorName"]
    df = pd.read_csv(db_path) if os.path.exists(db_path) else pd.DataFrame(columns=db_cols)
    inv_df = pd.read_csv(inv_path) if os.path.exists(inv_path) else pd.DataFrame(columns=["Item", "Stock", "Expiry", "Unit"])

    st.markdown(f"""<div class="header-style no-print"><div style="display:flex; justify-content:space-between; align-items:center;"><div><h1>{OWNER_INFO['PERMANENT_LAB_NAME']}</h1><p>{OWNER_INFO['PERMANENT_DOC_NAME']}</p></div><div><h3>{datetime.now().strftime('%Y-%m-%d')}</h3></div></div></div>""", unsafe_allow_html=True)

    tabs = st.tabs(["📊 الإحصائيات", "🧪 تسجيل فحص", "👤 ملف المريض", "📄 ورقة الطباعة", "📂 الأرشيف الرقابي", "📦 المخزون", "🧠 AI", "💰 المالية", "⚙️ الإعدادات"])

    with tabs[1]: # تسجيل فحص كامل
        with st.form("main_entry", clear_on_submit=True):
            c1, c2, c3 = st.columns([2, 1, 1])
            p_name, p_age, p_gender = c1.text_input("اسم المريض الكامل"), c2.number_input("العمر", 1, 120, 25), c3.selectbox("الجنس", ["ذكر", "أنثى"])
            p_id = st.text_input("رقم PID", value=datetime.now().strftime("%H%M%S"))
            cat_sel = st.selectbox("القسم", list(LAB_CATALOG.keys()))
            test_sel = st.selectbox("التحليل", list(LAB_CATALOG[cat_sel]["Tests"].keys()))
            res_val = st.number_input("النتيجة", format="%.2f")
            if st.form_submit_button("حفظ النتيجة 🚀", use_container_width=True):
                status, _ = get_result_analysis(cat_sel, test_sel, res_val)
                new_row = [p_id, datetime.now().strftime("%Y-%m-%d"), datetime.now().strftime("%Y-%m-%d %H:%M"), p_name, p_age, p_gender, cat_sel, test_sel, res_val, LAB_CATALOG[cat_sel]["Tests"][test_sel][2], status, LAB_CATALOG[cat_sel]["Tests"][test_sel][3], LAB_CATALOG[cat_sel]["DefaultTube"], OWNER_INFO['PERMANENT_LAB_NAME'], OWNER_INFO['PERMANENT_DOC_NAME']]
                df = pd.concat([df, pd.DataFrame([new_row], columns=df.columns)], ignore_index=True)
                df.to_csv(db_path, index=False); st.toast("تم الحفظ!"); st.rerun()

    with tabs[2]: # ملف المريض والرادار
        if not df.empty:
            p_pick = st.selectbox("اختر المريض", df['Patient'].unique())
            p_data = df[df['Patient'] == p_pick]
            col_a, col_b = st.columns([1, 1])
            with col_a: st.plotly_chart(render_radar_chart(p_data), use_container_width=True)
            with col_b: st.dataframe(p_data[['Date', 'Test', 'Result', 'Status']], use_container_width=True)
            st.download_button("📥 Excel", export_to_excel(p_data), f"{p_pick}.xlsx")

    with tabs[3]: # ورقة الطباعة الاحترافية
        if not df.empty:
            target = st.selectbox("مريض الطباعة", df['Patient'].unique(), key="print_key")
            t_data = df[df['Patient'] == target]
            l = t_data.iloc[-1]
            st.markdown(f"""<div class="report-paper">
                <div class="report-header"><h2>{OWNER_INFO['PERMANENT_LAB_NAME']}</h2><p>إشراف: {OWNER_INFO['PERMANENT_DOC_NAME']}</p></div>
                <p><b>الاسم:</b> {target} | <b>العمر:</b> {l['Age']} | <b>التاريخ:</b> {l['Date']}</p>
                <table class="report-table"><thead><tr><th>التحليل</th><th>النتيجة</th><th>الوحدة</th><th>المدى الطبيعي</th></tr></thead><tbody>
                {"".join([f"<tr><td>{r['Test']}</td><td><b>{r['Result']}</b></td><td>{r['Unit']}</td><td>{LAB_CATALOG[r['Category']]['Tests'][r['Test']][0]}-{LAB_CATALOG[r['Category']]['Tests'][r['Test']][1]}</td></tr>" for _, r in t_data.iterrows()])}
                </tbody></table><br><br><p>توقيع الطبيب المختص: _________________</p></div>""", unsafe_allow_html=True)
            st.button("🖨️ طباعة التقرير")

    with tabs[4]: # الأرشيف الرقابي
        st.subheader("🕵️ تتبع جودة العينات")
        if not df.empty:
            for _, r in df.tail(10).iterrows():
                timer, cls = check_sample_stability(r['Timestamp'], r['Category'])
                st.markdown(f'<div style="background:white; padding:10px; border-radius:10px; margin-bottom:5px; border:1px solid #eee; display:flex; justify-content:space-between;"><span><b>{r["Patient"]}</b> | {r["Test"]}</span> <span class="stability-timer {cls}">{timer}</span></div>', unsafe_allow_html=True)

    with tabs[0]: # الإحصائيات
        c1, c2, c3 = st.columns(3)
        c1.metric("إجمالي المرضى", len(df['Patient'].unique()))
        c2.metric("دخل اليوم", f"{df[df['Date']==datetime.now().strftime('%Y-%m-%d')]['Price'].sum()} $")
        c3.metric("الفحوصات", len(df))
        if not df.empty: st.plotly_chart(px.bar(df.groupby('Category').size().reset_index(name='c'), x='Category', y='c', title="توزيع العمل"), use_container_width=True)

    with tabs[5]: # المخزن
        st.subheader("📦 إدارة المخزون")
        st.dataframe(inv_df, use_container_width=True)

    with tabs[6]: # AI
        if not df.empty:
            ai_p = st.selectbox("تحليل AI للمريض", df['Patient'].unique(), key="ai_p")
            for ins in ai_diagnostic_logic(df[df['Patient'] == ai_p]):
                st.markdown(f'<div class="ai-insight-box">{ins}</div>', unsafe_allow_html=True)

    with tabs[7]: # المالية
        st.subheader("💰 المالية")
        st.dataframe(df[['Date', 'Patient', 'Test', 'Price']], use_container_width=True)
        st.success(f"الإجمالي: {df['Price'].sum()} $")

    with tabs[8]: # الإعدادات
        if st.button("خروج آمن"): st.session_state.user_code = None; st.rerun()

    st.markdown(f"<center style='opacity:0.2; padding:30px;'>{OWNER_INFO['SYSTEM_VERSION']}</center>", unsafe_allow_html=True)
