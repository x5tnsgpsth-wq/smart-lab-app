import streamlit as st
import pandas as pd
from datetime import datetime

# 1. إعداد الصفحة والستايل
st.set_page_config(page_title="المختبر المتكامل Pro", layout="wide")
st.markdown("<style> * { direction: rtl; text-align: right; } .stTabs [data-baseweb='tab-list'] { gap: 20px; } </style>", unsafe_allow_html=True)

# 2. البيانات الأساسية (تخزين مستقر)
if 'patients' not in st.session_state: st.session_state.patients = []
if 'inv' not in st.session_state: st.session_state.inv = {"Glucose": 100, "CBC": 100, "HbA1c": 50}

# 3. التبويبات الرئيسية (لضمان ظهور كل الميزات)
tab1, tab2, tab3, tab4 = st.tabs(["➕ تسجيل فحص", "📋 السجل والديون", "📦 المخزن", "📊 الأرباح والموظفين"])

# --- التبويب 1: تسجيل فحص (إضافة اسم الموظف يدوياً) ---
with tab1:
    st.subheader("📝 إدخال بيانات الفحص الجديد")
    with st.form("entry_form", clear_on_submit=True):
        col_staff = st.columns(1)[0]
        # ميزة الإضافة اليدوية لاسم الموظف هنا
        current_user = col_staff.text_input("اسم الموظف المسؤول (أدخل اسمك هنا)")
        
        st.divider()
        
        col1, col2 = st.columns(2)
        p_name = col1.text_input("اسم المريض")
        p_test = col1.selectbox("نوع الفحص", list(st.session_state.inv.keys()))
        p_res = col1.number_input("النتيجة", format="%.2f")
        
        p_price = col2.number_input("السعر الكلي", value=10000)
        p_paid = col2.number_input("المبلغ المدفوع", value=10000)
        p_phone = col2.text_input("رقم الهاتف")
        
        if st.form_submit_button("حفظ وتوثيق البيانات"):
            if not current_user:
                st.error("يرجى كتابة اسم الموظف أولاً!")
            elif st.session_state.inv[p_test] > 0:
                st.session_state.inv[p_test] -= 1 # خصم من المخزن
                st.session_state.patients.append({
                    "التاريخ": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "المريض": p_name, 
                    "الفحص": p_test, 
                    "النتيجة": p_res,
                    "الواصل": p_paid, 
                    "الدين": p_price - p_paid, 
                    "الموظف": current_user, # يتم حفظ الاسم الذي كُتب يدوياً
                    "الهاتف": p_phone
                })
                st.success(f"تم الحفظ بنجاح بواسطة: {current_user}")
            else: 
                st.error("المادة نفدت من المخزن!")

# --- التبويب 2: السجل والديون ---
with tab2:
    st.subheader("📋 مراجعة الحسابات والديون")
    if st.session_state.patients:
        df = pd.DataFrame(st.session_state.patients)
        st.dataframe(df, use_container_width=True)
        st.error(f"إجمالي الديون المتبقية في ذمة المرضى: {df['الدين'].sum():,} د.ع")
    else: 
        st.info("السجل فارغ حالياً.")

# --- التبويب 3: المخزن ---
with tab3:
    st.subheader("📦 إدارة المخزون")
    st.table(pd.DataFrame(st.session_state.inv.items(), columns=["المادة", "الكمية المتبقية"]))
    if st.button("➕ تزويد المخزن (إضافة 50 لكل المواد)"):
        for k in st.session_state.inv: st.session_state.inv[k] += 50
        st.rerun()

# --- التبويب 4: الأرباح والإحصائيات ---
with tab4:
    st.subheader("📊 أداء الموظفين والأرباح")
    if st.session_state.patients:
        df_f = pd.DataFrame(st.session_state.patients)
        c1, c2 = st.columns(2)
        c1.metric("إجمالي النقد المستلم", f"{df_f['الواصل'].sum():,} د.ع")
        c2.metric("عدد الفحوصات المنجزة", len(df_f))
        
        st.write("📈 عدد الفحوصات حسب كل موظف (الأسماء التي أُدخلت يدوياً):")
        st.bar_chart(df_f['الموظف'].value_counts())
    else: 
        st.warning("لا توجد بيانات مالية أو إحصائيات لعرضها.")
