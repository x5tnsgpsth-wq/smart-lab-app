import streamlit as st
import pandas as pd
from datetime import datetime

# 1. إعدادات أساسية
st.set_page_config(page_title="المختبر المتكامل", layout="wide")
st.markdown("<style> * { direction: rtl; text-align: right; } </style>", unsafe_allow_html=True)

# 2. البيانات (تخزين ذكي)
if 'data' not in st.session_state: st.session_state.data = []
if 'inv' not in st.session_state: st.session_state.inv = {"Glucose": 50, "CBC": 30, "Urea": 20}

# 3. القائمة الجانبية
st.sidebar.title("🏥 نظام الإدارة")
user = st.sidebar.selectbox("المحلل:", ["د. محمد", "علي", "سارة"])
page = st.sidebar.radio("الانتقال إلى:", ["📥 تسجيل وحسابات", "📋 السجل والديون", "📦 المخزن والأرباح"])

# --- الصفحة 1: الإدخال والحسابات ---
if page == "📥 تسجيل وحسابات":
    st.subheader(f"تسجيل فحص - الموظف: {user}")
    with st.form("f1", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name = c1.text_input("اسم المريض")
        test = c1.selectbox("الفحص", list(st.session_state.inv.keys()))
        price = c2.number_input("السعر", value=10000)
        paid = c2.number_input("الواصل", value=10000)
        res = st.number_input("النتيجة")
        
        if st.form_submit_button("حفظ"):
            if st.session_state.inv[test] > 0:
                st.session_state.inv[test] -= 1 # خصم من المخزن
                st.session_state.data.append({
                    "التاريخ": datetime.now().strftime("%m-%d %H:%M"),
                    "المريض": name, "الفحص": test, "النتيجة": res,
                    "الواصل": paid, "الدين": price - paid, "المحلل": user
                })
                st.success("تم الحفظ وتحديث المخزن والديون ✅")
            else: st.error("المادة نافدة!")

# --- الصفحة 2: السجل والديون ---
elif page == "📋 السجل والديون":
    st.subheader("📋 سجل المرضى والديون")
    if st.session_state.data:
        df = pd.DataFrame(st.session_state.data)
        st.dataframe(df, use_container_width=True)
        st.metric("إجمالي الديون بذمة المرضى", f"{df['الدين'].sum():,} د.ع")
    else: st.info("لا توجد سجلات")

# --- الصفحة 3: المخزن والأرباح ---
elif page == "📦 المخزن والأرباح":
    st.subheader("📊 الإدارة المالية والمخزن")
    col_inv, col_fin = st.columns(2)
    
    with col_inv:
        st.write("📦 حالة المخزن:")
        st.table(pd.DataFrame(st.session_state.inv.items(), columns=["المادة", "الكمية"]))
        if st.button("تزويد المخزن (إضافة 10)"):
            for k in st.session_state.inv: st.session_state.inv[k] += 10
            st.rerun()

    with col_fin:
        if st.session_state.data:
            df_f = pd.DataFrame(st.session_state.data)
            st.write("💰 الملخص المالي:")
            st.metric("الإيراد النقدي", f"{df_f['الواصل'].sum():,} د.ع")
            st.bar_chart(df_f['المحلل'].value_counts())
