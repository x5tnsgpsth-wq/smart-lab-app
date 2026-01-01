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
    
    .user-profile-box {
        background: rgba(255,255,255,0.1); padding: 10px; border-radius: 15px;
        border: 1px solid rgba(255,255,255,0.2); margin-top: 10px;
    }

    .header-style {
        background: linear-gradient(135deg, #0f172a 0%, #1e40af 100%);
        padding: 35px; border-radius: 25px; color: white;
        margin-bottom: 30px; box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    }
    header { visibility: hidden !important; }
    </style>
""", unsafe_allow_html=True)

# --- 2. نظام الهوية الثابتة والافتراضية ---
OWNER_INFO = {
    "PERMANENT_LAB_NAME": "مختبر النخبة التخصصي",
    "PERMANENT_DOC_NAME": "د. أحمد المصطفى",
    "SYSTEM_VERSION": "v11.0 Multi-User Profile",
    "LICENSE_KEY": "PREMIUM-2026-X"
}

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

# --- 3. إدارة الملفات الشخصية لكل مستخدم ---
def get_file_path(extension):
    user_id = "".join(x for x in (st.session_state.get('user_code', 'default')) if x.isalnum())
    return f"user_data_{user_id}.{extension}"

def load_user_profile():
    path = get_file_path("json")
    if os.path.exists(path):
        return json.load(open(path, "r", encoding="utf-8"))
    return {
        "lab_name": OWNER_INFO["PERMANENT_LAB_NAME"],
        "doc_name": OWNER_INFO["PERMANENT_DOC_NAME"],
        "title": "مدير المختبر",
        "bio": "أخصائي تحليلات مرضية",
        "currency": "$",
        "joined": datetime.now().strftime("%Y-%m-%d")
    }

def get_result_analysis(test, val):
    for cat in LAB_CATALOG.values():
        if test in cat:
            low, high, unit, price = cat[test]
            if val < low: return "منخفض 🔵", "critical-red"
            if val > high: return "مرتفع 🔴", "critical-red"
            return "طبيعي 🟢", "normal-green"
    return "غير محدد", "warning-yellow"

# --- 4. واجهة المستخدم ---
if 'user_code' not in st.session_state: st.session_state.user_code = None

if st.session_state.user_code is None:
    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        st.markdown(f"<br><br><h1 style='text-align:center;'>🧬 BioLab</h1><h4 style='text-align:center;'>نظام الإدارة الشخصي</h4>", unsafe_allow_html=True)
        code_input = st.text_input("أدخل رمز الوصول الخاص بك", type="password", help="كل رمز يفتح ملفاً شخصياً مستقلاً")
        if st.button("دخول للنظام الآمن 🔓", use_container_width=True, type="primary"):
            st.session_state.user_code = code_input
            st.rerun()
else:
    profile = load_user_profile()
    db_path = get_file_path("csv")
    df = pd.read_csv(db_path) if os.path.exists(db_path) else pd.DataFrame(columns=["PID", "Date", "Patient", "Category", "Test", "Result", "Unit", "Status", "Price"])

    # هيدر يعكس شخصية المستخدم
    st.markdown(f"""
        <div class="header-style">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <h1 style="margin:0;">{profile['lab_name']}</h1>
                    <div class="user-profile-box">
                        <b>👤 {profile['doc_name']}</b> | <small>{profile['title']}</small>
                    </div>
                </div>
                <div style="text-align:right;">
                    <h3>{datetime.now().strftime('%Y-%m-%d')}</h3>
                    <code>رمز الوصول: {st.session_state.user_code[:2]}****</code>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab_ai, tab6, tab_profile = st.tabs([
        "📊 الإحصائيات", "🧪 تسجيل فحص", "📂 الأرشيف", "📄 التقارير", "🧠 تحليل AI", "💰 المالية", "👤 الملف الشخصي"
    ])

    with tab1:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("إجمالي مرضاي", len(df['Patient'].unique()))
        c2.metric("فحوصات اليوم", len(df[df['Date'] == datetime.now().strftime("%Y-%m-%d")]))
        c3.metric("رصيد الخزنة", f"{profile['currency']}{df['Price'].sum():,.0f}")
        c4.metric("تنبيهات حرجة", len(df[df['Status'].str.contains("🔴|🔵")]))
        if not df.empty:
            st.plotly_chart(px.area(df.groupby('Date').sum(numeric_only=True).reset_index(), x='Date', y='Price', title="نمو نشاطك العملي"), use_container_width=True)

    with tab2:
        with st.form("pro_entry", clear_on_submit=True):
            col1, col2 = st.columns(2)
            p_name = col1.text_input("اسم المريض")
            p_id = col2.text_input("كود المريض (PID)", value=datetime.now().strftime("%H%M%S"))
            cat_sel = st.selectbox("القسم", list(LAB_CATALOG.keys()))
            test_sel = st.selectbox("التحليل", list(LAB_CATALOG[cat_sel].keys()))
            res_val = st.number_input(f"النتيجة ({LAB_CATALOG[cat_sel][test_sel][2]})", format="%.2f")
            if st.form_submit_button("اعتماد النتيجة في ملفي 🚀", use_container_width=True):
                if p_name:
                    status, _ = get_result_analysis(test_sel, res_val)
                    unit, price = LAB_CATALOG[cat_sel][test_sel][2], LAB_CATALOG[cat_sel][test_sel][3]
                    new_data = pd.DataFrame([[p_id, datetime.now().strftime("%Y-%m-%d"), p_name, cat_sel, test_sel, res_val, unit, status, price]], columns=df.columns)
                    df = pd.concat([df, new_data], ignore_index=True)
                    df.to_csv(db_path, index=False)
                    st.success(f"تم تسجيل الفحص بنجاح في قاعدة بياناتك.")
                else: st.error("أدخل اسم المريض")

    with tab3:
        search = st.text_input("🔍 بحث في أرشيفي الخاص...")
        f_df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)] if search else df
        for idx, row in f_df.iloc[::-1].iterrows():
            _, style = get_result_analysis(row['Test'], row['Result'])
            st.markdown(f"""<div class="status-card {style}"><b>👤 {row['Patient']}</b> | {row['Test']}: {row['Result']} {row['Unit']}</div>""", unsafe_allow_html=True)

    with tab4:
        st.subheader("📑 إصدار تقرير رسمي مختوم")
        if not df.empty:
            target_patient = st.selectbox("اختر مريضاً من سجلك", df['Patient'].unique())
            if st.button("توليد التقرير بتوقيعي"):
                st.info(f"تقرير صادر عن: {profile['doc_name']}")
                # (هنا يوضع كود HTML التقرير السابق مع إضافة توقيع المستخدم)

    with tab_ai:
        st.subheader("🧠 التحليل الذكي لمرضاك")
        st.info("هذا القسم يحلل بيانات مرضاك فقط بناءً على تاريخهم المسجل عندك.")

    with tab6:
        st.subheader("💰 المالية الشخصية")
        st.write(f"إجمالي إيرادات حسابك: {df['Price'].sum()} {profile['currency']}")
        st.dataframe(df[["Date", "Patient", "Test", "Price"]], use_container_width=True)

    with tab_profile:
        st.subheader("👤 إعدادات ملفي الشخصي")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            new_doc = st.text_input("اسمي الكامل", profile['doc_name'])
            new_title = st.text_input("المسمى الوظيفي", profile['title'])
            new_lab = st.text_input("اسم مختبري", profile['lab_name'])
        with col_p2:
            new_bio = st.text_area("نبذة قصيرة (تظهر في التقارير)", profile['bio'])
            new_curr = st.selectbox("العملة المعتمدة", ["$", "IQD", "EGP", "SAR"])
        
        if st.button("حفظ تغييرات ملفي الشخصي 💾"):
            updated_profile = {
                "lab_name": new_lab, "doc_name": new_doc, "title": new_title,
                "bio": new_bio, "currency": new_curr, "joined": profile['joined']
            }
            with open(get_file_path("json"), "w", encoding="utf-8") as f:
                json.dump(updated_profile, f)
            st.success("تم تحديث معلوماتك الشخصية!")
            st.rerun()
        
        st.divider()
        if st.button("تسجيل الخروج من هذا الملف 🚪"):
            st.session_state.user_code = None
            st.rerun()

    st.markdown(f"<center style='opacity:0.2; margin-top:40px;'>{OWNER_INFO['SYSTEM_VERSION']} - ملف مستخدم محمي</center>", unsafe_allow_html=True)
