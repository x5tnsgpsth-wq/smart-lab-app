import streamlit as st
import pandas as pd
from datetime import datetime
import os
import urllib.parse

# 1. إعدادات الصفحة والنمط
st.set_page_config(page_title="مختبر التحليلات - النظام الذكي", layout="wide")
st.markdown("<style> * { direction: rtl; text-align: right; } </style>", unsafe_allow_html=True)

# 2. تعريف المعدلات الطبيعية لكل فحص (يمكنك تعديلها حسب مختبرك)
NORMAL_RANGES = {
    "Glucose": {"min": 70, "max": 126, "unit": "mg/dL"},
    "CBC (Hb)": {"min": 12, "max": 16, "unit": "g/dL"},
    "HbA1c": {"min": 4, "max": 5.6, "unit": "%"},
    "Urea": {"min": 15, "max": 45, "unit": "mg/dL"}
}

# 3. وظائف حفظ واستعادة البيانات
def save_data(data):
    pd.DataFrame(data).to_csv("lab_smart_backup.csv", index=False, encoding='utf-8-sig')

if 'patients' not in st.session_state:
    if os.path.exists("lab_smart_backup.csv"):
        st.session_state.patients = pd.read_csv("lab_smart_backup.csv").to_dict('records')
    else:
        st.session_state.patients = []

# 4. التبويبات
tab1, tab2, tab3 = st.tabs(["📝 إدخال ذكي", "📜 النتائج والتشخيص", "📦 الإدارة"])

with tab1:
    st.subheader("تسجيل الفحص والتحليل التلقائي")
    with st.form("smart_form", clear_on_submit=True):
        staff = st.text_input("👤 اسم المحلل")
        c1, c2 = st.columns(2)
        name = c1.text_input("اسم المريض")
        test = c1.selectbox("نوع الفحص", list(NORMAL_RANGES.keys()))
        res = c1.number_input(f"النتيجة ({NORMAL_RANGES[test]['unit']})", format="%.2f")
        
        price = c2.number_input("السعر", value=10000)
        paid = c2.number_input("الواصل", value=10000)
        phone = c2.text_input("رقم الهاتف")
        
        if st.form_submit_button("حفظ وتحليل"):
            # تحديد حالة النتيجة تلقائياً
            status = "طبيعي"
            color = "green"
            if res < NORMAL_RANGES[test]["min"]:
                status = "منخفض"
                color = "blue"
            elif res > NORMAL_RANGES[test]["max"]:
                status = "مرتفع"
                color = "red"
                
            new_entry = {
                "التاريخ": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "المريض": name, "الفحص": test, "النتيجة": res,
                "الحالة": status, "اللون": color, "المحلل": staff,
                "الواصل": paid, "الدين": price - paid, "الهاتف": phone
            }
            st.session_state.patients.append(new_entry)
            save_data(st.session_state.patients)
            st.success(f"تم الحفظ. حالة النتيجة: {status}")

with tab2:
    if st.session_state.patients:
        df = pd.DataFrame(st.session_state.patients)
        p_sel = st.selectbox("عرض تقرير المريض:", df['المريض'].unique())
        if p_sel:
            data = df[df['المريض'] == p_sel].iloc[-1]
            # توليد الوصل مع تلوين النتيجة حسب الحالة
            st.markdown(f"""
            <div style="border:2px solid {data['اللون']}; padding:20px; border-radius:15px; background:white;">
                <h2 style="color:{data['اللون']};">تقرير مخبري: {data['الحالة']}</h2>
                <hr>
                <p><b>المريض:</b> {data['المريض']} | <b>المحلل:</b> {data['المحلل']}</p>
                <p><b>الفحص:</b> {data['الفحص']} | <b>النتيجة:</b> <span style="font-size:28px;">{data['النتيجة']}</span></p>
                <p><b>المعدل الطبيعي:</b> {NORMAL_RANGES[data['الفحص']]['min']} - {NORMAL_RANGES[data['الفحص']]['max']} {NORMAL_RANGES[data['الفحص']]['unit']}</p>
                <p><b>التاريخ:</b> {data['التاريخ']}</p>
            </div>
            """, unsafe_allow_html=True)
    else: st.info("لا توجد بيانات سجلات.")

with tab3:
    st.subheader("📊 ملخص العمل")
    if st.session_state.patients:
        df_f = pd.DataFrame(st.session_state.patients)
        st.metric("إجمالي الدخل", f"{df_f['الواصل'].sum():,} د.ع")
        st.write("📈 إحصائيات الحالة الصحية للمرضى:")
        st.bar_chart(df_f['الحالة'].value_counts())
