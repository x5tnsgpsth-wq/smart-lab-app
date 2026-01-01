import streamlit as st
import pandas as pd
from datetime import datetime

# إعدادات الصفحة - النسخة الشاملة v3.0
st.set_page_config(page_title="المختبر المتكامل", layout="wide")
st.markdown("<style> * { direction: rtl; text-align: right; } </style>", unsafe_allow_html=True)

# 1. تهيئة البيانات في الذاكرة
if 'patients' not in st.session_state: st.session_state.patients = []
if 'inventory' not in st.session_state:
    st.session_state.inventory = {"Glucose": 50, "CBC": 30, "HbA1c": 20}

# 2. القائمة الجانبية (Sidebar)
st.sidebar.title("🏥 لوحة التحكم")
user = st.sidebar.selectbox("الموظف الحالي:", ["د. محمد", "المحلل علي", "المحللة سارة"])
page = st.sidebar.radio("القائمة:", ["الرئيسية (تسجيل فحص)", "المخزن والنواقص", "السجل المالي العام"])

# --- الصفحة الرئيسية: تسجيل الفحوصات ---
if page == "الرئيسية (تسجيل فحص)":
    st.header(f"مرحباً {user} - تسجيل فحص جديد")
    
    with st.form("lab_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("اسم المريض")
            test = st.selectbox("نوع الفحص", list(st.session_state.inventory.keys()))
        with col2:
            res = st.number_input("النتيجة", format="%.2f")
            paid = st.number_input("المبلغ المدفوع (د.ع)", step=500)
            
        if st.form_submit_button("حفظ البيانات"):
            if st.session_state.inventory[test] > 0:
                # خصم من المخزن
                st.session_state.inventory[test] -= 1
                # حفظ في السجل
                entry = {
                    "التاريخ": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "المريض": name, "الفحص": test, "النتيجة": res,
                    "المبلغ": paid, "الموظف": user
                }
                st.session_state.patients.append(entry)
                st.success(f"تم الحفظ! المتبقي من مواد {test}: {st.session_state.inventory[test]}")
            else:
                st.error(f"عذراً، مادة {test} نفدت من المخزن!")

# --- صفحة المخزن ---
elif page == "المخزن والنواقص":
    st.header("📦 حالة المخزن")
    # عرض كميات المخزن
    for item, qty in st.session_state.inventory.items():
        color = "red" if qty < 5 else "green"
        st.markdown(f"**{item}:** <span style='color:{color}'>{qty} قطعة متبقية</span>", unsafe_allow_html=True)
    
    st.divider()
    st.subheader("➕ تحديث كمية المخزن")
    item_to_add = st.selectbox("اختر المادة لتزويدها:", list(st.session_state.inventory.keys()))
    new_qty = st.number_input("الكمية المضافة:", min_value=1)
    if st.button("تحديث المخزن"):
        st.session_state.inventory[item_to_add] += new_qty
        st.success(f"تم إضافة {new_qty} إلى {item_to_add}")

# --- صفحة السجل المالي ---
elif page == "السجل المالي العام":
    st.header("📋 السجل الشامل")
    if st.session_state.patients:
        df = pd.DataFrame(st.session_state.patients)
        st.table(df)
        st.metric("إجمالي الدخل اليومي", f"{df['المبلغ'].sum():,} د.ع")
    else:
        st.info("لا توجد بيانات حالياً.")
