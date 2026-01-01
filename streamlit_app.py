import streamlit as st
import sqlite3
import pandas as pd

# 1. إعدادات أساسية جداً
st.set_page_config(page_title="المختبر")

# 2. إنشاء قاعدة البيانات بشكل مبسط
db = sqlite3.connect("simple_lab.db")
sql = db.cursor()
sql.execute("CREATE TABLE IF NOT EXISTS lab (id INTEGER PRIMARY KEY, name TEXT, test TEXT, result TEXT)")
db.commit()

# 3. واجهة بسيطة جداً بدون أي تعقيدات CSS
st.title("نظام المختبر")

# زر لإضافة مريض للتجربة فقط
with st.form(key="form1"):
    p_name = st.text_input("اسم المريض")
    p_test = st.text_input("نوع الفحص")
    p_res = st.text_input("النتيجة")
    if st.form_submit_button("حفظ"):
        sql.execute("INSERT INTO lab (name, test, result) VALUES (?,?,?)", (p_name, p_test, p_res))
        db.commit()
        st.success("تم!")

st.write("---")

# 4. عرض البيانات بطريقة بدائية ومضمونة
st.subheader("سجل البيانات")
data = pd.read_sql("SELECT * FROM lab", db)
st.table(data) # استخدمنا st.table بدلاً من dataframe لأنها أكثر استقراراً

# 5. زر التحميل بطريقة الرابط المباشر
if not data.empty:
    csv = data.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="تحميل الملف (Excel)",
        data=csv,
        file_name="lab.csv",
        mime="text/csv",
        key="simple_download_btn"
    )
