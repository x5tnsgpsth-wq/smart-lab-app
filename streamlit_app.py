import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse

# 1. إعدادات الصفحة
st.set_page_config(page_title="نظام المختبر الشامل - الأرشفة والطباعة", layout="wide")
st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    .print-receipt {
        border: 2px solid #000;
        padding: 15px;
        margin: 10px;
        background-color: white;
        color: black;
    }
    @media print {
        .no-print { display: none !important; }
        .stTabs [data-baseweb="tab-list"] { display: none; }
    }
</style>
""", unsafe_allow_html=True)

# 2. تهيئة البيانات
if 'patients' not in st.session_state: st.session_state.patients = []
if 'inv' not in st.session_state: st.session_state.inv = {"Glucose": 100, "CBC": 100, "HbA1c": 50}

# 3. التبويبات
tab1, tab2, tab3, tab4 = st.tabs(["📝 تسجيل", "📜 الوصل والباركود", "💰 المالية والمخزن", "📂 الأرشيف اليومي"])

with tab1:
    st.subheader("تسجيل مراجع جديد")
    with st.form("lab_form"):
        staff_user = st.text_input("👤 اسم المحلل المسؤول (يدوي)")
        c1, c2 = st.columns(2)
        p_name = c1.text_input("اسم المريض")
        p_test = c1.selectbox("الفحص", list(st.session_state.inv.keys()))
        p_res = c1.number_input("النتيجة", format="%.2f")
        p_price = c2.number_input("السعر", value=10000)
        p_paid = c2.number_input("المدفوع", value=10000)
        p_phone = c2.text_input("رقم الهاتف")
        
        if st.form_submit_button("حفظ وتأكيد"):
            if staff_user and p_name:
                st.session_state.inv[p_test] -= 1
                st.session_state.patients.append({
                    "التاريخ": datetime.now().strftime("%Y-%m-%d"),
                    "الوقت": datetime.now().strftime("%H:%M"),
                    "المريض": p_name, "الفحص": p_test, "النتيجة": p_res,
                    "الواصل": p_paid, "الدين": p_price - p_paid, 
                    "الموظف": staff_user, "الهاتف": p_phone
                })
                st.success(f"✅ تم التسجيل بواسطة: {staff_user}")

with tab2:
    st.subheader("📜 معاينة الوصل")
    if st.session_state.patients:
        df = pd.DataFrame(st.session_state.patients)
        p_sel = st.selectbox("اختر المريض للطباعة:", df['المريض'].unique())
        if p_sel:
            data = df[df['المريض'] == p_sel].iloc[-1]
            qr_text = f"Patient:{data['المريض']}|Result:{data['النتيجة']}|Staff:{data['الموظف']}"
            qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data={urllib.parse.quote(qr_text)}"
            
            st.markdown(f"""
            <div class="print-receipt">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h3>مختبر التحليلات المرضية</h3>
                    <img src="{qr_url}">
                </div>
                <hr>
                <p><b>التاريخ:</b> {data['التاريخ']} | <b>الوقت:</b> {data['الوقت']}</p>
                <p><b>اسم المريض:</b> {data['المريض']}</p>
                <p><b>الفحص:</b> {data['الفحص']} | <b>النتيجة:</b> <span style="font-size:22px; color:red;">{data['النتيجة']}</span></p>
                <p><b>المحلل المسؤول:</b> {data['الموظف']}</p>
                <hr>
                <p>الواصل: {data['الواصل']:,} د.ع | المتبقي: {data['الدين']:,} د.ع</p>
            </div>
            """, unsafe_allow_html=True)
            st.button("🖨️ طباعة الوصل (Ctrl+P)", on_click=None)

with tab3:
    st.subheader("💰 الميزانية والمخازن")
    if st.session_state.patients:
        df_fin = pd.DataFrame(st.session_state.patients)
        st.metric("نقد الصندوق اليوم", f"{df_fin['الواصل'].sum():,} د.ع")
        st.warning(f"إجمالي ديون المرضى: {df_fin['الدين'].sum():,} د.ع")
    st.write("📦 المواد المتبقية:")
    st.table(pd.DataFrame(st.session_state.inv.items(), columns=["المادة", "الكمية"]))

with tab4:
    st.subheader("📂 الأرشيف وتصدير البيانات")
    if st.session_state.patients:
        df_arch = pd.DataFrame(st.session_state.patients)
        # تصدير لإكسل
        csv = df_arch.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 تحميل الأرشيف بالكامل (Excel)", csv, "lab_archive.csv", "text/csv")
        st.dataframe(df_arch)
    else:
        st.info("لا توجد بيانات مؤرشفة.")
