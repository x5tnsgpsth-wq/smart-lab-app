import streamlit as st
import pandas as pd
from datetime import datetime

# 1. إعداد الصفحة والستايل
st.set_page_config(page_title="المختبر المتكامل Pro", layout="wide")
st.markdown("<style> * { direction: rtl; text-align: right; } .stTabs [data-baseweb='tab-list'] { gap: 20px; } </style>", unsafe_allow_html=True)

# 2. البيانات الأساسية (تخزين مستقر)
if 'patients' not in st.session_state: st.session_state.patients = []
if 'inv' not in st.session_state: st.session_state.inv = {"Glucose": 100, "CBC": 100, "HbA1c": 50}
if 'staff' not in st.session_state: st.session_state.staff = ["د. محمد", "علي", "سارة"]

# 3. العنوان الجانبي لاختيار الموظف (ثابت)
st.sidebar.title("👤 الدخول")
current_user = st.sidebar.selectbox("الموظف الحالي:", st.session_state.staff)

# 4. التبويبات الرئيسية (لضمان عدم اختفاء الميزات)
tab1, tab2, tab3, tab4 = st.tabs(["➕ تسجيل فحص", "📋 السجل والديون", "📦 المخزن", "📊 الأرباح والموظفين"])

# --- التبويب 1: تسجيل فحص (مع الموظف والديون) ---
with tab1:
    st.subheader(f"إدخال بيانات - المحلل: {current_user}")
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        p_name = col1.text_input("اسم المريض")
        p_test = col1.selectbox("نوع الفحص", list(st.session_state.inv.keys()))
        p_res = col1.number_input("النتيجة", format="%.2f")
        p_price = col2.number_input("السعر الكلي", value=10000)
        p_paid = col2.number_input("المبلغ المدفوع", value=10000)
        
        if st.form_submit_button("حفظ وتوثيق"):
            if st.session_state.inv[p_test] > 0:
                st.session_state.inv[p_test] -= 1 # خصم من المخزن
                st.session_state.patients.append({
                    "التاريخ": datetime.now().strftime("%Y-%m-%d"),
                    "المريض": p_name, "الفحص": p_test, "النتيجة": p_res,
                    "الواصل": p_paid, "الدين": p_price - p_paid, "الموظف": current_user
                })
                st.success(f"تم الحفظ بواسطة {current_user} ✅")
            else: st.error("المادة نفدت من المخزن!")

# --- التبويب 2: السجل والديون ---
with tab2:
    st.subheader("📋 مراجعة الحسابات والديون")
    if st.session_state.patients:
        df = pd.DataFrame(st.session_state.patients)
        st.dataframe(df, use_container_width=True)
        st.error(f"إجمالي الديون بذمة المرضى: {df['الدين'].sum():,} د.ع")
    else: st.info("السجل فارغ.")

# --- التبويب 3: المخزن ---
with tab3:
    st.subheader("📦 إدارة المخزون")
    st.table(pd.DataFrame(st.session_state.inv.items(), columns=["المادة", "الكمية المتبقية"]))
    if st.button("➕ تزويد المخزن (إضافة 50 لكل المواد)"):
        for k in st.session_state.inv: st.session_state.inv[k] += 50
        st.rerun()

# --- التبويب 4: الأرباح والموظفين (الإحصائيات) ---
with tab4:
    st.subheader("📊 أداء الموظفين والأرباح")
    if st.session_state.patients:
        df_f = pd.DataFrame(st.session_state.patients)
        c1, c2 = st.columns(2)
        c1.metric("إجمالي النقد المستلم", f"{df_f['الواصل'].sum():,} د.ع")
        c2.metric("عدد فحوصات اليوم", len(df_f))
        
        st.write("📈 إنتاجية كل موظف:")
        st.bar_chart(df_f['الموظف'].value_counts())
    else: st.warning("لا توجد إحصائيات بعد.")
