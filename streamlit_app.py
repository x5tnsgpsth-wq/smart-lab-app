import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse

# 1. إعدادات الصفحة
st.set_page_config(page_title="مختبر برو - نظام الأرشفة", layout="wide")
st.markdown("""<style> * { direction: rtl; text-align: right; } </style>""", unsafe_allow_html=True)

# 2. إدارة البيانات (استخدام Session State)
if 'data_list' not in st.session_state:
    st.session_state.data_list = []

# 3. القائمة الجانبية
st.sidebar.title("📁 إدارة الأرشيف")
menu = st.sidebar.radio("القائمة", ["إدخال جديد", "البحث والأرشفة", "التقرير المالي اليومي"])

if menu == "إدخال جديد":
    st.header("📝 تسجيل فحص")
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("اسم المريض")
            test = st.selectbox("نوع الفحص", ["CBC", "Glucose", "Urea", "HbA1c", "TSH", "Vitamin D"])
            price = st.number_input("السعر", value=5000)
        with col2:
            res = st.number_input("النتيجة", format="%.2f")
            paid = st.number_input("المدفوع", value=5000)
            date_manual = st.date_input("تاريخ الفحص", datetime.now())
            
        if st.form_submit_button("حفظ"):
            entry = {
                "التاريخ": date_manual.strftime("%Y-%m-%d"),
                "المريض": name, "الفحص": test, "النتيجة": res,
                "المدفوع": paid, "المتبقي": price - paid
            }
            st.session_state.data_list.append(entry)
            st.success("تم الحفظ في الأرشيف")

elif menu == "البحث والأرشفة":
    st.header("🔍 البحث في السجلات السابقة")
    if st.session_state.data_list:
        df = pd.DataFrame(st.session_state.data_list)
        
        col_a, col_b = st.columns(2)
        with col_a:
            search_name = st.text_input("بحث باسم المريض")
        with col_b:
            search_date = st.date_input("أو ابحث بتاريخ محدد", value=None)
        
        # منطق الفلترة
        filtered_df = df
        if search_name:
            filtered_df = filtered_df[filtered_df['المريض'].str.contains(search_name, na=False)]
        if search_date:
            filtered_df = filtered_df[filtered_df['التاريخ'] == search_date.strftime("%Y-%m-%d")]
            
        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.info("الأرشيف فارغ حالياً")

elif menu == "التقرير المالي اليومي":
    st.header("💰 ملخص الحسابات حسب التاريخ")
    if st.session_state.data_list:
        df = pd.DataFrame(st.session_state.data_list)
        target_date = st.date_input("اختر اليوم لاستخراج التقرير:", datetime.now())
        
        day_data = df[df['التاريخ'] == target_date.strftime("%Y-%m-%d")]
        
        if not day_data.empty:
            c1, c2 = st.columns(2)
            c1.metric("إجمالي الدخل النقدي", f"{day_data['المدفوع'].sum():,} د.ع")
            c2.metric("إجمالي الديون المسجلة", f"{day_data['المتبقي'].sum():,} د.ع")
            st.table(day_data[['المريض', 'الفحص', 'المدفوع']])
        else:
            st.warning("لا توجد فحوصات مسجلة لهذا التاريخ")
