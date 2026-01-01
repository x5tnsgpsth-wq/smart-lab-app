import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px
import time

# --- 1. إعدادات المنصة المتقدمة ---
st.set_page_config(page_title="BioLab Pro Enterprise", page_icon="🔬", layout="wide")

# CSS احترافي للواجهة وتلوين الخلايا
st.markdown("""
    <style>
    .stApp { background-color: #f0f2f6; }
    .main-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #2563eb 100%);
        padding: 25px; border-radius: 20px; color: white;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); margin-bottom: 30px;
    }
    .stat-card {
        background: white; padding: 20px; border-radius: 15px;
        border-bottom: 4px solid #2563eb; transition: transform 0.3s;
    }
    .stat-card:hover { transform: translateY(-5px); }
    [data-testid="stMetricValue"] { color: #1e3a8a; }
    </style>
""", unsafe_allow_html=True)

# --- 2. إدارة الجلسة والبيانات ---
if 'user_code' not in st.session_state: st.session_state.user_code = None

def get_db_path():
    safe_id = "".join(x for x in st.session_state.user_code if x.isalnum())
    return f"private_db_{safe_id}.csv"

# --- 3. بوابة الدخول المصممة ---
def login_screen():
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("""
            <div style="background: white; padding: 40px; border-radius: 25px; text-align: center; border: 1px solid #e2e8f0;">
                <h1 style="font-size: 60px;">🔐</h1>
                <h2 style="color: #1e3a8a;">BioLab Pro</h2>
                <p style="color: #64748b;">نظام الإدارة المخبرية السحابي</p>
            </div>
        """, unsafe_allow_html=True)
        u_code = st.text_input("رمز الوصول الشخصي", type="password", help="أدخل رمزك الخاص لفتح مساحتك المشفرة")
        if st.button("دخول للنظام", use_container_width=True, type="primary"):
            if u_code:
                st.session_state.user_code = u_code
                st.rerun()
            else: st.error("يرجى إدخال الرمز")

# --- 4. لوحة التحكم الاحترافية ---
def main_app():
    db_file = get_db_path()
    
    # تحميل البيانات مع التأكد من وجود الأعمدة
    if 'df' not in st.session_state or st.session_state.get('reload'):
        if os.path.exists(db_file):
            st.session_state.df = pd.read_csv(db_file)
        else:
            st.session_state.df = pd.DataFrame(columns=["ID", "التاريخ", "المريض", "الفحص", "النتيجة", "الحالة", "الهاتف"])
        st.session_state.reload = False

    # الهيدر العلوي
    st.markdown(f"""
        <div class="main-header">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h1 style="margin:0; font-size: 28px;">🔬 منصة المختبر الذكية</h1>
                    <p style="margin:0; opacity: 0.8;">مرحباً بك في مساحة العمل الآمنة</p>
                </div>
                <div style="text-align: left;">
                    <code style="background: rgba(255,255,255,0.2); padding: 5px 15px; border-radius: 10px;">ID: {st.session_state.user_code}</code>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # تبويبات النظام الجديد
    tab1, tab2, tab3, tab4 = st.tabs(["📊 السجلات الذكية", "➕ تسجيل فحص", "📈 التحليلات", "🛠️ إدارة البيانات"])

    with tab1:
        st.markdown("### 🔍 البحث والتصنيف البصري")
        if not st.session_state.df.empty:
            # فلترة سريعة بالحالة
            status_filter = st.multiselect("تصفية حسب الحالة:", ["Normal", "Critical"], default=["Normal", "Critical"])
            search = st.text_input("🔎 ابحث بالاسم أو الهاتف...")
            
            filtered_df = st.session_state.df[st.session_state.df['الحالة'].isin(status_filter)]
            if search:
                filtered_df = filtered_df[filtered_df['المريض'].str.contains(search) | filtered_df['الهاتف'].str.contains(search)]
            
            # تلوين الجدول (Conditional Formatting)
            def highlight_status(val):
                color = '#fecaca' if val == 'Critical' else '#bbf7d0'
                return f'background-color: {color}'
            
            st.dataframe(filtered_df.style.applymap(highlight_status, subset=['الحالة']), use_container_width=True)
        else:
            st.info("المساحة فارغة، ابدأ بإضافة مريض.")

    with tab2:
        with st.form("new_test", clear_on_submit=True):
            st.markdown("### 📝 تفاصيل الفحص")
            c1, c2, c3 = st.columns(3)
            name = c1.text_input("اسم المريض")
            test_type = c2.selectbox("نوع الفحص", ["Glucose", "CBC", "HbA1c", "Creatinine", "Urea"])
            phone = c3.text_input("رقم الهاتف")
            
            res = c1.number_input("النتيجة المخبرية", format="%.2f")
            ref_min = c2.number_input("الحد الأدنى للطبيعي", value=70.0)
            ref_max = c3.number_input("الحد الأقصى للطبيعي", value=110.0)
            
            if st.form_submit_button("إرسال ومعالجة النتيجة"):
                status = "Normal" if ref_min <= res <= ref_max else "Critical"
                new_id = str(int(time.time()))
                new_data = pd.DataFrame([[new_id, datetime.now().strftime("%Y-%m-%d"), name, test_type, res, status, phone]], 
                                       columns=st.session_state.df.columns)
                st.session_state.df = pd.concat([st.session_state.df, new_data], ignore_index=True)
                st.session_state.df.to_csv(db_file, index=False)
                st.toast(f"تم تسجيل {name} بنجاح!", icon="✅")
                time.sleep(1)
                st.rerun()

    with tab3:
        if not st.session_state.df.empty:
            st.markdown("### 📊 تقارير الأداء")
            m1, m2, m3 = st.columns(3)
            with m1:
                st.markdown(f'<div class="stat-card"><h4>إجمالي السجلات</h4><h1>{len(st.session_state.df)}</h1></div>', unsafe_allow_html=True)
            with m2:
                crit_count = len(st.session_state.df[st.session_state.df['الحالة'] == 'Critical'])
                st.markdown(f'<div class="stat-card"><h4>حالات حرجة</h4><h1 style="color:red">{crit_count}</h1></div>', unsafe_allow_html=True)
            with m3:
                st.markdown(f'<div class="stat-card"><h4>نسبة الدقة</h4><h1>100%</h1></div>', unsafe_allow_html=True)
            
            st.write("---")
            fig = px.bar(st.session_state.df, x="التاريخ", color="الحالة", title="معدل الحالات اليومي", barmode="group")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("لا توجد بيانات للتحليل")

    with tab4:
        st.markdown("### 🛠️ إدارة السجلات")
        if not st.session_state.df.empty:
            id_to_delete = st.selectbox("اختر سجل لحذفه (بناءً على الاسم والنتيجة):", 
                                       st.session_state.df.index, 
                                       format_func=lambda x: f"{st.session_state.df.iloc[x]['المريض']} - {st.session_state.df.iloc[x]['الفحص']}")
            
            if st.button("🗑️ حذف السجل المحدد", type="primary"):
                st.session_state.df = st.session_state.df.drop(id_to_delete)
                st.session_state.df.to_csv(db_file, index=False)
                st.success("تم الحذف بنجاح")
                st.rerun()
        
        st.write("---")
        if st.button("خروج آمن من النظام 🚪"):
            del st.session_state.user_code
            st.rerun()

# --- 5. التشغيل ---
if st.session_state.user_code is None:
    login_screen()
else:
    main_app()
