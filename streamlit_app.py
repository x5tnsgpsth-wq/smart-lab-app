import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. إعداد الصفحة
st.set_page_config(page_title="المختبر الذكي - الإدارة المالية", layout="wide")
st.markdown("<style> * { direction: rtl; text-align: right; } </style>", unsafe_allow_html=True)

# 2. البيانات الأساسية (تكلفة المواد لتحديد الربح)
if 'inventory_costs' not in st.session_state:
    st.session_state.inventory_costs = {
        "Glucose": {"price": 10000, "cost": 2000},
        "CBC": {"price": 15000, "cost": 5000},
        "HbA1c": {"price": 20000, "cost": 7000}
    }

if 'patients' not in st.session_state:
    st.session_state.patients = []

# 3. القائمة الجانبية
menu = st.sidebar.radio("الإدارة المالية", ["تسجيل فحص مالي", "تحليل الأرباح الشهرية", "إعدادات الأسعار"])

if menu == "تسجيل فحص مالي":
    st.header("📝 تسجيل فحص مع احتساب الربح")
    with st.form("finance_form"):
        name = st.text_input("اسم المريض")
        test = st.selectbox("نوع الفحص", list(st.session_state.inventory_costs.keys()))
        paid = st.number_input("المبلغ المستلم", value=st.session_state.inventory_costs[test]["price"])
        
        if st.form_submit_button("حفظ وحساب الربح"):
            cost = st.session_state.inventory_costs[test]["cost"]
            profit = paid - cost
            entry = {
                "التاريخ": datetime.now().strftime("%Y-%m"),
                "اليوم": datetime.now().strftime("%d"),
                "المريض": name,
                "الفحص": test,
                "الإيراد": paid,
                "التكلفة": cost,
                "الربح": profit
            }
            st.session_state.patients.append(entry)
            st.success(f"تم الحفظ. صافي الربح من هذا الفحص: {profit:,} د.ع")

elif menu == "تحليل الأرباح الشهرية":
    st.header("📊 ميزانية المختبر")
    if st.session_state.patients:
        df = pd.DataFrame(st.session_state.patients)
        
        # ملخص مالي سريع
        c1, c2, c3 = st.columns(3)
        c1.metric("إجمالي الإيرادات", f"{df['الإيراد'].sum():,} د.ع")
        c2.metric("إجمالي تكلفة المواد", f"{df['التكلفة'].sum():,} د.ع")
        c3.metric("صافي الربح الحقيقي", f"{df['الربح'].sum():,} د.ع", delta=f"{df['الربح'].sum():,}")

        st.divider()
        st.subheader("مخطط النمو اليومي للأرباح")
        # تجميع الأرباح حسب اليوم
        daily_profit = df.groupby('اليوم')['الربح'].sum()
        st.line_chart(daily_profit)
        
        st.subheader("تفاصيل العمليات")
        st.table(df)
    else:
        st.info("لا توجد بيانات مالية متوفرة لهذا الشهر.")

elif menu == "إعدادات الأسعار":
    st.header("⚙️ ضبط تكلفة الفحوصات")
    st.write("حدد سعر البيع وتكلفة المواد لكل فحص لضمان دقة الحسابات:")
    for test, info in st.session_state.inventory_costs.items():
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.inventory_costs[test]["price"] = st.number_input(f"سعر فحص {test}", value=info["price"])
        with col2:
            st.session_state.inventory_costs[test]["cost"] = st.number_input(f"تكلفة مواد {test}", value=info["cost"])
