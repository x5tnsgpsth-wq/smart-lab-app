import streamlit as st
import pandas as pd
from datetime import datetime

# إعداد الصفحة
st.set_page_config(page_title="مختبر برو v2.0", layout="wide")

# إجبار الصفحة على التعرف على التحديث من خلال نص ترحيبي جديد
st.sidebar.info("تحديث النظام: تم إضافة ميزة الموظفين ✅")

# إدارة البيانات
if 'data_list' not in st.session_state:
    st.session_state.data_list = []

# --- ميزة الموظفين الجديدة ---
st.sidebar.title("👤 إدارة الطاقم")
staff_list = ["د. محمد", "المحلل علي", "المحللة سارة", "موظف الاستقبال"]
current_user = st.sidebar.selectbox("اختر الموظف الحالي:", staff_list)

# القائمة الرئيسية
menu = st.sidebar.radio("القائمة", ["إدخال نتائج", "السجل الشامل"])

if menu == "إدخال نتائج":
    st.header(f"📝 إدخال جديد - الموظف: {current_user}")
    with st.form("entry_form"):
        name = st.text_input("اسم المريض")
        test = st.selectbox("نوع الفحص", ["Glucose", "CBC", "HbA1c"])
        res = st.number_input("النتيجة")
        if st.form_submit_button("حفظ"):
            entry = {
                "المريض": name,
                "الفحص": test,
                "النتيجة": res,
                "الموظف المسؤول": current_user, # هذه هي الميزة الجديدة
                "الوقت": datetime.now().strftime("%H:%M")
            }
            st.session_state.data_list.append(entry)
            st.success(f"تم الحفظ بواسطة {current_user}")

elif menu == "السجل الشامل":
    st.header("📋 سجل الفحوصات")
    if st.session_state.data_list:
        df = pd.DataFrame(st.session_state.data_list)
        st.dataframe(df, use_container_width=True)
    else:
        st.write("السجل فارغ.")
