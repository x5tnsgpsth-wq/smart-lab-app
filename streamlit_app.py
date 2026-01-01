import streamlit as st
import pandas as pd
from datetime import datetime

# 1. إعدادات الصفحة
st.set_page_config(page_title="نظام المختبر - إدارة الطاقم", layout="wide")
st.markdown("""<style> * { direction: rtl; text-align: right; } </style>""", unsafe_allow_html=True)

# 2. إدارة البيانات (استخدام Session State)
if 'data_list' not in st.session_state:
    st.session_state.data_list = []

# 3. القائمة الجانبية لإدارة الموظفين
st.sidebar.title("👤 طاقم العمل")
staff_member = st.sidebar.selectbox("الموظف المناوب حالياً:", ["د. أحمد (المدير)", "محلل 1", "محلل 2", "موظف الاستقبال"])
st.sidebar.divider()

menu = st.sidebar.radio("القائمة", ["إدخال نتائج الفحص", "سجل الفحوصات اليومي", "إنتاجية الموظفين"])

if menu == "إدخال نتائج الفحص":
    st.header(f"📝 تسجيل فحص جديد - بواسطة: {staff_member}")
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("اسم المريض")
            test = st.selectbox("نوع الفحص", ["CBC", "Glucose", "Urea", "HbA1c", "Creatinine"])
            price = st.number_input("السعر", value=5000)
        with col2:
            res = st.number_input("النتيجة", format="%.2f")
            paid = st.number_input("المدفوع", value=5000)
            date_manual = st.date_input("تاريخ الفحص", datetime.now())
            
        if st.form_submit_button("حفظ النتيجة في السجل"):
            entry = {
                "التاريخ": date_manual.strftime("%Y-%m-%d"),
                "المريض": name, 
                "الفحص": test, 
                "النتيجة": res,
                "الموظف المسؤول": staff_member, # إضافة اسم الموظف
                "المدفوع": paid, 
                "المتبقي": price - paid
            }
            st.session_state.data_list.append(entry)
            st.success(f"تم الحفظ بنجاح بواسطة {staff_member}")

elif menu == "سجل الفحوصات اليومي":
    st.header("📋 السجل الشامل للنشاط")
    if st.session_state.data_list:
        df = pd.DataFrame(st.session_state.data_list)
        # فلتر حسب الموظف إذا أراد المدير رؤية عمل شخص محدد
        staff_filter = st.multiselect("عرض نتائج موظف محدد:", df['الموظف المسؤول'].unique())
        
        display_df = df
        if staff_filter:
            display_df = df[df['الموظف المسؤول'].isin(staff_filter)]
            
        st.dataframe(display_df, use_container_width=True)
    else:
        st.info("لا توجد بيانات مسجلة")

elif menu == "إنتاجية الموظفين":
    st.header("📊 إحصائيات أداء الطاقم")
    if st.session_state.data_list:
        df = pd.DataFrame(st.session_state.data_list)
        
        # عرض عدد الفحوصات لكل موظف
        st.subheader("عدد الفحوصات المنجزة لكل موظف")
        st.bar_chart(df['الموظف المسؤول'].value_counts())
        
        # عرض المبالغ التي استلمها كل موظف
        st.subheader("المبالغ المستلمة حسب الموظف")
        revenue_by_staff = df.groupby('الموظف المسؤول')['المدفوع'].sum()
        st.table(revenue_by_staff)
    else:
        st.warning("لا توجد بيانات كافية لتحليل الأداء")
