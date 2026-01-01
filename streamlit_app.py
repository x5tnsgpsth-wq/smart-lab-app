import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse

# 1. إعدادات الصفحة
st.set_page_config(page_title="المختبر الذكي Pro", layout="wide")

# تنسيق المظهر (ثيم احترافي)
st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    .metric-container { background-color: #f0f2f6; padding: 20px; border-radius: 10px; border: 1px solid #d1d5db; }
    .stButton>button { border-radius: 8px; background-color: #007bff; color: white; height: 3em; }
</style>
""", unsafe_allow_html=True)

# 2. إدارة البيانات (Session State لسرعة التابلت)
if 'data_list' not in st.session_state:
    st.session_state.data_list = []

# 3. واجهة التطبيق
st.sidebar.title("🧪 التحكم بالمختبر")
menu = st.sidebar.selectbox("انتقل إلى:", ["📈 لوحة الإحصائيات والأرباح", "📥 تسجيل فحص ودفع", "📋 سجل المرضى والحسابات", "💾 التصدير والإدارة"])

# --- الشاشة 1: لوحة الإحصائيات ---
if menu == "📈 لوحة الإحصائيات والأرباح":
    st.title("الوضع العام للمختبر")
    if st.session_state.data_list:
        df = pd.DataFrame(st.session_state.data_list)
        
        # الصف الأول: المقاييس المالية
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("إجمالي الإيرادات (د.ع)", f"{df['المدفوع'].sum():,.0f}")
        with c2:
            st.metric("الديون المتبقية (د.ع)", f"{df['المتبقي'].sum():,.0f}", delta=f"{df['المتبقي'].sum():,.0f}", delta_color="inverse")
        with c3:
            high_risk = len(df[df['الحالة'] == "مرتفع ⚠️"])
            st.metric("الحالات المرتفعة اليوم", high_risk)
        
        st.divider()
        
        # الصف الثاني: الرسوم البيانية
        col_left, col_right = st.columns(2)
        with col_left:
            st.subheader("أكثر الفحوصات طلباً")
            st.bar_chart(df['الفحص'].value_counts())
        with col_right:
            st.subheader("توزيع الحالات الطبيعية/المرتفعة")
            # تبسيط العرض للتابلت
            st.write(df['الحالة'].value_counts())
    else:
        st.info("لا توجد بيانات كافية لعرض الإحصائيات. ابدأ بتسجيل أول مريض.")

# --- الشاشة 2: تسجيل فحص ودفع (نفس الكود السابق مع تحسين) ---
elif menu == "📥 تسجيل فحص ودفع":
    st.title("إدخال بيانات مريض جديد")
    with st.form("lab_entry", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("اسم المريض")
            phone = st.text_input("رقم الواتساب (بدون أصفار)")
            test = st.selectbox("نوع الفحص", ["CBC", "HbA1c", "Glucose", "TSH", "Lipid Profile"])
        with col2:
            res = st.number_input("النتيجة", format="%.2f")
            price = st.number_input("سعر الفحص", step=500)
            paid = st.number_input("المبلغ الواصل", step=500)
        
        if st.form_submit_button("حفظ وحساب"):
            entry = {
                "التاريخ": datetime.now().strftime("%Y-%m-%d"),
                "المريض": name, "التواصل": phone, "الفحص": test,
                "النتيجة": res, "السعر": price, "المدفوع": paid,
                "المتبقي": price - paid,
                "الحالة": "مرتفع ⚠️" if res > 110 else "طبيعي ✅"
            }
            st.session_state.data_list.append(entry)
            st.success(f"تم الحفظ! المتبقي على المريض: {price-paid} د.ع")

# --- باقي الأقسام (السجل والتصدير) تتبع نفس المنطق المستقر ---
elif menu == "📋 سجل المرضى والحسابات":
    st.title("سجل المراجعات")
    if st.session_state.data_list:
        df_log = pd.DataFrame(st.session_state.data_list)
        st.dataframe(df_log, use_container_width=True)
    else: st.write("السجل فارغ.")

elif menu == "💾 التصدير والإدارة":
    st.title("إدارة البيانات")
    if st.session_state.data_list:
        csv = pd.DataFrame(st.session_state.data_list).to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 تحميل سجل الإكسل الكامل", csv, "lab_report.csv", "text/csv")
        if st.button("🗑️ مسح كل البيانات"):
            st.session_state.data_list = []
            st.rerun()
