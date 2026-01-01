import streamlit as st
import pandas as pd
from datetime import datetime
import os
import urllib.parse

# 1. إعدادات البنية التحتية
st.set_page_config(page_title="نظام المختبر المتكامل v11", layout="wide")
st.markdown("<style> * { direction: rtl; text-align: right; } .stTabs [data-baseweb='tab-list'] { gap: 15px; font-weight: bold; } </style>", unsafe_allow_html=True)

# 2. قاعدة البيانات السحابية المصغرة (حفظ واستعادة)
def save_db(data):
    pd.DataFrame(data).to_csv("lab_master_db.csv", index=False, encoding='utf-8-sig')

def load_db():
    if os.path.exists("lab_master_db.csv"):
        return pd.read_csv("lab_master_db.csv").to_dict('records')
    return []

# 3. تهيئة المتغيرات (لضمان عدم اختفاء أي ميزة)
if 'patients' not in st.session_state: st.session_state.patients = load_db()
if 'inv' not in st.session_state: st.session_state.inv = {"Glucose": 100, "CBC": 100, "HbA1c": 50, "Urea": 50}

# 4. محرك القيم الطبيعية (Normal Ranges)
NR = {
    "Glucose": {"min": 70, "max": 126, "unit": "mg/dL"},
    "CBC": {"min": 12, "max": 16, "unit": "g/dL"},
    "HbA1c": {"min": 4, "max": 5.6, "unit": "%"},
    "Urea": {"min": 15, "max": 45, "unit": "mg/dL"}
}

# --- تقسيم الواجهة إلى 4 أقسام واضحة لا تختفي ---
tab1, tab2, tab3, tab4 = st.tabs(["📝 الإدخال والتشخيص", "📜 الوصل والباركود", "📦 المخزن والديون", "📊 الأداء والأرشيف"])

# التبويب 1: التسجيل والتشخيص
with tab1:
    st.info("إدخال فحص جديد مع تحديد الموظف يدوياً")
    with st.form("entry_form", clear_on_submit=True):
        staff_input = st.text_input("👤 اسم الموظف المسؤول (يدوي)")
        c1, c2 = st.columns(2)
        p_name = c1.text_input("اسم المريض")
        p_test = c1.selectbox("نوع الفحص", list(NR.keys()))
        p_res = c1.number_input(f"النتيجة ({NR[p_test]['unit']})", format="%.2f")
        
        p_price = c2.number_input("السعر الكلي", value=10000)
        p_paid = c2.number_input("الواصل", value=10000)
        p_phone = c2.text_input("رقم الهاتف")
        
        if st.form_submit_button("✅ حفظ وتحليل النتيجة"):
            if staff_input and p_name:
                # التحليل الطبي التلقائي
                status, color = "طبيعي", "green"
                if p_res < NR[p_test]["min"]: status, color = "منخفض", "blue"
                elif p_res > NR[p_test]["max"]: status, color = "مرتفع", "red"
                
                # خصم المخزن
                st.session_state.inv[p_test] -= 1
                
                # إضافة البيانات
                entry = {
                    "التاريخ": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "المريض": p_name, "الفحص": p_test, "النتيجة": p_res,
                    "الحالة": status, "اللون": color, "الموظف": staff_input,
                    "الواصل": p_paid, "الدين": p_price - p_paid, "الهاتف": p_phone
                }
                st.session_state.patients.append(entry)
                save_db(st.session_state.patients)
                st.success(f"تم الحفظ! النتيجة: {status}")
            else: st.warning("يرجى ملء الاسم واسم الموظف")

# التبويب 2: الوصل والباركود (QR Code)
with tab2:
    if st.session_state.patients:
        df = pd.DataFrame(st.session_state.patients)
        selected = st.selectbox("اختر مريضاً لعرض وصله:", df['المريض'].unique())
        if selected:
            d = df[df['المريض'] == selected].iloc[-1]
            qr_data = f"Patient:{d['المريض']}|Res:{d['النتيجة']}|By:{d['الموظف']}"
            qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data={urllib.parse.quote(qr_data)}"
            
            st.markdown(f"""
            <div style="border:3px solid {d['اللون']}; padding:15px; border-radius:10px; background:#fff;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h3 style="margin:0;">وصل مختبر التحليلات</h3>
                    <img src="{qr_url}">
                </div>
                <hr>
                <p><b>المريض:</b> {d['المريض']} | <b>الموظف المسؤول:</b> {d['الموظف']}</p>
                <p><b>الفحص:</b> {d['الفحص']} | <b>النتيجة:</b> <span style="font-size:24px; color:{d['اللون']};">{d['النتيجة']} ({d['الحالة']})</span></p>
                <p><b>المالية:</b> مدفوع {d['الواصل']:,} | متبقي {d['الدين']:,} د.ع</p>
            </div>
            """, unsafe_allow_html=True)
    else: st.info("لا توجد بيانات سجلات.")

# التبويب 3: المخزن والديون
with tab3:
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.subheader("📦 حالة المواد")
        st.table(pd.DataFrame(st.session_state.inv.items(), columns=["المادة", "الكمية"]))
    with col_m2:
        st.subheader("💰 الديون الخارجية")
        if st.session_state.patients:
            total_debt = pd.DataFrame(st.session_state.patients)['الدين'].sum()
            st.error(f"إجمالي مبالغ الديون: {total_debt:,} د.ع")

# التبويب 4: الأداء والأرشيف
with tab4:
    if st.session_state.patients:
        df_all = pd.DataFrame(st.session_state.patients)
        st.write("📈 إنتاجية الموظفين (الأسماء المدخلة يدوياً):")
        st.bar_chart(df_all['الموظف'].value_counts())
        
        st.divider()
        csv_file = df_all.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 تحميل الأرشيف الشامل (Excel)", csv_file, "lab_archive.csv")
        st.dataframe(df_all)
