import streamlit as st
import pandas as pd
from datetime import datetime

# 1. إعداد الصفحة
st.set_page_config(page_title="مختبر برو - إدارة المخازن", layout="wide")
st.markdown("""<style> * { direction: rtl; text-align: right; } </style>""", unsafe_allow_html=True)

# 2. إدارة البيانات (استخدام الذاكرة المؤقتة)
if 'data_list' not in st.session_state: st.session_state.data_list = []
if 'inventory' not in st.session_state:
    # بيانات أولية للمخزن لتجربة الميزة
    st.session_state.inventory = [
        {"المادة": "Glucose Kit", "الكمية المتبقية": 5, "تاريخ الانتهاء": "2026-12-01"},
        {"المادة": "HbA1c Strips", "الكمية المتبقية": 12, "تاريخ الانتهاء": "2026-06-15"}
    ]

# 3. القائمة الجانبية
st.sidebar.title("📦 قسم الإدارة")
menu = st.sidebar.radio("القائمة", ["إدخال فحص", "إدارة المخزن", "تنبيهات النواقص"])

if menu == "إدخال فحص":
    st.header("📝 تسجيل فحص")
    with st.form("entry_form"):
        name = st.text_input("اسم المريض")
        test = st.selectbox("نوع الفحص", [item["المادة"] for item in st.session_state.inventory])
        res = st.number_input("النتيجة")
        if st.form_submit_button("حفظ"):
            # منطق لتقليل الكمية من المخزن تلقائياً عند إجراء فحص
            for item in st.session_state.inventory:
                if item["المادة"] == test:
                    if item["الكمية المتبقية"] > 0:
                        item["الكمية المتبقية"] -= 1
                        st.session_state.data_list.append({"المريض": name, "الفحص": test, "النتيجة": res})
                        st.success(f"تم الحفظ! الكمية المتبقية من {test}: {item['الكمية المتبقية']}")
                    else:
                        st.error(f"عذراً! مادة {test} نفدت من المخزن.")

elif menu == "إدارة المخزن":
    st.header("🛒 مراقبة المخزون")
    # إضافة مادة جديدة للمخزن
    with st.expander("➕ إضافة مادة جديدة للمخزن"):
        with st.form("inv_form"):
            new_item = st.text_input("اسم المادة/الكيت")
            new_qty = st.number_input("الكمية المضافة", min_value=1)
            new_exp = st.date_input("تاريخ الانتهاء")
            if st.form_submit_button("إضافة للمخزن"):
                st.session_state.inventory.append({"المادة": new_item, "الكمية المتبقية": new_qty, "تاريخ الانتهاء": str(new_exp)})
                st.rerun()

    # عرض جدول المخزون الحالي
    inv_df = pd.DataFrame(st.session_state.inventory)
    st.table(inv_df)

elif menu == "تنبيهات النواقص":
    st.header("🔔 تنبيهات هامة")
    low_stock = [item for item in st.session_state.inventory if item["الكمية المتبقية"] < 10]
    
    if low_stock:
        for item in low_stock:
            st.warning(f"المادة **{item['المادة']}** قاربت على النفاد! (الكمية الحالية: {item['الكمية المتبقية']})")
    else:
        st.success("جميع المواد متوفرة بكميات جيدة ✅")
