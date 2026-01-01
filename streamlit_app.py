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
    
    .patient-info-box {
        background: #f8fafc; border: 1px solid #e2e8f0; padding: 20px;
        border-radius: 15px; border-left: 5px solid #3b82f6; margin-bottom: 20px;
    }
    
    .stability-badge {
        font-size: 0.8em; padding: 2px 8px; border-radius: 10px; font-weight: bold;
    }
    .expired { background: #fee2e2; color: #dc2626; border: 1px solid #dc2626; }
    .fresh { background: #dcfce7; color: #16a34a; border: 1px solid #16a34a; }

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
    "SYSTEM_VERSION": "v18.0 Patient-Centric Edition",
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
        }
    },
    "Biochemistry (الكيمياء الحيوية)": {
        "DefaultTube": "Yellow (Gel) 🟡", "Stability": 48,
        "Tests": {
            "Glucose (Fasting)": (70, 100, "mg/dL", 5), "HbA1c": (4, 5.6, "%", 25), "Urea": (15, 45, "mg/dL", 10),
            "Creatinine": (0.6, 1.2, "mg/dL", 15), "Albumin": (3.4, 5.4, "g/dL", 12), "Total Protein": (6.4, 8.3, "g/dL", 10)
        }
    }
}
TUBE_TYPES = ["Purple (EDTA) 🟣", "Yellow (Gel) 🟡", "Red (Plain) 🔴", "Blue (Citrate) 🔵"]

# --- 4. إدارة الملفات والبيانات ---
def get_file_path(extension):
    user_id = "".join(x for x in (st.session_state.get('user_code', 'default')) if x.isalnum())
    return f"biolab_data_{user_id}.{extension}"

def load_user_profile():
    path = get_file_path("json")
    if os.path.exists(path): return json.load(open(path, "r", encoding="utf-8"))
    return {"lab_name": OWNER_INFO["PERMANENT_LAB_NAME"], "doc_name": OWNER_INFO["PERMANENT_DOC_NAME"], "title": "مدير المختبر", "currency": "$", "daily_target": 1000}

def get_result_analysis(cat, test, val):
    if cat not in LAB_CATALOG: return "غير محدد", "warning-yellow"
    data = LAB_CATALOG[cat]["Tests"][test]
    low, high, unit, price = data
    if low == 0 and high == 0: return "طبيعي 🟢", "normal-green"
    if val < low: return "منخفض 🔵", "critical-red"
    if val > high: return "مرتفع 🔴", "critical-red"
    return "طبيعي 🟢", "normal-green"

def check_stability(timestamp_str, category):
    try:
        draw_time = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M")
        stability_hours = LAB_CATALOG[category]["Stability"]
        expiry_time = draw_time + timedelta(hours=stability_hours)
        remaining = expiry_time - datetime.now()
        if remaining.total_seconds() <= 0: return "منتهية ❌", "expired"
        return f"صالحة: {int(remaining.total_seconds() // 3600)} ساعة ✅", "fresh"
    except: return "غير محدد", ""

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
    
    # تحديث الأعمدة لتشمل معلومات المريض الإضافية
    cols = ["PID", "Date", "Timestamp", "Patient", "Age", "Gender", "Category", "Test", "Result", "Unit", "Status", "Price", "Tube", "LabName", "DoctorName"]
    df = pd.read_csv(db_path) if os.path.exists(db_path) else pd.DataFrame(columns=cols)
    inv_df = pd.read_csv(inv_path) if os.path.exists(inv_path) else pd.DataFrame(columns=["Item", "Stock", "Expiry", "Unit"])

    st.markdown(f"""<div class="header-style"><div style="display:flex; justify-content:space-between;"><div><h1>{profile['lab_name']}</h1><p>{profile['doc_name']}</p></div><div style="text-align:right;"><h3>{datetime.now().strftime('%Y-%m-%d')}</h3></div></div></div>""", unsafe_allow_html=True)

    tabs = st.tabs(["📊 الإحصائيات", "🧪 تسجيل فحص", "👤 معلومات المريض", "📂 الأرشيف", "📦 المخزون", "🧠 تحليل AI", "💰 المالية", "⚙️ الإعدادات"])

    with tabs[1]: # تسجيل فحص (معدل لإضافة العمر والجنس)
        with st.form("entry_form", clear_on_submit=True):
            c1, c2, c3 = st.columns([2, 1, 1])
            p_name = c1.text_input("اسم المريض")
            p_age = c2.number_input("العمر", min_value=1, max_value=120, value=25)
            p_gender = c3.selectbox("الجنس", ["ذكر", "أنثى"])
            
            c4, c5 = st.columns(2)
            cat_sel = c4.selectbox("القسم", list(LAB_CATALOG.keys()))
            test_sel = c5.selectbox("التحليل", list(LAB_CATALOG[cat_sel]["Tests"].keys()))
            
            res_val = st.number_input(f"النتيجة ({LAB_CATALOG[cat_sel]['Tests'][test_sel][2]})", format="%.2f")
            
            if st.form_submit_button("حفظ البيانات 🚀", use_container_width=True):
                status, _ = get_result_analysis(cat_sel, test_sel, res_val)
                new_data = [
                    datetime.now().strftime("%H%M%S"), datetime.now().strftime("%Y-%m-%d"), 
                    datetime.now().strftime("%Y-%m-%d %H:%M"), p_name, p_age, p_gender,
                    cat_sel, test_sel, res_val, LAB_CATALOG[cat_sel]["Tests"][test_sel][2],
                    status, LAB_CATALOG[cat_sel]["Tests"][test_sel][3], 
                    LAB_CATALOG[cat_sel]["DefaultTube"], profile['lab_name'], profile['doc_name']
                ]
                df = pd.concat([df, pd.DataFrame([new_data], columns=df.columns)], ignore_index=True)
                df.to_csv(db_path, index=False)
                st.success("تم الحفظ بنجاح!")

    with tabs[2]: # التبويب الجديد: معلومات المريض
        st.subheader("👤 السجل الشخصي والمعلومات الحيوية")
        if not df.empty:
            p_select = st.selectbox("اختر اسم المريض لاستعراض ملفه", df['Patient'].unique())
            p_file = df[df['Patient'] == p_select].iloc[-1]
            all_tests = df[df['Patient'] == p_select]
            
            st.markdown(f"""
                <div class="patient-info-box">
                    <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px;">
                        <div><b>👤 الاسم:</b> {p_file['Patient']}</div>
                        <div><b>🎂 العمر:</b> {p_file['Age']} سنة</div>
                        <div><b>🚻 الجنس:</b> {p_file['Gender']}</div>
                        <div><b>🏥 المختبر:</b> {p_file['LabName']}</div>
                        <div><b>👨‍⚕️ الدكتور:</b> {p_file['DoctorName']}</div>
                        <div><b>⏰ وقت التسجيل:</b> {p_file['Timestamp']}</div>
                        <div><b>📅 تاريخ الزيارة:</b> {p_file['Date']}</div>
                        <div><b>🆔 رقم المريض:</b> {p_file['PID']}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            st.write("📋 **سجل التحاليل الخاصة بالمريض:**")
            st.dataframe(all_tests[['Category', 'Test', 'Result', 'Unit', 'Status', 'Timestamp']], use_container_width=True)
        else:
            st.info("لا توجد بيانات مرضى مسجلة حالياً.")

    with tabs[3]: # الأرشيف
        search = st.text_input("🔍 بحث سريـع...")
        f_df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)] if search else df
        for idx, row in f_df.iloc[::-1].iterrows():
            _, style = get_result_analysis(row['Category'], row['Test'], row['Result'])
            st.markdown(f"""<div class="status-card {style}"><b>👤 {row['Patient']} ({row['Age']} سنة)</b> | {row['Test']}: {row['Result']} {row['Unit']}</div>""", unsafe_allow_html=True)

    with tabs[0]: # الإحصائيات
        c1, c2, c3 = st.columns(3)
        c1.metric("إجمالي المرضى", len(df['Patient'].unique()))
        c2.metric("إيرادات اليوم", f"{profile['currency']}{df[df['Date']==datetime.now().strftime('%Y-%m-%d')]['Price'].sum()}")
        c3.metric("الفحوصات المنفذة", len(df))

    with tabs[4]: # المخزن
        st.write("📦 إدارة المخزون اليدوية")
        if not inv_df.empty: st.table(inv_df)
        else: st.info("المخزن فارغ")

    with tabs[6]: # المالية
        st.dataframe(df[['Date', 'Patient', 'Test', 'Price', 'LabName']])

    with tabs[7]: # الإعدادات
        if st.button("تسجيل الخروج"):
            st.session_state.user_code = None; st.rerun()

    st.markdown(f"<center style='opacity:0.2; margin-top:40px;'>{OWNER_INFO['SYSTEM_VERSION']}</center>", unsafe_allow_html=True)
