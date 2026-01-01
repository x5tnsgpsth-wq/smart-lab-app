import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse

# 1. إعدادات الصفحة
st.set_page_config(page_title="مختبر برو - التنبيه الذكي", layout="wide")
st.markdown("""<style> * { direction: rtl; text-align: right; } .critical { color: red; font-weight: bold; } </style>""", unsafe_allow_html=True)

# 2. إدارة البيانات
if 'data_list' not in st.session_state:
    st.session_state.data_list = []

# وظيفة لتحديد مستوى الخطورة
def check_severity(test, value):
    thresholds = {
        "Glucose": {"high": 200, "critical": 350},
        "HbA1c": {"high": 7, "critical": 10},
        "Urea": {"high": 50, "critical": 100},
        "Creatinine": {"high": 1.2, "critical": 2.5}
    }
    if test in thresholds:
        if value >= thresholds[test]["critical"]: return "🚨 خطر جداً"
        if value >= thresholds[test]["high"]: return "⚠️ مرتفع"
    return "✅ طبيعي"

# 3. واجهة التطبيق
st.sidebar.title("🧬 نظام المختبر")
menu = st.sidebar.radio("القائمة", ["إدخال نتائج", "السجل الشامل", "ملخص الحالات الحرجة"])

if menu == "إدخال نتائج":
    st.header("📝 تسجيل نتيجة فحص")
    with st.form("entry_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("اسم المريض")
            phone = st.text_input("رقم الهاتف")
            test = st.selectbox("نوع الفحص", ["Glucose", "HbA1c", "Urea", "Creatinine"])
        with col2:
            res = st.number_input("النتيجة", format="%.2f")
            price = st.number_input("السعر", value=5000)
            paid = st.number_input("المدفوع", value=5000)
            
        if st.form_submit_button("حفظ النتيجة"):
            severity = check_severity(test, res)
            entry = {
                "التاريخ": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "المريض": name, "الهاتف": phone, "الفحص": test,
                "النتيجة": res, "الحالة": severity,
                "المتبقي": price - paid
            }
            st.session_state.data_list.append(entry)
            if "🚨" in severity:
                st.error(f"تنبيه: نتيجة المريض {name} حرجة جداً!")
            else:
                st.success("تم الحفظ")

elif menu == "السجل الشامل":
    st.header("📋 السجل العام")
    if st.session_state.data_list:
        df = pd.DataFrame(st.session_state.data_list)
        st.table(df) # استخدام Table لضمان ظهور الألوان والرموز بوضوح
    else:
        st.info("لا يوجد بيانات")

elif menu == "ملخص الحالات الحرجة":
    st.header("🚨 الحالات التي تحتاج متابعة")
    if st.session_state.data_list:
        df = pd.DataFrame(st.session_state.data_list)
        critical_df = df[df['الحالة'].str.contains("🚨")]
        if not critical_df.empty:
            st.warning(f"يوجد لديك {len(critical_df)} حالة حرجة اليوم!")
            st.dataframe(critical_df)
        else:
            st.success("كل النتائج ضمن النطاق الآمن حتى الآن.")
