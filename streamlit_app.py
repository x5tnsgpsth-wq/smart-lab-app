import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. إعداد الصفحة
st.set_page_config(page_title="المختبر الاحترافي - نظام الأمان", layout="wide")
st.markdown("<style> * { direction: rtl; text-align: right; } </style>", unsafe_allow_html=True)

# 2. وظيفة الحفظ في ملف (Backup)
def save_to_backup(data):
    df = pd.DataFrame(data)
    df.to_csv("backup_lab_data.csv", index=False, encoding='utf-8-sig')

# تحميل البيانات من النسخة الاحتياطية عند تشغيل التطبيق أول مرة
if 'patients' not in st.session_state:
    if os.path.exists("backup_lab_data.csv"):
        st.session_state.patients = pd.read_csv("backup_lab_data.csv").to_dict('records')
    else:
        st.session_state.patients = []

if 'inventory' not in st.session_state:
    st.session_state.inventory = {"Glucose": 50, "CBC": 30, "HbA1c": 20}

# 3. الواجهة البرمجية
st.sidebar.title("🛡️ أمن البيانات")
menu = st.sidebar.radio("انتقل إلى:", ["تسجيل فحص", "المخزن", "استعادة النسخة الاحتياطية"])

if menu == "تسجيل فحص":
    st.header("📝 إدخال بيانات")
    with st.form("entry_form"):
        name = st.text_input("اسم المريض")
        test = st.selectbox("الفحص", list(st.session_state.inventory.keys()))
        res = st.number_input("النتيجة", format="%.2f")
        paid = st.number_input("المبلغ الواصل", step=500)
        
        if st.form_submit_button("حفظ وتأمين"):
            if st.session_state.inventory[test] > 0:
                st.session_state.inventory[test] -= 1
                entry = {
                    "التاريخ": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "المريض": name, "الفحص": test, "النتيجة": res, "المبلغ": paid
                }
                st.session_state.patients.append(entry)
                # حفظ نسخة احتياطية فورية في ملف
                save_to_backup(st.session_state.patients)
                st.success("✅ تم الحفظ وتأمين نسخة احتياطية!")
            else:
                st.error("⚠️ المادة نفدت!")

elif menu == "المخزن":
    st.header("📦 حالة المخزن الحالية")
    st.write(st.session_state.inventory)

elif menu == "استعادة النسخة الاحتياطية":
    st.header("📂 إدارة الملفات")
    if os.path.exists("backup_lab_data.csv"):
        df_backup = pd.read_csv("backup_lab_data.csv")
        st.write("آخر بيانات تم تأمينها:")
        st.dataframe(df_backup)
        
        # زر لتحميل النسخة الاحتياطية يدوياً للتابلت
        csv = df_backup.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 تحميل النسخة الاحتياطية للجهاز", csv, "manual_backup.csv", "text/csv")
    else:
        st.warning("لا توجد نسخة احتياطية مسجلة بعد.")
