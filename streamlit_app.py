import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import io
import qrcode  # ميزة جديدة: يحتاج تثبيت pip install qrcode

# --- 1. هندسة الواجهة والمنع المطلق للتحديث وسلاسة الحركة ---
st.set_page_config(page_title="BioLab Intelligence Pro", page_icon="🧬", layout="wide")

# ميزة 1: نظام CSS عالمي مطور مع تأثيرات حركية (Glassmorphism)
st.markdown("""
    <script>
    window.onbeforeunload = function() { return "تحذير: قد تفقد البيانات غير المحفوظة!"; };
    </script>
    <style>
    [data-testid="stStatusWidget"], [data-testid="stHeader"], .stDeployButton { display: none !important; }
    
    /* ميزة 2: سلاسة الانتقال بين التبويبات */
    .stTabs [data-baseweb="tab"] {
        transition: all 0.4s ease-in-out;
    }
    
    .critical-alert-card {
        background: rgba(127, 29, 29, 0.9); color: white; padding: 20px; border-radius: 15px;
        border: 4px solid #f87171; animation: blinker 1.5s linear infinite;
        margin: 10px 0; text-align: center; font-weight: bold; box-shadow: 0 10px 20px rgba(0,0,0,0.3);
    }
    @keyframes blinker { 50% { opacity: 0.6; } }

    .ai-insight-box {
        background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px);
        border-right: 10px solid #2563eb; padding: 20px; border-radius: 15px;
        margin: 15px 0; border: 1px solid rgba(37, 99, 235, 0.2);
    }

    .report-paper {
        background: white; border: 2px solid #334155; padding: 40px;
        border-radius: 5px; color: black; font-family: 'Courier New', sans-serif;
        box-shadow: 0 0 20px rgba(0,0,0,0.1); margin: 20px auto; max-width: 800px;
    }
    .header-style {
        background: linear-gradient(90deg, #0f172a 0%, #1e40af 100%);
        padding: 40px; border-radius: 0 0 50px 50px; color: white; margin-bottom: 25px;
        text-align: center; box-shadow: 0 10px 30px rgba(30, 64, 175, 0.3);
    }
    
    /* ميزة 3: تأثيرات التحويم على الأزرار */
    .stButton>button:hover {
        transform: scale(1.02); background: #1e40af !important; color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. نظام الهوية الثابتة ---
OWNER_INFO = {
    "PERMANENT_LAB_NAME": "مختبر النخبة التخصصي",
    "PERMANENT_DOC_NAME": "د. أحمد المصطفى",
    "SYSTEM_VERSION": "v35.0 Global Enterprise",
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

# --- 4. الوظائف التحليلية (الأصلية + ميزات جديدة) ---
def generate_qr_code(data):
    qr = qrcode.make(data)
    buf = io.BytesIO()
    qr.save(buf, format="PNG")
    return buf.getvalue()

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

# ميزة 4: البحث العالمي السريع في الشريط الجانبي
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/809/809957.png", width=100)
    st.title("البحث الذكي")
    search_query = st.text_input("ابحث عن مريض أو فحص...")
    st.divider()
    currency_mode = st.radio("العملة المعروضة", ["USD $", "IQD (Local)"]) # ميزة 5: تحويل عملات

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

    # ميزة 6: تصفية البيانات فورياً بناءً على البحث العالمي
    if search_query:
        df = df[df.apply(lambda row: search_query.lower() in row.astype(str).str.lower().values, axis=1)]

    st.markdown(f'<div class="header-style"><h1>{OWNER_INFO["PERMANENT_LAB_NAME"]}</h1><p>{OWNER_INFO["PERMANENT_DOC_NAME"]} - النظام العالمي المتكامل</p></div>', unsafe_allow_html=True)

    tabs = st.tabs(["📊 الإحصائيات", "🧪 تسجيل فحص", "👤 ملف المريض", "📄 الطباعة", "📂 الأرشيف", "📦 المخزون", "🧠 AI", "💰 المالية", "⚙️ الإعدادات"])

    with tabs[1]: # تسجيل فحص
        with st.form("entry_form", clear_on_submit=True):
            c1, c2, c3 = st.columns([2, 1, 1])
            name, age, gender = c1.text_input("اسم المريض"), c2.number_input("العمر", 1, 120, 25), c3.selectbox("الجنس", ["ذكر", "أنثى"])
            pid = st.text_input("PID", value=datetime.now().strftime("%H%M%S"))
            cat = st.selectbox("القسم", list(LAB_CATALOG.keys()))
            test = st.selectbox("التحليل", list(LAB_CATALOG[cat]["Tests"].keys()))
            val = st.number_input("النتيجة", format="%.2f")
            if st.form_submit_button("حفظ الفحص 🚀"):
                # ميزة 7: تنبيه صوتي عند الحفظ (مخفي برمجياً)
                st.markdown('<audio autoplay><source src="https://www.soundjay.com/buttons/sounds/button-37a.mp3" type="audio/mpeg"></audio>', unsafe_allow_html=True)
                low, high = LAB_CATALOG[cat]["Tests"][test][:2]
                status = "مرتفع 🔴" if val > high else ("منخفض 🔵" if val < low else "طبيعي 🟢")
                new_row = [pid, datetime.now().strftime("%Y-%m-%d"), datetime.now().strftime("%Y-%m-%d %H:%M"), name, age, gender, cat, test, val, LAB_CATALOG[cat]["Tests"][test][2], status, LAB_CATALOG[cat]["Tests"][test][3], LAB_CATALOG[cat]["DefaultTube"], OWNER_INFO["PERMANENT_LAB_NAME"], OWNER_INFO["PERMANENT_DOC_NAME"]]
                df = pd.concat([df, pd.DataFrame([new_row], columns=df.columns)], ignore_index=True)
                df.to_csv(db_p, index=False); st.toast("✅ تم الحفظ بنجاح!"); st.rerun()

    with tabs[2]: # ملف المريض
        if not df.empty:
            p = st.selectbox("اختر مريضاً", df['Patient'].unique())
            p_df = df[df['Patient'] == p]
            c_a, c_b = st.columns([2, 1])
            with c_a: st.plotly_chart(render_radar_chart(p_df), use_container_width=True)
            with c_b: 
                # ميزة 8: QR Code المريض
                st.image(generate_qr_code(f"Patient: {p}\nID: {p_df['PID'].iloc[0]}\nStatus: Processed"), caption="Scan to Verify")
                st.dataframe(p_df[['Date', 'Test', 'Result', 'Status']], use_container_width=True)
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
                        + '</table><br><br>توقيع الطبيب المختص: ____________</div>', unsafe_allow_html=True)

    with tabs[0]: # الإحصائيات (محدثة)
        # ميزة 9: مؤشر ضغط العمل (رسم بياني زمني)
        df['Hour'] = pd.to_datetime(df['Timestamp']).dt.hour
        workload = df.groupby('Hour').size().reset_index(name='Counts')
        st.plotly_chart(px.area(workload, x='Hour', y='Counts', title="مؤشر ضغط العمل خلال اليوم"), use_container_width=True)
        
        critical_cases = df[df['Status'].str.contains("🔴|🔵")]
        if not critical_cases.empty:
            st.markdown(f'<div class="critical-alert-card">⚠️ تنبيه: يوجد {len(critical_cases)} نتائج خارج المدى الطبيعي!</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.metric("إجمالي المرضى", len(df['Patient'].unique()))
        total_p = df[df['Date']==datetime.now().strftime('%Y-%m-%d')]['Price'].sum()
        price_display = total_p if currency_mode == "USD $" else total_p * 1500
        c2.metric("دخل اليوم", f"{price_display} {'$' if currency_mode == 'USD $' else 'IQD'}")
        c3.metric("الفحوصات المنجزة", len(df))

    with tabs[5]: # المخزون (ميزة 10: تنبيه انتهاء الصلاحية)
        st.subheader("📦 إدارة المستلزمات")
        st.dataframe(inv_df, use_container_width=True)
        if st.button("تحديث المخزن"):
             new_inv = pd.DataFrame([["Cuvettes", 500, "2026-12", "Box"], ["EDTA Tubes", 1000, "2026-06", "Pcs"]], columns=["Item", "Stock", "Expiry", "Unit"])
             new_inv.to_csv(inv_p, index=False); st.rerun()

    with tabs[6]: # AI
        if not df.empty:
            ai_p = st.selectbox("تحليل AI للمريض", df['Patient'].unique(), key="ai_select")
            for ins in ai_diagnostic_logic(df[df['Patient'] == ai_p]):
                st.markdown(f'<div class="ai-insight-box">{ins}</div>', unsafe_allow_html=True)

    with tabs[8]: # الإعدادات
        # ميزة إضافية: تنظيف البيانات
        if st.button("تنظيف ذاكرة النظام المؤقتة"):
            st.cache_data.clear(); st.success("تم التنظيف!"); st.rerun()
        if st.button("تسجيل الخروج"): st.session_state.user_code = None; st.rerun()

    st.markdown(f"<center style='opacity:0.2;'>{OWNER_INFO['SYSTEM_VERSION']} | Licensed to: {OWNER_INFO['PERMANENT_DOC_NAME']}</center>", unsafe_allow_html=True)
