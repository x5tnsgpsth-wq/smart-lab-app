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
    "SYSTEM_VERSION": "v14.0 Multi-Tube & Full Lab",
    "LICENSE_KEY": "PREMIUM-2026-X"
}

# --- 3. الموسوعة المخبرية الشاملة مع التيوبات (أهم إضافة) ---
# تم إضافة تحاليل الألبومين، اليوريا، وظائف الكلى، الدهون وغيرها
LAB_CATALOG = {
    "Hematology (أمراض الدم)": {
        "DefaultTube": "Purple (EDTA) 🟣",
        "Tests": {
            "CBC": (12, 16, "g/dL", 15), "HGB": (12, 18, "g/dL", 10), "PLT": (150, 450, "10^3/uL", 12),
            "WBC": (4, 11, "10^3/uL", 10), "ESR": (0, 20, "mm/hr", 8), "PCV": (37, 52, "%", 10),
            "Blood Group": (0, 0, "Type", 5)
        }
    },
    "Biochemistry (الكيمياء الحيوية)": {
        "DefaultTube": "Yellow (Gel) 🟡",
        "Tests": {
            "Albumin": (3.4, 5.4, "g/dL", 12), "Glucose": (70, 100, "mg/dL", 5), "Urea": (15, 45, "mg/dL", 10),
            "Creatinine": (0.6, 1.2, "mg/dL", 15), "Uric Acid": (3.5, 7.2, "mg/dL", 10), "HbA1c": (4, 5.6, "%", 25),
            "Total Protein": (6.4, 8.3, "g/dL", 10), "S.Cholesterol": (125, 200, "mg/dL", 15), "Triglycerides": (50, 150, "mg/dL", 15)
        }
    },
    "Liver Function (وظائف الكبد)": {
        "DefaultTube": "Yellow (Gel) 🟡",
        "Tests": {
            "ALT (GPT)": (7, 56, "U/L", 12), "AST (GOT)": (10, 40, "U/L", 12), "ALP": (44, 147, "U/L", 15),
            "T. Bilirubin": (0.1, 1.2, "mg/dL", 10), "D. Bilirubin": (0, 0.3, "mg/dL", 10)
        }
    },
    "Hormones & Immunology": {
        "DefaultTube": "Red (Plain) 🔴",
        "Tests": {
            "TSH": (0.4, 4.0, "mIU/L", 30), "Vitamin D3": (30, 100, "ng/mL", 50), "Ferritin": (20, 250, "ng/mL", 25),
            "CRP": (0, 6, "mg/L", 15), "RF": (0, 20, "IU/mL", 15), "ASO": (0, 200, "IU/mL", 15)
        }
    },
    "Coagulation (التخثر)": {
        "DefaultTube": "Blue (Citrate) 🔵",
        "Tests": {
            "PT": (11, 13.5, "sec", 20), "PTT": (25, 35, "sec", 20), "INR": (0.8, 1.2, "Ratio", 20)
        }
    }
}

TUBE_TYPES = [
    "Purple (EDTA) 🟣", "Yellow (Gel) 🟡", "Red (Plain) 🔴", 
    "Blue (Citrate) 🔵", "Green (Heparin) 🟢", "Grey (Fluoride) ⚪", "Black (ESR) ⚫"
]

# --- 4. إدارة الملفات ---
def get_file_path(extension):
    user_id = "".join(x for x in (st.session_state.get('user_code', 'default')) if x.isalnum())
    return f"user_data_{user_id}.{extension}"

def load_user_profile():
    path = get_file_path("json")
    if os.path.exists(path): return json.load(open(path, "r", encoding="utf-8"))
    return {"lab_name": OWNER_INFO["PERMANENT_LAB_NAME"], "doc_name": OWNER_INFO["PERMANENT_DOC_NAME"], "title": "مدير المختبر", "bio": "أخصائي تحليلات", "currency": "$", "joined": datetime.now().strftime("%Y-%m-%d")}

def get_result_analysis(cat_name, test, val):
    tests = LAB_CATALOG[cat_name]["Tests"]
    if test in tests:
        low, high, unit, price = tests[test]
        if low == 0 and high == 0: return "وصفـي ℹ️", "normal-green"
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
        code_input = st.text_input("رمز الدخول الآمن", type="password")
        if st.button("فتح النظام", use_container_width=True, type="primary"):
            st.session_state.user_code = code_input
            st.rerun()
else:
    profile = load_user_profile()
    db_path, inv_path = get_file_path("csv"), get_file_path("inv")
    df = pd.read_csv(db_path) if os.path.exists(db_path) else pd.DataFrame(columns=["PID", "Date", "Patient", "Category", "Test", "Result", "Unit", "Status", "Price", "Tube"])
    inv_df = pd.read_csv(inv_path) if os.path.exists(inv_path) else pd.DataFrame(columns=["Item", "Stock", "Expiry", "Unit"])

    st.markdown(f"""<div class="header-style"><h1>{profile['lab_name']}</h1><p>{profile['doc_name']} | {OWNER_INFO['SYSTEM_VERSION']}</p></div>""", unsafe_allow_html=True)

    tab1, tab2, tab3, tab_inv, tab_profile = st.tabs(["📊 الإحصائيات", "🧪 تسجيل فحص جديد", "📂 الأرشيف الذكي", "📦 المخزن", "👤 البروفايل"])

    with tab2:
        with st.form("entry_form", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            p_name = col_a.text_input("اسم المريض الثلاثي")
            p_id = col_b.text_input("رقم العينة/المريض", value=datetime.now().strftime("%H%M%S"))
            
            cat_sel = st.selectbox("قسم التحليل", list(LAB_CATALOG.keys()))
            test_list = list(LAB_CATALOG[cat_sel]["Tests"].keys())
            test_sel = st.selectbox("نوع التحليل", test_list)
            
            # ميزة جديدة: اختيار نوع التيوب
            default_tube = LAB_CATALOG[cat_sel]["DefaultTube"]
            tube_sel = st.selectbox("نوع أنبوب العينة (Tube)", TUBE_TYPES, index=TUBE_TYPES.index(default_tube))
            
            res_val = st.number_input(f"النتيجة الرقمية ({LAB_CATALOG[cat_sel]['Tests'][test_sel][2]})", format="%.2f")
            
            if st.form_submit_button("اعتماد الفحص وحفظ البيانات 🚀", use_container_width=True):
                if p_name:
                    status, _ = get_result_analysis(cat_sel, test_sel, res_val)
                    unit, price = LAB_CATALOG[cat_sel]["Tests"][test_sel][2], LAB_CATALOG[cat_sel]["Tests"][test_sel][3]
                    
                    # خصم المخزون
                    if test_sel in inv_df['Item'].values:
                        idx = inv_df[inv_df['Item'] == test_sel].index[0]
                        if inv_df.at[idx, 'Stock'] > 0: inv_df.at[idx, 'Stock'] -= 1
                        inv_df.to_csv(inv_path, index=False)

                    new_row = pd.DataFrame([[p_id, datetime.now().strftime("%Y-%m-%d"), p_name, cat_sel, test_sel, res_val, unit, status, price, tube_sel]], columns=df.columns)
                    df = pd.concat([df, new_row], ignore_index=True)
                    df.to_csv(db_path, index=False)
                    st.success(f"تم تسجيل تحليل {test_sel} في أنبوب {tube_sel}")
                else: st.error("يرجى إدخال اسم المريض")

    with tab3:
        st.subheader("🔍 السجل التاريخي للنتائج")
        search = st.text_input("بحث بالاسم أو رقم العينة...")
        f_df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)] if search else df
        
        for idx, row in f_df.iloc[::-1].iterrows():
            _, style = get_result_analysis(row['Category'], row['Test'], row['Result'])
            st.markdown(f"""
                <div class="status-card {style}">
                    <b>👤 {row['Patient']}</b> | التحليل: {row['Test']} | النتيجة: {row['Result']} {row['Unit']} <br>
                    <small>الأنبوب: {row['Tube']} | التاريخ: {row['Date']}</small>
                </div>
            """, unsafe_allow_html=True)

    with tab_inv:
        st.subheader("📦 إدارة المحاليل والتحكم اليدوي")
        
        # تحكم يدوي بالكمية
        if not inv_df.empty:
            for i, row in inv_df.iterrows():
                c_1, c_2, c_3, c_4 = st.columns([2, 1, 1, 1])
                c_1.write(f"🧪 {row['Item']}")
                c_2.write(f"المخزون: {row['Stock']}")
                if c_3.button("➕ زيادة", key=f"up_{i}"):
                    inv_df.at[i, 'Stock'] += 1
                    inv_df.to_csv(inv_path, index=False)
                    st.rerun()
                if c_4.button("➖ نقص", key=f"down_{i}"):
                    if inv_df.at[i, 'Stock'] > 0:
                        inv_df.at[i, 'Stock'] -= 1
                        inv_df.to_csv(inv_path, index=False)
                        st.rerun()
        else:
            st.info("أضف مواد للمخزن من تبويب الإعدادات")

    with tab1:
        st.metric("إجمالي الفحوصات المنفذة", len(df))
        if not df.empty:
            st.plotly_chart(px.pie(df, names='Tube', title="توزيع استخدام الأنابيب"), use_container_width=True)

    st.markdown(f"<center style='opacity:0.3; margin-top:50px;'>BioLab System {OWNER_INFO['SYSTEM_VERSION']}</center>", unsafe_allow_html=True)
