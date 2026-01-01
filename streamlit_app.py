import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime
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
    
    .trend-up { color: #ef4444; font-weight: bold; }
    .trend-down { color: #3b82f6; font-weight: bold; }
    .trend-stable { color: #10b981; font-weight: bold; }

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
    "SYSTEM_VERSION": "v9.0 Vision & Report Pro",
    "LICENSE_KEY": "PREMIUM-2026-X"
}

# --- 3. الموسوعة الطبية ---
LAB_CATALOG = {
    "Hematology (أمراض الدم)": {
        "CBC": (12, 16, "g/dL", 15), "HGB": (12, 18, "g/dL", 10), "PLT": (150, 450, "10^3/uL", 12),
        "WBC": (4, 11, "10^3/uL", 10), "ESR": (0, 20, "mm/hr", 8), "PCV": (37, 52, "%", 10)
    },
    "Biochemistry (الكيمياء الحيوية)": {
        "Glucose (Fasting)": (70, 100, "mg/dL", 5), "HbA1c": (4, 5.6, "%", 25), "Urea": (15, 45, "mg/dL", 10),
        "Creatinine": (0.6, 1.2, "mg/dL", 15), "ALT (GPT)": (7, 56, "U/L", 12)
    },
    "Hormones (الهرمونات)": {
        "TSH": (0.4, 4.0, "mIU/L", 30), "Vitamin D3": (30, 100, "ng/mL", 50), "Ferritin": (20, 250, "ng/mL", 25)
    }
}

# --- 4. الإدارة والذكاء التحليلي ---
def get_file_path(extension):
    user_id = "".join(x for x in (st.session_state.get('user_code', 'default')) if x.isalnum())
    return f"biolab_intel_{user_id}.{extension}"

def load_lab_settings():
    path = get_file_path("json")
    if os.path.exists(path):
        saved_data = json.load(open(path, "r", encoding="utf-8"))
        return {
            "lab_name": saved_data.get("lab_name", OWNER_INFO["PERMANENT_LAB_NAME"]),
            "doc_name": saved_data.get("doc_name", OWNER_INFO["PERMANENT_DOC_NAME"]),
            "currency": saved_data.get("currency", "$")
        }
    return {"lab_name": OWNER_INFO["PERMANENT_LAB_NAME"], "doc_name": OWNER_INFO["PERMANENT_DOC_NAME"], "currency": "$"}

def get_result_analysis(test, val):
    for cat in LAB_CATALOG.values():
        if test in cat:
            low, high, unit, price = cat[test]
            if val < low: return "منخفض 🔵", "critical-red"
            if val > high: return "مرتفع 🔴", "critical-red"
            return "طبيعي 🟢", "normal-green"
    return "غير محدد", "warning-yellow"

def analyze_health_trend(patient_df, current_test, current_val):
    history = patient_df[patient_df['Test'] == current_test]
    if len(history) < 1: return "سجل بكر 🆕", "trend-stable"
    last_val = history.iloc[-1]['Result']
    diff = current_val - last_val
    if abs(diff) < (last_val * 0.05): return "مستقر ↔️", "trend-stable"
    return (f"ارتفاع ({diff:+.1f}) 📈", "trend-up") if diff > 0 else (f"انخفاض ({diff:.1f}) 📉", "trend-down")

# --- 5. واجهة المستخدم ---
if 'user_code' not in st.session_state: st.session_state.user_code = None

if st.session_state.user_code is None:
    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        st.markdown(f"<br><br><h1 style='text-align:center;'>🧬 BioLab Intelligence</h1><p style='text-align:center;'>{OWNER_INFO['SYSTEM_VERSION']}</p>", unsafe_allow_html=True)
        code_input = st.text_input("رمز التشفير للدخول", type="password")
        if st.button("فتح النظام الآمن", use_container_width=True, type="primary"):
            st.session_state.user_code = code_input
            st.rerun()
else:
    settings = load_lab_settings()
    db_path = get_file_path("csv")
    df = pd.read_csv(db_path) if os.path.exists(db_path) else pd.DataFrame(columns=["PID", "Date", "Patient", "Category", "Test", "Result", "Unit", "Status", "Price"])

    st.markdown(f"""<div class="header-style"><h1>{settings['lab_name']}</h1><p>إدارة {settings['doc_name']} | {OWNER_INFO['SYSTEM_VERSION']}</p></div>""", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab6, tab5 = st.tabs(["📊 الإحصائيات", "🧪 تسجيل فحص", "📂 الأرشيف الذكي", "📄 إصدار تقرير", "💰 المالية", "⚙️ الإعدادات"])

    with tab1:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("إجمالي المرضى", len(df['Patient'].unique()))
        c2.metric("فحوصات اليوم", len(df[df['Date'] == datetime.now().strftime("%Y-%m-%d")]))
        c3.metric("إيرادات الشهر", f"{settings['currency']}{df['Price'].sum():,.0f}")
        c4.metric("حالات حرجة", len(df[df['Status'].str.contains("🔴|🔵")]))
        if not df.empty:
            st.plotly_chart(px.line(df.groupby('Date').sum(numeric_only=True).reset_index(), x='Date', y='Price', title="منحنى النمو"), use_container_width=True)

    with tab2:
        with st.form("pro_entry", clear_on_submit=True):
            col1, col2 = st.columns(2)
            p_name = col1.text_input("اسم المريض")
            p_id = col2.text_input("كود المريض (PID)", value=datetime.now().strftime("%H%M%S"))
            cat_sel = st.selectbox("القسم", list(LAB_CATALOG.keys()))
            test_sel = st.selectbox("التحليل", list(LAB_CATALOG[cat_sel].keys()))
            res_val = st.number_input(f"النتيجة ({LAB_CATALOG[cat_sel][test_sel][2]})", format="%.2f")
            if st.form_submit_button("اعتماد وحفظ 🚀", use_container_width=True):
                if p_name:
                    status, _ = get_result_analysis(test_sel, res_val)
                    unit, price = LAB_CATALOG[cat_sel][test_sel][2], LAB_CATALOG[cat_sel][test_sel][3]
                    new_data = pd.DataFrame([[p_id, datetime.now().strftime("%Y-%m-%d"), p_name, cat_sel, test_sel, res_val, unit, status, price]], columns=df.columns)
                    df = pd.concat([df, new_data], ignore_index=True)
                    df.to_csv(db_path, index=False)
                    st.success(f"تم تسجيل الفحص للمريض {p_name}")
                else: st.error("أدخل الاسم")

    with tab3:
        search = st.text_input("🔍 بحث سريـع...")
        f_df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)] if search else df
        for idx, row in f_df.iloc[::-1].iterrows():
            _, style = get_result_analysis(row['Test'], row['Result'])
            st.markdown(f"""<div class="status-card {style}"><b>👤 {row['Patient']}</b> | {row['Test']}: {row['Result']} {row['Unit']}</div>""", unsafe_allow_html=True)

    # --- ميزة جديدة: نظام إصدار التقرير الطبي الشامل ---
    with tab4:
        st.subheader("📑 إصدار التقرير الطبي الرسمي")
        if not df.empty:
            target_patient = st.selectbox("اختر المريض لإصدار التقرير", df['Patient'].unique())
            patient_results = df[df['Patient'] == target_patient]
            
            if st.button("توليد معاينة التقرير"):
                report_html = f"""
                <div style="padding:30px; border:2px solid #1e40af; border-radius:15px; font-family:Arial; direction:rtl; background:white; color:black;">
                    <div style="text-align:center; border-bottom:2px solid #1e40af; padding-bottom:10px;">
                        <h1 style="margin:0; color:#1e40af;">{settings['lab_name']}</h1>
                        <p style="margin:5px;">إشراف الطبيب: {settings['doc_name']}</p>
                        <p>تاريخ التقرير: {datetime.now().strftime('%Y-%m-%d')}</p>
                    </div>
                    <div style="margin-top:20px;">
                        <p><b>اسم المريض:</b> {target_patient}</p>
                        <p><b>رقم المريض (PID):</b> {patient_results.iloc[0]['PID']}</p>
                    </div>
                    <table style="width:100%; border-collapse:collapse; margin-top:20px; text-align:center;">
                        <thead>
                            <tr style="background:#f3f4f6;">
                                <th style="border:1px solid #ddd; padding:10px;">التحليل</th>
                                <th style="border:1px solid #ddd; padding:10px;">النتيجة</th>
                                <th style="border:1px solid #ddd; padding:10px;">الوحدة</th>
                                <th style="border:1px solid #ddd; padding:10px;">الحالة</th>
                            </tr>
                        </thead>
                        <tbody>
                """
                for _, r in patient_results.iterrows():
                    report_html += f"""
                            <tr>
                                <td style="border:1px solid #ddd; padding:8px;">{r['Test']}</td>
                                <td style="border:1px solid #ddd; padding:8px;"><b>{r['Result']}</b></td>
                                <td style="border:1px solid #ddd; padding:8px;">{r['Unit']}</td>
                                <td style="border:1px solid #ddd; padding:8px;">{r['Status']}</td>
                            </tr>
                    """
                report_html += """
                        </tbody>
                    </table>
                    <div style="margin-top:30px; border-top:1px solid #ddd; padding-top:10px; font-size:12px; color:#555;">
                        * تم إنشاء هذا التقرير تلقائياً بواسطة نظام BioLab Intelligence Pro.
                        <br>توقيع الطبيب: __________________
                    </div>
                </div>
                """
                st.markdown(report_html, unsafe_allow_html=True)
                st.download_button("تحميل التقرير كملف HTML للطباعة", report_html, file_name=f"Report_{target_patient}.html", mime="text/html")
        else:
            st.info("لا توجد بيانات لإصدار تقارير.")

    with tab6:
        st.subheader("💰 الإدارة المالية")
        st.dataframe(df[["Date", "Patient", "Test", "Price"]], use_container_width=True)

    with tab5:
        st.subheader("⚙️ الإعدادات وحماية الملكية")
        st.warning(f"هذا النظام ملك لـ {OWNER_INFO['PERMANENT_LAB_NAME']}")
        n_l = st.text_input("اسم المختبر", settings['lab_name'])
        n_d = st.text_input("اسم الطبيب", settings['doc_name'])
        if st.button("حفظ التعديلات"):
            with open(get_file_path("json"), "w", encoding="utf-8") as f:
                json.dump({"lab_name": n_l, "doc_name": n_d, "currency": settings['currency']}, f)
            st.rerun()
        if st.button("إعادة ضبط المصنع ⚠️"):
            if os.path.exists(get_file_path("json")): os.remove(get_file_path("json"))
            st.rerun()

    st.markdown(f"<center style='opacity:0.2; margin-top:40px;'>BioLab Intelligence {OWNER_INFO['SYSTEM_VERSION']}</center>", unsafe_allow_html=True)
