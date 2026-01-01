import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import urllib.parse

# إعداد الصفحة
st.set_page_config(page_title="المختبر الذكي Pro", layout="wide")
st.markdown("""<style> * { direction: rtl; text-align: right; } </style>""", unsafe_allow_html=True)

# قاعدة البيانات (تحديث الجداول لإضافة الحسابات)
conn = sqlite3.connect("lab_finance.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS patients 
               (id INTEGER PRIMARY KEY, name TEXT, contact TEXT, test TEXT, result REAL, 
               total_price REAL, paid REAL, status TEXT, date TEXT)""")
conn.commit()

# القائمة الجانبية
st.sidebar.title("🧪 إدارة المختبر")
choice = st.sidebar.radio("انتقل إلى:", ["📊 الإحصائيات", "📥 تسجيل فحص ودفع", "📋 السجل والديون", "⚙️ الإدارة"])

# --- 1. الإحصائيات ---
if choice == "📊 الإحصائيات":
    st.title("الوضع المالي والعام")
    df = pd.read_sql("SELECT * FROM patients", conn)
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("إجمالي الفحوصات", len(df))
        with c2: st.metric("إجمالي الإيرادات", f"{df['paid'].sum():,.0f} د.ع")
        with c3: st.metric("الديون المتبقية", f"{(df['total_price'] - df['paid']).sum():,.0f} د.ع")
        st.bar_chart(df['test'].value_counts())

# --- 2. تسجيل فحص ودفع ---
elif choice == "📥 تسجيل فحص ودفع":
    st.title("إدخال فحص وحسابات")
    with st.form("lab_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("اسم المريض")
            contact = st.text_input("رقم التواصل")
            test = st.selectbox("نوع الفحص", ["Glucose", "HbA1c", "Urea", "CBC"])
        with col2:
            res = st.number_input("النتيجة", format="%.2f")
            price = st.number_input("سعر الفحص الكلي", step=250)
            paid = st.number_input("المبلغ المدفوع حالياً", step=250)
        
        if st.form_submit_button("حفظ البيانات"):
            if name:
                status = "طبيعي" if res < 120 else "مرتفع ⚠️"
                dt = datetime.now().strftime("%Y-%m-%d %H:%M")
                cursor.execute("INSERT INTO patients (name, contact, test, result, total_price, paid, status, date) VALUES (?,?,?,?,?,?,?,?)", 
                               (name, contact, test, res, price, paid, status, dt))
                conn.commit()
                st.success(f"تم الحفظ! المتبقي على المريض: {price - paid} د.ع")

# --- 3. السجل والديون ---
elif choice == "📋 السجل والديون":
    st.title("سجل المرضى")
    df = pd.read_sql("SELECT * FROM patients ORDER BY id DESC", conn)
    if not df.empty:
        # إضافة عمود للمتبقي (Debt)
        df['المتبقي'] = df['total_price'] - df['paid']
        st.dataframe(df[['name', 'test', 'result', 'total_price', 'paid', 'المتبقي', 'date']], use_container_width=True)

# --- 4. الإدارة والتحميل ---
elif choice == "⚙️ الإدارة":
    st.title("تصدير وإدارة البيانات")
    df_exp = pd.read_sql("SELECT * FROM patients", conn)
    
    if not df_exp.empty:
        # حل مشكلة الزر: تحويل البيانات إلى CSV مع ترميز UTF-8-SIG لدعم العربية في إكسل
        csv_data = df_exp.to_csv(index=False).encode('utf-8-sig')
        
        st.download_button(
            label="📥 اضغط هنا لتحميل سجل الإكسل",
            data=csv_data,
            file_name="lab_report.csv",
            mime="text/csv",
            key='download-csv' # إضافة مفتاح فريد للزر
        )
