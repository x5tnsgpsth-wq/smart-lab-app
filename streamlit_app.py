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

# --- 2. نظام الهوية الثابتة ---
OWNER_INFO = {
    "PERMANENT_LAB_NAME": "مختبر النخبة التخصصي",
    "PERMANENT_DOC_NAME": "د. أحمد المصطفى",
    "SYSTEM_VERSION": "v13.0 Ultimate Catalog",
    "LICENSE_KEY": "PREMIUM-2026-X"
}

# --- 3. الموسوعة الطبية الشاملة (جميع التحاليل) ---
LAB_CATALOG = {
    "Hematology (أمراض الدم)": {
        "CBC": (12, 16, "g/dL", 15), "HGB": (12, 18, "g/dL", 10), "PLT": (150, 450, "10^3/uL", 12),
        "WBC": (4, 11, "10^3/uL", 10), "ESR": (0, 20, "mm/hr", 8), "PCV": (37, 52, "%", 10),
        "PT": (11, 13.5, "sec", 15), "PTT": (25, 35, "sec", 15), "Blood Group": (0, 0, "Type", 5)
    },
    "Liver Function (وظائف الكبد)": {
        "ALT (GPT)": (7, 56, "U/L", 12), "AST (GOT)": (10, 40, "U/L", 12), "ALP": (44, 147, "U/L", 15),
        "Albumin": (3.4, 5.4, "g/dL", 10), "Total Bilirubin": (0.1, 1.2, "mg/dL", 10), "Direct Bilirubin": (0, 0.3, "mg/dL", 10)
    },
    "Kidney Function (وظائف الكلى)": {
        "Urea": (15, 45, "mg/dL", 10), "Creatinine": (0.6, 1.2, "mg/dL", 15), "Uric Acid": (3.5, 7.2, "mg/dL", 10),
        "S. Electrolytes (Na+)": (135, 145, "mmol/L", 20), "Potassium (K+)": (3.6, 5.2, "mmol/L", 20)
    },
    "Biochemistry & Lipids": {
        "Glucose (Fasting)": (70, 100, "mg/dL", 5), "HbA1c": (4, 5.6, "%", 25), "S.Cholesterol": (125, 200, "mg/dL", 15),
        "Triglycerides": (50, 150, "mg/dL", 15), "HDL": (40, 60, "mg/dL", 15), "LDL": (0, 100, "mg/dL", 15)
    },
    "Hormones & Vitamins": {
        "TSH": (0.4, 4.0, "mIU/L", 30), "T3": (80, 200, "ng/dL", 30), "T4": (5, 12, "ug/dL", 30),
        "Vitamin D3": (30, 100, "ng/mL", 50), "Ferritin": (20, 250, "ng/mL", 25), "Vitamin B12": (200, 900, "pg/mL", 40),
        "PSA (Prostate)": (0, 4, "ng/mL", 45), "Prolactin": (2, 29, "ng/mL", 35)
    },
    "Immunology & Virology": {
        "CRP": (0, 6, "mg/L", 15), "RF (Rheumatoid)": (0, 20, "IU/mL", 15), "ASO": (0, 200, "IU/mL", 15),
        "HBsAg": (0, 0, "Index", 25), "HCV": (0, 0, "Index", 25), "HIV": (0, 0, "Index", 30),
        "Widal Test": (0, 0, "Titer", 15), "Rose Bengal": (0, 0, "Res", 15)
    },
    "General Tests": {
        "GUE (Urine)": (0, 0, "Physical", 10), "GSE (Stool)": (0, 0, "Physical", 10), "Seminal Fluid": (0, 0, "Analysis", 30)
    }
}

# --- 4. وظائف الإدارة والملفات ---
def get_file_path(extension):
    user_id = "".join(x for x in (st.session_state.get('user_code', 'default')) if x.isalnum())
    return f"user_data_{user_id}.{extension}"

def load_user_profile():
    path = get_file_path("json")
    if os.path.exists(path): return json.load(open(path, "r", encoding="utf-8"))
    return {"lab_name": OWNER_INFO["PERMANENT_LAB_NAME"], "doc_name": OWNER_INFO["PERMANENT_DOC_NAME"], "title": "مدير المختبر", "bio": "أخصائي تحليلات", "currency": "$", "joined": datetime.now().strftime("%Y-%m-%d")}

def get_result_analysis(test, val):
    for cat in LAB_CATALOG.values():
        if test in cat:
            low, high, unit, price = cat[test]
            if low == 0 and high == 0: return "فحص وصفي ℹ️", "normal-green"
            if val < low: return "منخفض 🔵", "critical-red"
            if val > high: return "مرتفع 🔴", "critical-red"
            return "طبيعي 🟢", "normal-green"
    return "غير محدد", "warning-yellow"

# --- 5. واجهة المستخدم ---
if 'user_code' not in st.session_state: st.session_state.user_code = None

if st.session_state.user_code is None:
    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        st.markdown(f"<br><br><h1 style='text-align:center;'>🧬 BioLab Intelligence</h1>", unsafe_allow_html=True)
        code_input = st.text_input("رمز الوصول", type="password")
        if st.button("دخول", use_container_width=True, type="primary"):
            st.session_state.user_code = code_input
            st.rerun()
else:
    profile = load_user_profile()
    db_path, inv_path = get_file_path("csv"), get_file_path("inv")
    df = pd.read_csv(db_path) if os.path.exists(db_path) else pd.DataFrame(columns=["PID", "Date", "Patient", "Category", "Test", "Result", "Unit", "Status", "Price"])
    inv_df = pd.read_csv(inv_path) if os.path.exists(inv_path) else pd.DataFrame(columns=["Item", "Stock", "Expiry", "Unit"])

    st.markdown(f"""<div class="header-style"><h1>{profile['lab_name']}</h1><p>{profile['doc_name']} | {OWNER_INFO['SYSTEM_VERSION']}</p></div>""", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab_inv, tab_ai, tab6, tab_profile = st.tabs(["📊 الإحصائيات", "🧪 تسجيل فحص", "📂 الأرشيف", "📄 التقارير", "📦 المخزون", "🧠 تحليل AI", "💰 المالية", "👤 الملف الشخصي"])

    with tab2:
        with st.form("pro_entry", clear_on_submit=True):
            col1, col2 = st.columns(2)
            p_name = col1.text_input("اسم المريض")
            p_id = col2.text_input("PID", value=datetime.now().strftime("%H%M%S"))
            cat_sel = st.selectbox("القسم", list(LAB_CATALOG.keys()))
            test_sel = st.selectbox("التحليل", list(LAB_CATALOG[cat_sel].keys()))
            res_val = st.number_input(f"النتيجة ({LAB_CATALOG[cat_sel][test_sel][2]})", format="%.2f")
            if st.form_submit_button("حفظ وخصم تلقائي 🚀"):
                if p_name:
                    # خصم المخزون تلقائياً
                    if test_sel in inv_df['Item'].values:
                        idx = inv_df[inv_df['Item'] == test_sel].index[0]
                        if inv_df.at[idx, 'Stock'] > 0: inv_df.at[idx, 'Stock'] -= 1
                        inv_df.to_csv(inv_path, index=False)
                    
                    status, _ = get_result_analysis(test_sel, res_val)
                    new_data = pd.DataFrame([[p_id, datetime.now().strftime("%Y-%m-%d"), p_name, cat_sel, test_sel, res_val, LAB_CATALOG[cat_sel][test_sel][2], status, LAB_CATALOG[cat_sel][test_sel][3]]], columns=df.columns)
                    df = pd.concat([df, new_data], ignore_index=True)
                    df.to_csv(db_path, index=False)
                    st.success("تم الحفظ")

    with tab_inv:
        st.subheader("📦 إدارة المخزون والمحاليل")
        
        # إضافة مادة جديدة
        with st.expander("➕ إضافة مادة جديدة للمخزن"):
            with st.form("add_inv"):
                new_item = st.selectbox("اختر التحليل", [t for cat in LAB_CATALOG.values() for t in cat.keys()])
                new_qty = st.number_input("الكمية الأولية", min_value=1)
                new_exp = st.date_input("الصلاحية")
                if st.form_submit_button("إضافة"):
                    inv_df = pd.concat([inv_df, pd.DataFrame([[new_item, new_qty, str(new_exp), "Test"]], columns=inv_df.columns)], ignore_index=True)
                    inv_df.to_csv(inv_path, index=False)
                    st.rerun()

        # الجرد والتحكم اليدوي بالكمية
        st.markdown("### 📋 جرد المحاليل والتحكم اليدوي")
        if not inv_df.empty:
            for i, row in inv_df.iterrows():
                col_i1, col_i2, col_i3, col_i4 = st.columns([2, 1, 1, 1])
                col_i1.write(f"🧪 **{row['Item']}** (صلاحية: {row['Expiry']})")
                col_i2.write(f"الكمية: **{row['Stock']}**")
                
                if col_i3.button("➕ زيادة", key=f"add_{i}"):
                    inv_df.at[i, 'Stock'] += 1
                    inv_df.to_csv(inv_path, index=False)
                    st.rerun()
                
                if col_i4.button("➖ نقص", key=f"sub_{i}"):
                    if inv_df.at[i, 'Stock'] > 0:
                        inv_df.at[i, 'Stock'] -= 1
                        inv_df.to_csv(inv_path, index=False)
                        st.rerun()
                st.divider()

    with tab1:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("إجمالي المرضى", len(df['Patient'].unique()))
        c2.metric("إيرادات", f"{profile['currency']}{df['Price'].sum()}")
        if not df.empty: st.plotly_chart(px.line(df.groupby('Date').sum(numeric_only=True).reset_index(), x='Date', y='Price'))

    with tab3:
        st.dataframe(df.iloc[::-1], use_container_width=True)

    with tab_profile:
        st.write(f"مرحباً دكتور {profile['doc_name']}")
        if st.button("خروج"):
            st.session_state.user_code = None
            st.rerun()

    st.markdown(f"<center style='opacity:0.2;'>{OWNER_INFO['SYSTEM_VERSION']}</center>", unsafe_allow_html=True)
