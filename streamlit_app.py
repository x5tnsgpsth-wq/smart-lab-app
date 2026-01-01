import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. إعدادات الصفحة
st.set_page_config(page_title="Lab Smart System", layout="wide")

# 2. وظائف قاعدة البيانات
DB_FILE = "lab_database.csv"

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["التاريخ", "المريض", "الفحص", "النتيجة", "الحالة", "الموظف", "الهاتف"])

# تحميل البيانات في ذاكرة التطبيق
if 'df' not in st.session_state:
    st.session_state.df = load_data()

# 3. واجهة المستخدم
st.title("🔬 نظام المختبر الاحترافي")

tabs = st.tabs(["📝 تسجيل فحص", "📊 السجلات والتحليل", "📦 المخزن"])

with tabs[0]:
    with st.form("entry_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("اسم المريض")
            test = st.selectbox("نوع الفحص", ["Glucose", "CBC", "HbA1c", "Urea"])
            res = st.number_input("النتيجة", format="%.2f")
        with col2:
            phone = st.text_input("رقم الهاتف")
            staff = st.text_input("المحلل المسؤول")
        
        if st.form_submit_button("حفظ النتيجة"):
            if name and staff:
                # تحديد الحالة
                status = "طبيعي" # تبسيط للمثال
                new_data = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), name, test, res, status, staff, phone]], 
                                        columns=st.session_state.df.columns)
                st.session_state.df = pd.concat([st.session_state.df, new_data], ignore_index=True)
                st.session_state.df.to_csv(DB_FILE, index=False)
                st.success("✅ تم الحفظ بنجاح")
            else:
                st.error("⚠️ يرجى ملء اسم المريض والمحلل")

with tabs[1]:
    if not st.session_state.df.empty:
        st.subheader("📋 سجل المرضى")
        st.dataframe(st.session_state.df, use_container_width=True)
        
        # رسم بياني بسيط (يعمل بدون مكتبات خارجية معقدة)
        st.subheader("📈 إحصائيات الفحوصات")
        test_counts = st.session_state.df['الفحص'].value_counts()
        st.bar_chart(test_counts)
    else:
        st.info("لا توجد بيانات مسجلة بعد.")

with tabs[2]:
    st.subheader("📦 إدارة المواد")
    st.write("سيتم ربط المخزن آلياً في التحديث القادم.")
