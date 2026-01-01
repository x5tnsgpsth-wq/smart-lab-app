import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime
import plotly.express as px
import io

# --- 1. محرك الإعدادات والنطاقات المرجعية ---
def get_status(test, result):
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

# --- 2. الحل الجذري لمنع تحديث الصفحة (Anti-Pull-to-Refresh) ---
st.set_page_config(page_title="BioLab Ultra", page_icon="🧬", layout="wide")

# حقن جافا سكريبت لتعطيل ميزة السحب للتحديث في الأندرويد
st.components.v1.html("""
    <script>
    window.addEventListener('touchstart', function(e) {
        if (e.touches.length !== 1) return;
        this.startPos = e.touches[0].pageY;
    }, {passive: false});

    window.addEventListener('touchmove', function(e) {
        var touch = e.touches[0];
        if (this.startPos < touch.pageY && window.scrollY <= 1) {
            e.preventDefault(); // منع المتصفح من إظهار حلقة التحميل
        }
    }, {passive: false});
    </script>
""", height=0)

# حقن التنسيق الاحترافي وقفل أبعاد الصفحة
st.markdown("""
    <style>
    /* قفل المحتوى ومنع المتصفح من استدعاء ميزة التحديث */
    html, body {
        overscroll-behavior-y: none !important;
        overscroll-behavior: none !important;
        height: 100% !important;
        overflow: hidden !important;
    }
    
    [data-testid="stAppViewContainer"] {
        height: 100vh !important;
        overflow-y: auto !important;
        -webkit-overflow-scrolling: touch;
    }

    /* تصميم البطاقات الاحترافي */
    .patient-card {
        background: #ffffff; padding: 15px; border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 10px;
        border-right: 5px solid #1e3a8a; color: #1e293b;
    }
    
    /* إخفاء الزوائد الافتراضية لزيادة الثبات */
    header { visibility: hidden !important; } 
    footer { visibility: hidden !important; }
    .block-container { padding-top: 1rem !important; }
    </style>
""", unsafe_allow_html=True)

if 'user_code' not in st.session_state: st.session_state.user_code = None

# --- 3. شاشة الدخول ---
if st.session_state.user_code is None:
    _, col, _ = st.columns([0.1, 0.8, 0.1])
    with col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.image("https://cdn-icons-png.flaticon.com/512/3063/3063205.png", width=80)
        st.title("BioLab Ultra")
        u_code = st.text_input("رمز الدخول الشخصي", type="password", key="login_key")
        if st.button("دخول للنظام", use_container_width=True, type="primary"):
            st.session_state.user_code = u_code
            st.rerun()
else:
    # --- 4. التطبيق الرئيسي ---
    user_settings = load_settings()
    db_file = f"private_db_{''.join(x for x in st.session_state.user_code if x.isalnum())}.csv"
    
    if 'df' not in st.session_state:
        st.session_state.df = pd.read_csv(db_file) if os.path.exists(db_file) else pd.DataFrame(columns=["ID", "التاريخ", "المريض", "الفحص", "النتيجة", "الحالة", "الهاتف"])

    # الهيدر الاحترافي المتدرج
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); padding:20px; border-radius:20px; color:white; margin-bottom:20px;">
            <h2 style="margin:0;">{user_settings.get('lab_name')}</h2>
            <p style="margin:0; opacity:0.8;">المشرف: د. {user_settings.get('doctor_name')}</p>
        </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["📋 السجلات", "🧪 إضافة فحص", "📈 إحصائيات", "⚙️ الإعدادات"])

    with tab1:
        search = st.text_input("🔍 بحث عن مريض...", placeholder="الاسم أو الهاتف", key="search_input")
        filtered = st.session_state.df
        if search:
            filtered = filtered[filtered['المريض'].str.contains(search, na=False) | filtered['الهاتف'].str.contains(search, na=False)]

        # عرض البيانات بنظام البطاقات (Card System)
        if not filtered.empty:
            for index, row in filtered.iloc[::-1].head(20).iterrows():
                st.markdown(f"""
                    <div class="patient-card">
                        <div style="display: flex; justify-content: space-between;">
                            <b>👤 {row['المريض']}</b>
                            <small style="color:gray;">{row['التاريخ']}</small>
                        </div>
                        <div style="margin-top:8px;">
                            <span>{row['الفحص']}: <b>{row['النتيجة']}</b></span>
                            <span style="float:left; font-weight:bold;">{row['الحالة']}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            # زر تصدير البيانات
            buffer = io.BytesIO()
            st.session_state.df.to_excel(buffer, index=False)
            st.download_button("📥 تحميل كافة السجلات (Excel)", data=buffer.getvalue(), file_name="lab_export.xlsx", use_container_width=True)
        else:
            st.info("لا توجد سجلات حالياً.")

    with tab2:
        with st.container():
            st.markdown("### 🧪 تسجيل عينة جديدة")
            with st.form("ultra_form_no_refresh", clear_on_submit=True):
                col1, col2 = st.columns(2)
                p_name = col1.text_input("اسم المريض الثلاثي")
                p_phone = col2.text_input("رقم الهاتف")
                
                test_options = ["Glucose (Fasting)", "HbA1c", "CBC", "Uric Acid", "TSH", "Creatinine", "Urea", "Lipid Profile", "Vitamin D"]
                p_test = st.selectbox("نوع التحليل", sorted(test_options))
                p_result = st.number_input("النتيجة المخبرية", step=0.01)
                
                if st.form_submit_button("حفظ السجل في السحابة ✅", use_container_width=True):
                    if p_name:
                        status = get_status(p_test, p_result)
                        new_row = pd.DataFrame([[datetime.now().strftime("%H%M%S"), datetime.now().strftime("%Y-%m-%d"), p_name, p_test, p_result, status, p_phone]], columns=st.session_state.df.columns)
                        st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
                        st.session_state.df.to_csv(db_file, index=False)
                        st.toast(f"تم الحفظ: {status}", icon="✅")
                    else: st.error("يرجى إدخال اسم المريض")

    with tab3:
        if not st.session_state.df.empty:
            st.plotly_chart(px.pie(st.session_state.df, names='الحالة', title="توزيع الحالات الصحية العامة", hole=0.3), use_container_width=True)
            st.plotly_chart(px.histogram(st.session_state.df, x='التاريخ', title="نشاط المختبر اليومي"), use_container_width=True)
        else: st.info("قم بإضافة بيانات أولاً لعرض الإحصائيات.")

    with tab4:
        st.markdown("### ⚙️ إدارة النظام")
        n_lab = st.text_input("اسم المختبر", value=user_settings.get('lab_name'))
        n_doc = st.text_input("الطبيب المسؤول", value=user_settings.get('doctor_name'))
        
        if st.button("💾 حفظ الإعدادات", use_container_width=True):
            save_settings({"lab_name": n_lab, "doctor_name": n_doc, "theme": "Dark"})
            st.toast("تم تحديث إعدادات المختبر بنجاح!")
        
        st.divider()
        if st.button("تسجيل الخروج الآمن 🚪", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    st.markdown("<p style='text-align:center; color:gray; font-size:10px;'>BioLab Ultra v2.5 - Stable Android Build</p>", unsafe_allow_html=True)
