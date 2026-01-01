import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# 1. إعداد الصفحة
st.set_page_config(page_title="المختبر الاحترافي", layout="wide")
st.markdown("""<style> * { direction: rtl; text-align: right; } </style>""", unsafe_allow_html=True)

# 2. قاعدة البيانات
conn = sqlite3.connect("lab_stable.db", check_same_thread=False)
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS data 
             (id INTEGER PRIMARY KEY, name TEXT, test TEXT, result REAL, price INTEGER, paid INTEGER, date TEXT)""")
conn.commit()

# 3. القائمة الجانبية
menu = st.sidebar.radio("القائمة:", ["تسجيل فحص", "السجل المالي", "تحميل البيانات"])

if menu == "تسجيل فحص":
    st.header("📝 إدخال بيانات المريض")
    with st.form("input_form"):
        name = st.text_input("اسم المريض")
        test = st.selectbox("الفحص", ["Glucose", "HbA1c", "Urea", "CBC"])
        res = st.number_input("النتيجة", format="%.2f")
        price = st.number_input("السعر الكلي", value=0)
        paid = st.number_input("المبلغ المدفوع", value=0)
        
        if st.form_submit_button("حفظ"):
            dt = datetime.now().strftime("%Y-%m-%d %H:%M")
            c.execute("INSERT INTO data (name, test, result, price, paid, date) VALUES (?,?,?,?,?,?)",
                      (name, test, res, price, paid, dt))
            conn.commit()
            st.success("تم الحفظ بنجاح")

elif menu == "السجل المالي":
    st.header("📋 سجل المرضى والحسابات")
    df = pd.read_sql("SELECT name as 'المريض', test as 'الفحص', result as 'النتيجة', price as 'السعر', paid as 'المدفوع', (price-paid) as 'المتبقي', date as 'التاريخ' FROM data", conn)
    if not df.empty:
        # عرض الجدول بشكل يسمح بالنسخ (Copy) كبديل للتحميل إذا فشل الزر
        st.write("يمكنك تحديد البيانات ونسخها مباشرة إلى Excel")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("لا توجد سجلات")

elif menu == "تحميل البيانات":
    st.header("📥 تصدير السجل")
    df_export = pd.read_sql("SELECT * FROM data", conn)
    
    if not df_export.empty:
        # الطريقة البديلة: تحويل البيانات لنص CSV وعرضها في مربع نصي ليتم نسخها
        csv = df_export.to_csv(index=False)
        st.text_area("إذا لم يعمل زر التحميل أدناه، قم بنسخ هذا النص ولصقه في ملف نصي بصيغة .csv", value=csv, height=200)
        
        # محاولة أخيرة لزر التحميل باستخدام Key مختلف
        st.download_button(
            label="📥 اضغط هنا للتحميل",
            data=csv.encode('utf-8-sig'),
            file_name='lab_data.csv',
            mime='text/csv',
            key='btn_download_v2'
        )
    else:
        st.warning("السجل فارغ.")
