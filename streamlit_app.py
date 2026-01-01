import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime
import plotly.express as px
import io

# --- 1. حماية الواجهة (منع حلقة التحديث) ---
st.set_page_config(page_title="BioLab Pro Max", page_icon="🧬", layout="wide")

st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] {
        overflow: hidden !important;
        position: fixed !important;
        width: 100% !important; height: 100% !important;
        overscroll-behavior-y: none !important;
        touch-action: none !important;
    }
    [data-testid="stMainViewContainer"] {
        overflow-y: auto !important;
        height: 100vh !important;
        -webkit-overflow-scrolling: touch !important;
        touch-action: pan-y !important;
        overscroll-behavior-y: contain !important;
    }
    .main-header {
        background: linear-gradient(135deg, #064e3b 0%, #059669 100%);
        padding: 25px; border-radius: 20px; color: white; margin-bottom: 20px;
    }
    .metric-card {
        background: #f0fdf4; border: 1px solid #bbf7d0;
        padding: 15px; border-radius: 10px; text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. قاعدة البيانات الموسعة مع الأسعار والقيم الطبيعية ---
LAB_CATALOG = {
    "Hematology": {
        "CBC": {"range": (12, 16), "unit": "g/dL", "price": 10},
        "PLT": {"range": (150, 450), "unit": "10^3/uL", "price": 8}
    },
    "Biochemistry": {
        "Glucose": {"range": (70, 100), "unit": "mg/dL", "price": 5},
        "HbA1c": {"range": (4, 5.6), "unit": "%", "price": 15},
        "Creatinine": {"range": (0.6, 1.2), "unit": "mg/dL", "price": 7}
    },
    "Hormones": {
        "TSH": {"range": (0.4, 4.0), "unit": "mIU/L", "price": 20},
        "Vitamin D3": {"range": (30, 100), "unit": "ng/mL", "price": 35}
    }
}

# --- 3. المحرك البرمجي ---
def load_settings():
    safe_id = "".join(x for x in (st.session_state.get('user_code', 'default')) if x.isalnum())
    p = f"set_{safe_id}.json"
    return json.load(open(p, "r", encoding="utf-8")) if os.path.exists(p) else {"lab_name": "مختبر الثقة", "doc_name": "مدير المختبر"}

def check_result(test, val):
    for cat in LAB_CATALOG.values():
        if test in cat:
            low, high = cat[test]["range"]
            if val < low: return "منخفض 🔵", "#dbeafe"
            if val > high: return "مرتفع 🔴", "#fee2e2"
            return "طبيعي 🟢", "#dcfce7"
    return "غير محدد", "#f3f4f6"

# --- 4. واجهة المستخدم ---
if 'user_code' not in st.session_state: st.session_state.user_code = None

if st.session_state.user_code is None:
    st.title("🧬 نظام BioLab الذكي")
    code = st.text_input("رمز الدخول السري", type="password")
    if st.button("دخول"):
        st.session_state.user_code = code
        st.rerun()
else:
    settings = load_settings()
    safe_id = "".join(x for x in st.session_state.user_code if x.isalnum())
    db_file = f"data_{safe_id}.csv"
    df = pd.read_csv(db_file) if os.path.exists(db_file) else pd.DataFrame(columns=["ID", "Date", "Patient", "Test", "Result", "Status", "Price"])

    st.markdown(f'<div class="main-header"><h1>{settings["lab_name"]}</h1><p>د. {settings["doc_name"]}</p></div>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["📊 الإدارة والمالية", "🧪 فحص جديد", "🔍 بحث وتقارير", "⚙️ الإعدادات"])

    with tab1:
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="metric-card"><h3>المرضى اليوم</h3><h2>{len(df[df["Date"] == datetime.now().strftime("%Y-%m-%d")])}</h2></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="metric-card"><h3>إجمالي الإيرادات</h3><h2>${df["Price"].sum()}</h2></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="metric-card"><h3>فحوصات غير طبيعية</h3><h2>{len(df[df["Status"].str.contains("🔴|🔵")])}</h2></div>', unsafe_allow_html=True)
        
        st.divider()
        st.plotly_chart(px.line(df, x="Date", y="Price", title="نمو الإيرادات اليومي"), use_container_width=True)

    with tab2:
        with st.form("add_test"):
            p_name = st.text_input("اسم المريض")
            cat = st.selectbox("قسم التحليل", list(LAB_CATALOG.keys()))
            test = st.selectbox("نوع التحليل", list(LAB_CATALOG[cat].keys()))
            res = st.number_input("النتيجة", format="%.2f")
            if st.form_submit_button("حفظ وإصدار الفاتورة"):
                status, _ = check_result(test, res)
                price = LAB_CATALOG[cat][test]["price"]
                new_row = pd.DataFrame([[datetime.now().strftime("%S%M"), datetime.now().strftime("%Y-%m-%d"), p_name, test, res, status, price]], columns=df.columns)
                df = pd.concat([df, new_row], ignore_index=True)
                df.to_csv(db_file, index=False)
                st.success(f"تم الحفظ. السعر: ${price}")

    with tab3:
        search_id = st.text_input("أدخل اسم المريض للبحث")
        if search_id:
            results = df[df["Patient"].str.contains(search_id)]
            st.dataframe(results)
            # زر تصدير Excel للمريض المحدد
            csv = results.to_csv(index=False).encode('utf-8-sig')
            st.download_button("تحميل التقرير الطبي", csv, f"{search_id}.csv", "text/csv")

    with tab4:
        st.subheader("إعدادات المختبر")
        lab = st.text_input("اسم المختبر", settings["lab_name"])
        doc = st.text_input("اسم الطبيب", settings["doc_name"])
        if st.button("حفظ الإعدادات"):
            with open(f"set_{safe_id}.json", "w", encoding="utf-8") as f:
                json.dump({"lab_name": lab, "doc_name": doc}, f)
            st.rerun()
