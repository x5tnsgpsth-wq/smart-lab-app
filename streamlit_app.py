import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse

# 1. إعدادات النظام الإجبارية لتحديث الواجهة
st.set_page_config(page_title="المختبر الاحترافي v7", layout="wide")
st.markdown("<style> * { direction: rtl; text-align: right; } .stTabs [data-baseweb='tab-list'] { color: blue; font-weight: bold; } </style>", unsafe_allow_html=True)

# 2. تهيئة البيانات (Session State) لضمان عدم الضياع
if 'patients' not in st.session_state: st.session_state.patients = []
if 'inv' not in st.session_state: st.session_state.inv = {"Glucose": 100, "CBC": 100, "HbA1c": 50}

# 3. عرض الميزات عبر "نظام التبويبات" لضمان ظهورها
tab1, tab2, tab3 = st.tabs(["📝 تسجيل الفحوصات", "📜 الوصل والباركود", "💰 الحسابات والمخزن"])

with tab1:
    st.info("قسم إدخال البيانات الجديد")
    with st.form("entry_form"):
        # ميزة الموظف (إدخال يدوياً)
        staff_name = st.text_input("👤 اسم الموظف المسؤول (اكتب اسمك هنا)")
        st.divider()
        c1, c2 = st.columns(2)
        p_name = c1.text_input("اسم المريض الثلاثي")
        p_test = c1.selectbox("نوع الفحص", list(st.session_state.inv.keys()))
        p_res = c1.number_input("النتيجة", format="%.2f")
        
        p_price = c2.number_input("السعر الكلي (د.ع)", value=10000)
        p_paid = c2.number_input("المبلغ الواصل (د.ع)", value=10000)
        p_phone = c2.text_input("رقم الهاتف (للتواصل)")
        
        if st.form_submit_button("✅ حفظ البيانات وإصدار الباركود"):
            if staff_name and p_name:
                st.session_state.inv[p_test] -= 1 # خصم من المخزن
                st.session_state.patients.append({
                    "التاريخ": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "المريض": p_name, "الفحص": p_test, "النتيجة": p_res,
                    "الواصل": p_paid, "الدين": p_price - p_paid, 
                    "الموظف": staff_name, "الهاتف": p_phone
                })
                st.success(f"تم الحفظ! المحلل: {staff_name}")
            else:
                st.warning("يرجى كتابة اسمك واسم المريض!")

with tab2:
    st.subheader("📋 عرض الوصل والباركود (QR)")
    if st.session_state.patients:
        df = pd.DataFrame(st.session_state.patients)
        p_sel = st.selectbox("اختر اسم المريض:", df['المريض'].unique())
        
        if p_sel:
            data = df[df['المريض'] == p_sel].iloc[-1]
            # ميزة الباركود التلقائي
            qr_text = f"Patient:{data['المريض']}|Result:{data['النتيجة']}|Staff:{data['الموظف']}"
            qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={qr_text}"
            
            st.markdown(f"""
            <div style="border:2px solid #ddd; padding:20px; border-radius:10px; background:#fff;">
                <div style="display:flex; justify-content:space-between;">
                    <h2 style="color:#2e7d32;">وصل مختبر التحليلات</h2>
                    <img src="{qr_url}" width="120">
                </div>
                <hr>
                <p><b>اسم المريض:</b> {data['المريض']}</p>
                <p><b>النتيجة:</b> <span style="font-size:24px; color:red;">{data['النتيجة']}</span></p>
                <p><b>المحلل المسؤول:</b> {data['الموظف']}</p>
                <p><b>الحالة المالية:</b> الواصل {data['الواصل']:,} | المتبقي {data['الدين']:,} د.ع</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.write("لا توجد بيانات حالياً.")

with tab3:
    st.subheader("💰 الإدارة والجرد المالي")
    if st.session_state.patients:
        df_fin = pd.DataFrame(st.session_state.patients)
        col_m1, col_m2 = st.columns(2)
        col_m1.metric("إجمالي الصندوق (نقداً)", f"{df_fin['الواصل'].sum():,} د.ع")
        col_m2.metric("إجمالي الديون الخارجية", f"{df_fin['الدين'].sum():,} د.ع", delta_color="inverse")
        
        st.write("📦 حالة المخزن:")
        st.table(pd.DataFrame(st.session_state.inv.items(), columns=["المادة", "الكمية المتبقية"]))
