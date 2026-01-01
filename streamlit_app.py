import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime
import plotly.express as px
import io

# --- 1. محرك الإعدادات والنطاقات المرجعية ---
def get_status(test, result):
    # نظام ذكي لتحديد حالة الفحص تلقائياً (مثال لبعض الفحوصات)
    ranges = {
        "Glucose (Fasting)": (70, 100),
        "HbA1c": (4, 5.7),
        "Uric Acid": (3.5, 7.2),
        "Calcium": (8.5, 10.5)
    }
    if test in ranges:
        low, high = ranges[test]
        if result < low: return "🔴 Low"
        if result > high: return "🟡 High"
        return "🟢 Normal"
    return "⚪ Not Set"

def load_settings():
    if 'user_code' not in st.session_state or not st.session_state.user_code: return {}
    safe_id = "".join(x for x in st.session_state.user_code if x.isalnum())
    config_path = f"config_{safe_id}.json"
    default_settings = {"lab_name": "SmartLab Pro", "doctor_name": "Admin", "theme": "Dark"}
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return {**default_settings, **json.load(f)}
    return default_settings

def save_settings(settings):
    safe_id = "".join(x for x in st.session_state.user_code if x.isalnum())
    config_path = f"config_{safe_id}.json"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False)

# --- 2. تهيئة الواجهة ومنع الـ Refresh ---
st.set_page_config(page_title="BioLab Ultra", page_icon="🧬", layout="wide")

st.markdown("""
    <style>
    /* منع السحب للتحديث في الاندرويد */
    html, body, [data-testid="stAppViewContainer"] { overscroll-behavior-y: contain; }
    
    /* تصميم البطاقات الاحترافي */
    .patient-card {
        background: #ffffff; padding: 15px; border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 10px;
        border-right: 5px solid #1e3a8a; color: #1e293b;
    }
    .status-tag { padding: 3px 8px; border-radius: 10px; font-size: 12px; font-weight: bold; }
    
    /* إلغاء الفراغات العلوية */
    .block-container { padding-top: 2rem !important; }
    </style>
""", unsafe_allow_html=True)

if 'user_code' not in st.session_state: st.session_state.user_code = None

# --- 3. شاشة الدخول ---
if st.session_state.user_code is None:
    _, col, _ = st.columns([0.1, 0.8, 0.1])
    with col:
        st.image("https://cdn-icons-png.flaticon.com/512/3063/3063205.png", width=80)
        st.title("BioLab Ultra")
        st.caption("نظام إدارة المختبرات الذكي - إصدار 2026")
        u_code = st.text_input("رمز الدخول", type="password")
        if st.button("دخول للنظام", use_container_width=True, type="primary"):
            st.session_state.user_code = u_code
            st.rerun()
else:
    # --- 4. التطبيق الرئيسي ---
    user_settings = load_settings()
    db_file = f"private_db_{''.join(x for x in st.session_state.user_code if x.isalnum())}.csv"
    
    if 'df' not in st.session_state:
        st.session_state.df = pd.read_csv(db_file) if os.path.exists(db_file) else pd.DataFrame(columns=["ID", "التاريخ", "المريض", "الفحص", "النتيجة", "الحالة", "الهاتف"])

    # الهيدر
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); padding:20px; border-radius:20px; color:white; margin-bottom:20px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div><h2 style="margin:0;">{user_settings.get('lab_name')}</h2><p style="margin:0; opacity:0.8;">د. {user_settings.get('doctor_name')}</p></div>
                <img src="https://cdn-icons-png.flaticon.com/512/2785/2785482.png" width="50">
            </div>
        </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["📋 السجلات", "🧪 إضافة فحص", "📈 إحصائيات", "⚙️ الإعدادات"])

    with tab1:
        st.markdown("### 🔍 البحث عن مريض")
        search = st.text_input("ابحث بالاسم أو الهاتف...", key="main_search")
        
        filtered = st.session_state.df
        if search:
            filtered = filtered[filtered['المريض'].str.contains(search, na=False) | filtered['الهاتف'].str.contains(search, na=False)]

        for index, row in filtered.iloc[::-1].head(10).iterrows():
            st.markdown(f"""
                <div class="patient-card">
                    <div style="display: flex; justify-content: space-between;">
                        <b>👤 {row['المريض']}</b>
                        <span>📅 {row['التاريخ']}</span>
                    </div>
                    <div style="margin-top: 10px;">
                        <span style="background: #e2e8f0; padding: 2px 8px; border-radius: 5px;">{row['الفحص']}</span>
                        <span style="margin-left: 10px;">النتيجة: <b>{row['النتيجة']}</b></span>
                        <span style="float: left;">{row['الحالة']}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
        if st.button("📥 تصدير السجلات لملف Excel", use_container_width=True):
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                st.session_state.df.to_excel(writer, index=False, sheet_name='Sheet1')
            st.download_button(label="تحميل الملف الآن", data=buffer, file_name=f"Lab_Report_{datetime.now().date()}.xlsx")

    with tab2:
        st.markdown("### ✍️ إدخال عينة جديدة")
        with st.form("ultra_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            name = col1.text_input("الاسم الكامل")
            phone = col2.text_input("رقم الهاتف")
            
            test_list = [
                "Glucose (Fasting)", "HbA1c", "CBC", "Uric Acid", "TSH", "Lipid Profile",
                "Creatinine", "Urea", "Calcium", "Vitamin D3", "Vitamin B12", "Ferritin",
                "PSA", "H. Pylori", "Widal Test", "CRP", "ESR", "ALT/AST", "Bilirubin"
            ]
            test = st.selectbox("نوع الفحص المخبري", sorted(test_list))
            result = st.number_input("النتيجة الرقمية", step=0.01)
            
            if st.form_submit_button("حفظ وإصدار التقرير 🚀", use_container_width=True):
                if name:
                    status = get_status(test, result)
                    new_data = pd.DataFrame([[datetime.now().strftime("%H%M%S"), datetime.now().strftime("%Y-%m-%d"), name, test, result, status, phone]], columns=st.session_state.df.columns)
                    st.session_state.df = pd.concat([st.session_state.df, new_data], ignore_index=True)
                    st.session_state.df.to_csv(db_file, index=False)
                    st.toast(f"تم الحفظ بنجاح: {status}", icon="🔬")
                else: st.error("يرجى إدخال الاسم")

    with tab3:
        st.markdown("### 📊 التحليل الذكي")
        if not st.session_state.df.empty:
            c1, c2 = st.columns(2)
            with c1:
                fig1 = px.pie(st.session_state.df, names='الحالة', title="توزيع الحالات الصحية", color_discrete_sequence=px.colors.qualitative.Set3)
                st.plotly_chart(fig1, use_container_width=True)
            with c2:
                fig2 = px.histogram(st.session_state.df, x='الفحص', title="أكثر الفحوصات طلباً")
                st.plotly_chart(fig2, use_container_width=True)
        else: st.info("لا توجد بيانات كافية")

    with tab4:
        st.markdown("### ⚙️ الإعدادات المتقدمة")
        new_lab = st.text_input("اسم المنشأة الطبية", value=user_settings.get('lab_name'))
        new_doc = st.text_input("الطبيب المشرف", value=user_settings.get('doctor_name'))
        
        if st.button("💾 حفظ كافة التغييرات", type="primary", use_container_width=True):
            save_settings({"lab_name": new_lab, "doctor_name": new_doc, "theme": "Dark"})
            st.toast("تم تحديث النظام!")
        
        st.divider()
        if st.button("⬅️ رجوع للخلف", use_container_width=True):
            st.toast("تم العودة للرئيسية")
        
        if st.button("تسجيل الخروج 🚪", type="secondary", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    # شريط سفلي جمالي
    st.markdown("""<div style='text-align: center; color: gray; font-size: 10px; margin-top: 50px;'>BioLab Ultra v2.0 - Secure Cloud Access</div>""", unsafe_allow_html=True)
