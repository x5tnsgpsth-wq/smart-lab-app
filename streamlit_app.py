import streamlit as st
import pandas as pd
from datetime import datetime
import os
import urllib.parse

# 1. إعدادات النظام
st.set_page_config(page_title="نظام المختبر الاحترافي v14", layout="wide")
st.markdown("<style> * { direction: rtl; text-align: right; } </style>", unsafe_allow_html=True)

# 2. إدارة قاعدة البيانات
DB_FILE = "lab_pro_master.csv"
def save_db(data): pd.DataFrame(data).to_csv(DB_FILE, index=False, encoding='utf-8-sig')
def load_db(): return pd.read_csv(DB_FILE).to_dict('records') if os.path.exists(DB_FILE) else []

if 'patients' not in st.session_state: st.session_state.patients = load_db()
if 'inv' not in st.session_state: st.session_state.inv = {"Glucose": 100, "CBC": 100, "HbA1c": 50, "Urea": 50}

# 3. محرك الفحوصات
NR = {
    "Glucose": {"min": 70, "max": 126, "unit": "mg/dL"},
    "CBC": {"min": 12, "max": 16, "unit": "g/dL"},
    "HbA1c": {"min": 4, "max": 5.6, "unit": "%"},
    "Urea": {"min": 15, "max": 45, "unit": "mg/dL"}
}

# --- تقسيم الواجهة ---
tab1, tab2, tab3, tab4 = st.tabs(["📝 الاستقبال والنتائج", "📜 طباعة الوصل", "📦 المخزن والديون", "🔐 قسم الإدارة"])

# التبويب 1: التسجيل والتحليل
with tab1:
    with st.form("entry_form", clear_on_submit=True):
        staff = st.text_input("👤 اسم المحلل (يدوياً)")
        st.divider()
        c1, c2 = st.columns(2)
        p_name = c1.text_input("اسم المريض")
        p_test = c1.selectbox("نوع الفحص", list(NR.keys()))
        p_res = c1.number_input(f"النتيجة ({NR[p_test]['unit']})", format="%.2f")
        p_paid = c2.number_input("المبلغ المدفوع", 10000)
        p_total = c2.number_input("السعر الكلي", 10000)
        p_phone = c2.text_input("رقم الهاتف")
        
        if st.form_submit_button("إرسال للتحليل والحفظ"):
            if staff and p_name:
                st.session_state.inv[p_test] -= 1
                status, color = ("طبيعي", "green") if NR[p_test]["min"] <= p_res <= NR[p_test]["max"] else (("مرتفع", "red") if p_res > NR[p_test]["max"] else ("منخفض", "blue"))
                entry = {
                    "التاريخ": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "المريض": p_name, "الفحص": p_test, "النتيجة": p_res,
                    "الحالة": status, "اللون": color, "الموظف": staff,
                    "الواصل": p_paid, "الدين": p_total - p_paid, "الهاتف": p_phone
                }
                st.session_state.patients.append(entry)
                save_db(st.session_state.patients)
                st.success(f"تم الحفظ! النتيجة: {status}")

# التبويب 2: الوصل والباركود
with tab2:
    if st.session_state.patients:
        df = pd.DataFrame(st.session_state.patients)
        selected_p = st.selectbox("اختر مريضاً:", df['المريض'].unique())
        if selected_p:
            d = df[df['المريض'] == selected_p].iloc[-1]
            qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data={urllib.parse.quote(f'Lab-ID:{d['المريض']}')}"
            st.markdown(f'<div style="border:3px solid {d["اللون"]}; padding:20px; background:white; color:black; border-radius:10px;"><div style="display:flex; justify-content:space-between;"><h3>مختبر التحليلات المتقدم</h3><img src="{qr_url}"></div><hr><p>المريض: {d["المريض"]} | المحلل: {d["الموظف"]}</p><p>النتيجة: <span style="font-size:24px; color:{d["اللون"]};">{d["النتيجة"]} ({d["الحالة"]})</span></p><p>المالية: مدفوع {d["الواصل"]:,} | متبقي {d["الدين"]:,}</p></div>', unsafe_allow_html=True)

# التبويب 3: المخزن والديون
with tab3:
    st.subheader("📦 حالة المواد والديون")
    for k, v in st.session_state.inv.items():
        if v < 10: st.error(f"⚠️ نقص في {k}: المتبقي {v}")
    st.table(pd.DataFrame(st.session_state.inv.items(), columns=["المادة", "الكمية المتبقية"]))
    if st.session_state.patients:
        total_debt = pd.DataFrame(st.session_state.patients)['الدين'].sum()
        st.warning(f"مجموع الديون بالخارج: {total_debt:,} د.ع")

# التبويب 4: قسم الإدارة المحمي
with tab4:
    st.subheader("🔐 صلاحيات المسؤول")
    password = st.text_input("أدخل كلمة المرور للوصول للحسابات والمسح", type="password")
    if password == "1234": # يمكنك تغيير كلمة المرور هنا
        st.success("تم تأكيد الصلاحية")
        if st.session_state.patients:
            df_admin = pd.DataFrame(st.session_state.patients)
            st.write("📊 تقرير أداء الموظفين اليومي:")
            st.table(df_admin.groupby('الموظف').agg({'الواصل': 'sum', 'المريض': 'count'}))
            
            st.divider()
            csv_data = df_admin.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 تحميل التقرير اليومي (Excel)", csv_data, "lab_daily_report.csv")
            
            if st.button("🔴 إغلاق الصندوق ومسح اليومية"):
                st.session_state.patients = []
                if os.path.exists(DB_FILE): os.remove(DB_FILE)
                st.rerun()
    elif password != "":
        st.error("كلمة المرور خاطئة!")
