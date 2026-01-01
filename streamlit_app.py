import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime
import plotly.express as px
import io

# --- 1. إعدادات النظام والقفل النووي لمنع حلقة التحميل ---
st.set_page_config(page_title="BioLab Royal Pro", page_icon="🧬", layout="wide")

st.markdown("""
    <style>
    /* القفل المطلق للمتصفح لمنع Pull-to-Refresh */
    html, body, [data-testid="stAppViewContainer"] {
        overflow: hidden !important;
        position: fixed !important;
        width: 100% !important; height: 100% !important;
        overscroll-behavior: none !important;
        touch-action: none !important;
    }
    [data-testid="stMainViewContainer"] {
        overflow-y: auto !important;
        height: 100vh !important;
        -webkit-overflow-scrolling: touch !important;
        touch-action: pan-y !important;
        overscroll-behavior-y: contain !important;
    }
    /* تنسيق الواجهة الراقية */
    .main-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 30px; border-radius: 20px; color: white;
        margin-bottom: 25px; border-bottom: 5px solid #3b82f6;
        box-shadow: 0 15px 25px rgba(0,0,0,0.2);
    }
    .stTab { background-color: transparent !important; }
    .status-box { padding: 5px 15px; border-radius: 15px; font-weight: bold; }
    header { visibility: hidden !important; }
    </style>
""", unsafe_allow_html=True)

# --- 2. الموسوعة الطبية الشاملة (البيانات المرجعية) ---
LAB_DB = {
    "Hematology": {
        "CBC": {"unit": "g/dL", "range": (12, 16), "price": 15},
        "WBC": {"unit": "10^3/uL", "range": (4, 11), "price": 10},
        "Platelets": {"unit": "10^3/uL", "range": (150, 450), "price": 10}
    },
    "Biochemistry": {
        "Glucose (Fasting)": {"unit": "mg/dL", "range": (70, 100), "price": 5},
        "HbA1c": {"unit": "%", "range": (4, 5.6), "price": 25},
        "Creatinine": {"unit": "mg/dL", "range": (0.6, 1.2), "price": 12},
        "Uric Acid": {"unit": "mg/dL", "range": (3.5, 7.2), "price": 10}
    },
    "Hormones": {
        "TSH": {"unit": "mIU/L", "range": (0.4, 4.0), "price": 30},
        "Vitamin D3": {"unit": "ng/mL", "range": (30, 100), "price": 50}
    },
    "Lipids": {
        "Cholesterol": {"unit": "mg/dL", "range": (125, 200), "price": 15},
        "Triglycerides": {"unit": "mg/dL", "range": (50, 150), "price": 15}
    }
}

# --- 3. إدارة البيانات الذكية ---
def get_user_path(ext):
    user_id = "".join(x for x in (st.session_state.get('user_code', 'guest')) if x.isalnum())
    return f"royal_{user_id}.{ext}"

def load_settings():
    path = get_user_path("json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f: return json.load(f)
    return {"lab_name": "مختبر العائلة الملكي", "doc_name": "الدكتور المدير"}

def analyze_result(test_name, value):
    for cat in LAB_DB.values():
        if test_name in cat:
            low, high = cat[test_name]["range"]
            if value < low: return "منخفض 🔵", "#dbeafe"
            if value > high: return "مرتفع 🔴", "#fee2e2"
            return "طبيعي 🟢", "#dcfce7"
    return "N/A", "#f3f4f6"

# --- 4. واجهة تسجيل الدخول ---
if 'user_code' not in st.session_state: st.session_state.user_code = None

if st.session_state.user_code is None:
    _, col, _ = st.columns([0.1, 0.8, 0.1])
    with col:
        st.markdown("<br><br><center><h1 style='font-size:60px;'>🧬</h1></center>", unsafe_allow_html=True)
        st.title("BioLab Royal Pro")
        st.caption("نظام إدارة المختبرات الأكثر أماناً واستقراراً")
        code = st.text_input("ادخل مفتاح التفعيل", type="password")
        if st.button("فتح النظام", use_container_width=True, type="primary"):
            st.session_state.user_code = code
            st.rerun()
else:
    settings = load_settings()
    db_path = get_user_path("csv")
    df = pd.read_csv(db_path) if os.path.exists(db_path) else pd.DataFrame(columns=["ID", "Date", "Patient", "Category", "Test", "Result", "Unit", "Status", "Price"])

    # الهيدر الملكي
    st.markdown(f"""
        <div class="main-card">
            <h1 style="margin:0; font-size:32px;">{settings['lab_name']}</h1>
            <p style="margin:0; opacity:0.7; font-size:18px;">بإشراف: د. {settings['doc_name']}</p>
        </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["🏛️ لوحة التحكم", "🧪 إضافة فحص", "📂 الأرشيف", "⚙️ الإعدادات"])

    with tab1:
        c1, c2, c3, c4 = st.columns(4)
        today = datetime.now().strftime("%Y-%m-%d")
        c1.metric("مرضى اليوم", len(df[df['Date'] == today]))
        c2.metric("إجمالي الفحوصات", len(df))
        c3.metric("إجمالي الدخل", f"${df['Price'].sum():,.2f}")
        c4.metric("حالات حرجة", len(df[df['Status'].str.contains("🔴")]))
        
        st.divider()
        if not df.empty:
            fig = px.area(df.groupby('Date').sum(numeric_only=True).reset_index(), x='Date', y='Price', title="منحنى النمو المالي")
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        with st.form("new_test_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            p_name = col1.text_input("اسم المريض بالكامل")
            p_phone = col2.text_input("رقم الهاتف (اختياري)")
            
            cat_select = st.selectbox("قسم التحليل", list(LAB_DB.keys()))
            test_select = st.selectbox("نوع التحليل", list(LAB_DB[cat_select].keys()))
            
            res_val = st.number_input(f"النتيجة ({LAB_DB[cat_select][test_select]['unit']})", format="%.2f")
            
            if st.form_submit_button("اعتماد وحفظ النتيجة 🚀", use_container_width=True):
                if p_name:
                    status, _ = analyze_result(test_select, res_val)
                    unit = LAB_DB[cat_select][test_select]['unit']
                    price = LAB_DB[cat_select][test_select]['price']
                    
                    new_row = pd.DataFrame([[
                        datetime.now().strftime("%f"), today, p_name, cat_select, test_select, res_val, unit, status, price
                    ]], columns=df.columns)
                    
                    df = pd.concat([df, new_row], ignore_index=True)
                    df.to_csv(db_path, index=False)
                    st.toast(f"تم حفظ فحص {test_select} للمريض {p_name}")
                else: st.error("يرجى إدخال اسم المريض")

    with tab3:
        search_query = st.text_input("🔍 ابحث عن مريض أو فحص...")
        filtered_df = df[df.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)] if search_query else df
        
        st.dataframe(filtered_df.iloc[::-1], use_container_width=True)
        
        if not filtered_df.empty:
            csv = filtered_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 تحميل النتائج المحددة (Excel/CSV)", csv, "Biolab_Report.csv", "text/csv", use_container_width=True)

    with tab4:
        st.subheader("🛠️ تخصيص النظام")
        new_lab = st.text_input("اسم المختبر الجديد", settings['lab_name'])
        new_doc = st.text_input("اسم الطبيب المسؤول", settings['doc_name'])
        if st.button("حفظ التغييرات 💾", use_container_width=True):
            with open(get_user_path("json"), "w", encoding="utf-8") as f:
                json.dump({"lab_name": new_lab, "doc_name": new_doc}, f)
            st.success("تم تحديث إعدادات المختبر بنجاح!")
            st.rerun()
            
        st.divider()
        if st.button("تسجيل الخروج 🚪", use_container_width=True):
            st.session_state.user_code = None
            st.rerun()

    st.markdown("<center style='opacity:0.3; padding-top:20px;'>BioLab Royal Edition © 2026 - Stable 4.0</center>", unsafe_allow_html=True)
