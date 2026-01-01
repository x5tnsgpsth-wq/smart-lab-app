import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse

# 1. إعداد الصفحة
st.set_page_config(page_title="نظام المختبر المتكامل v5", layout="wide")
st.markdown("<style> * { direction: rtl; text-align: right; } </style>", unsafe_allow_html=True)

# 2. تهيئة البيانات
if 'patients' not in st.session_state: st.session_state.patients = []
if 'inv' not in st.session_state: st.session_state.inv = {"Glucose": 100, "CBC": 100, "HbA1c": 50, "Urea": 50}

# 3. التبويبات
tab1, tab2, tab3 = st.tabs(["📝 تسجيل النتائج", "📋 السجل والتقارير", "📊 الحسابات والمخزن"])

with tab1:
    st.subheader("إدخال فحص جديد")
    with st.form("main_form", clear_on_submit=True):
        staff_name = st.text_input("اسم الموظف المسؤول (يدوي)") # الميزة المطلوبة
        st.divider()
        c1, c2 = st.columns(2)
        p_name = c1.text_input("اسم المريض")
        p_test = c1.selectbox("الفحص", list(st.session_state.inv.keys()))
        p_res = c1.number_input("النتيجة", format="%.2f")
        
        p_price = c2.number_input("السعر", value=10000)
        p_paid = c2.number_input("المدفوع", value=10000)
        p_phone = c2.text_input("رقم الهاتف (اختياري)")
        
        if st.form_submit_button("حفظ النتيجة"):
            if staff_name and p_name:
                st.session_state.inv[p_test] -= 1
                st.session_state.patients.append({
                    "التاريخ": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "المريض": p_name, "الفحص": p_test, "النتيجة": p_res,
                    "الواصل": p_paid, "الدين": p_price - p_paid, 
                    "الموظف": staff_name, "الهاتف": p_phone
                })
                st.success(f"تم الحفظ بواسطة {staff_name}")
            else:
                st.error("يرجى ملء اسم الموظف واسم المريض!")

with tab2:
    st.subheader("سجل النتائج وإرسال التقارير")
    if st.session_state.patients:
        df = pd.DataFrame(st.session_state.patients)
        st.dataframe(df, use_container_width=True)
        
        st.divider()
        st.subheader("📤 إرسال النتيجة للمريض")
        selected_p = st.selectbox("اختر المريض لإرسال تقريره:", df['المريض'].unique())
        
        if selected_p:
            row = df[df['المريض'] == selected_p].iloc[-1]
            # تجهيز نص الرسالة
            msg = f"نتائج مختبرنا:\nالمريض: {row['المريض']}\nالفحص: {row['الفحص']}\nالنتيجة: {row['النتيجة']}\nالحالة: {'طبيعي' if row['النتيجة'] < 150 else 'مرتفع'}\nالمحلل المسؤول: {row['الموظف']}"
            msg_url = urllib.parse.quote(msg)
            
            c1, c2 = st.columns(2)
            # زر واتساب
            c1.markdown(f'''<a href="https://wa.me/{row['الهاتف']}?text={msg_url}" target="_blank">
            <button style="width:100%; background-color:#25D366; color:white; border:none; padding:10px; border-radius:5px;">إرسال عبر WhatsApp</button></a>''', unsafe_allow_html=True)
            # زر تليجرام
            c2.markdown(f'''<a href="https://t.me/share/url?url={msg_url}" target="_blank">
            <button style="width:100%; background-color:#0088cc; color:white; border:none; padding:10px; border-radius:5px;">إرسال عبر Telegram</button></a>''', unsafe_allow_html=True)
    else:
        st.info("لا توجد بيانات سجلات.")

with tab3:
    st.subheader("المخزن والحسابات")
    if st.session_state.patients:
        df_fin = pd.DataFrame(st.session_state.patients)
        st.metric("صافي الدخل النقدي", f"{df_fin['الواصل'].sum():,} د.ع")
        st.write("📊 كميات المواد المتبقية:")
        st.table(pd.DataFrame(st.session_state.inv.items(), columns=["المادة", "الكمية"]))
