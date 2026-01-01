import streamlit as st
import pandas as pd
from datetime import datetime
import os
import urllib.parse

# 1. إعدادات الصفحة
st.set_page_config(page_title="نظام المختبر المتكامل v13", layout="wide")
st.markdown("<style> * { direction: rtl; text-align: right; } </style>", unsafe_allow_html=True)

# 2. وظائف إدارة البيانات
DB_FILE = "lab_comprehensive_db.csv"
def save_db(data): pd.DataFrame(data).to_csv(DB_FILE, index=False, encoding='utf-8-sig')
def load_db(): return pd.read_csv(DB_FILE).to_dict('records') if os.path.exists(DB_FILE) else []

# 3. تهيئة الجلسة
if 'patients' not in st.session_state: st.session_state.patients = load_db()
if 'inv' not in st.session_state: st.session_state.inv = {"Glucose": 100, "CBC": 100, "HbA1c": 50, "Urea": 50}

# المعدلات الطبيعية
NR = {
    "Glucose": {"min": 70, "max": 126, "unit": "mg/dL"},
    "CBC": {"min": 12, "max": 16, "unit": "g/dL"},
    "HbA1c": {"min": 4, "max": 5.6, "unit": "%"},
    "Urea": {"min": 15, "max": 45, "unit": "mg/dL"}
}

# --- واجهة التبويبات الرئيسية ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 الإدخال والتحليل", "📜 الوصل والباركود", "📦 المخزن والديون", "📊 أداء الموظفين", "⚙️ الإدارة والأمان"])

# التبويب 1: التسجيل
with tab1:
    st.subheader("تسجيل مراجع - إدخال يدوي للموظف")
    with st.form("entry_form", clear_on_submit=True):
        staff_name = st.text_input("👤 اسم الموظف المسؤول (يدوياً)")
        c1, c2 = st.columns(2)
        p_name = c1.text_input("اسم المريض")
        p_test = c1.selectbox("الفحص المجرى", list(NR.keys()))
        p_res = c1.number_input("النتيجة المخبرية", format="%.2f")
        p_price = c2.number_input("السعر", 10000)
        p_paid = c2.number_input("الواصل", 10000)
        p_phone = c2.text_input("رقم الهاتف")
        
        if st.form_submit_button("حفظ وتحليل النتيجة"):
            if staff_name and p_name:
                # التحليل الطبي
                status, color = ("طبيعي", "green") if NR[p_test]["min"] <= p_res <= NR[p_test]["max"] else (("مرتفع", "red") if p_res > NR[p_test]["max"] else ("منخفض", "blue"))
                st.session_state.inv[p_test] -= 1
                entry = {
                    "التاريخ": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "المريض": p_name, "الفحص": p_test, "النتيجة": p_res,
                    "الحالة": status, "اللون": color, "الموظف": staff_name,
                    "الواصل": p_paid, "الدين": p_price - p_paid, "الهاتف": p_phone
                }
                st.session_state.patients.append(entry)
                save_db(st.session_state.patients)
                st.success(f"✅ تم الحفظ. الحالة: {status}")

# التبويب 2: الوصل والباركود
with tab2:
    if st.session_state.patients:
        df = pd.DataFrame(st.session_state.patients)
        p_sel = st.selectbox("اختر مريضاً للوصل:", df['المريض'].unique())
        if p_sel:
            d = df[df['المريض'] == p_sel].iloc[-1]
            qr_text = f"P:{d['المريض']}|R:{d['النتيجة']}|By:{d['الموظف']}"
            qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data={urllib.parse.quote(qr_text)}"
            st.markdown(f'<div style="border:3px solid {d["اللون"]}; padding:20px; border-radius:10px; background:white; color:black;"><div style="display:flex; justify-content:space-between;"><h3>مختبر التحليلات</h3><img src="{qr_url}"></div><hr><p>المريض: {d["المريض"]} | المحلل: {d["الموظف"]}</p><p>النتيجة: <span style="font-size:24px; color:{d["اللون"]};">{d["النتيجة"]} ({d["الحالة"]})</span></p><p>المالية: واصل {d["الواصل"]:,} | متبقي {d["الدين"]:,}</p></div>', unsafe_allow_html=True)

# التبويب 3: المخزن والديون
with tab3:
    st.subheader("📦 الجرد والمواد")
    for k, v in st.session_state.inv.items():
        if v < 10: st.error(f"⚠️ نقص حاد: {k} (المتبقي: {v})")
    st.table(pd.DataFrame(st.session_state.inv.items(), columns=["المادة", "الكمية"]))
    if st.session_state.patients:
        st.warning(f"إجمالي ديون المراجعين: {pd.DataFrame(st.session_state.patients)['الدين'].sum():,}")

# التبويب 4: أداء الموظفين
with tab4:
    st.subheader("📊 إنتاجية الطاقم (الإدخال اليدوي)")
    if st.session_state.patients:
        df_p = pd.DataFrame(st.session_state.patients)
        # إحصائية لكل موظف
        staff_stats = df_p.groupby('الموظف').agg({'الواصل': 'sum', 'المريض': 'count'}).rename(columns={'الواصل': 'المبالغ المستلمة', 'المريض': 'عدد الفحوصات'})
        st.table(staff_stats)
        st.bar_chart(df_p['الموظف'].value_counts())

# التبويب 5: الإدارة والأمان
with tab5:
    st.subheader("🛡️ أمان البيانات والإغلاق")
    if st.session_state.patients:
        df_all = pd.DataFrame(st.session_state.patients)
        st.download_button("📥 تحميل الأرشيف Excel", df_all.to_csv(index=False).encode('utf-8-sig'), "lab_backup.csv")
        
        if st.button("🔴 مسح السجل اليومي (بعد تحميل الأرشيف)"):
            st.session_state.patients = []
            if os.path.exists(DB_FILE): os.remove(DB_FILE)
            st.rerun()
