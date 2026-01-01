import streamlit as st
import pandas as pd
import sqlite3

# إعدادات إجبارية للعرض
st.set_page_config(page_title="Test")

# إنشاء قاعدة بيانات بسيطة جداً
conn = sqlite3.connect("test.db")
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS data (name TEXT)")
conn.commit()

st.header("تجرية الاتصال")

# نموذج إدخال مبسط جداً
name_input = st.text_input("اكتب أي اسم هنا للتجربة")
if st.button("حفظ الاسم"):
    c.execute("INSERT INTO data (name) VALUES (?)", (name_input,))
    conn.commit()
    st.write(f"تم حفظ: {name_input}")

st.write("---")

# عرض البيانات بطريقة بدائية جداً
st.subheader("البيانات المحفوظة:")
df = pd.read_sql("SELECT * FROM data", conn)

if not df.empty:
    st.write(df) # عرض كجدول نصي بسيط
    
    # تحويل البيانات لنص مباشر
    csv_text = df.to_csv(index=False)
    st.text_area("انسخ البيانات من هنا إذا اختفى الزر:", value=csv_text)
    
    # محاولة إظهار الزر بمفتاح عشوائي جديد
    st.download_button("تحميل Excel", csv_text, "file.csv", "text/csv", key="unique_btn_999")
else:
    st.write("لا توجد بيانات بعد.")
