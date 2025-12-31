import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# إعدادات واجهة المستخدم
st.set_page_config(page_title="Smart Lab", layout="wide")
st.markdown("""<style> .main { text-align: right; direction: rtl; } </style>""", unsafe_allow_html=True)

# قاعدة البيانات
conn = sqlite3.connect("lab_database.db", check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS patients 
             (id INTEGER PRIMARY KEY, name TEXT, test TEXT, result REAL, min_v REAL, max_v REAL, status TEXT, date TEXT)''')
conn.commit()

st.title("🧪 مختبر الذكاء الاصطناعي - إدارة النتائج")

# --- نموذج الإدخال ---
with st.container():
    st.subheader("📝 تسجيل فحص جديد")
    c1, c2, c3 = st.columns(3)
    with c1:
        name = st.text_input("اسم المريض بالكامل")
        test = st.text_input("اسم الفحص (مثل: CBC, Urea)")
    with c2:
        res = st.number_input("النتيجة", format="%.2f")
        min_v = st.number_input("الحد الأدنى الطبيعي", value=0.0)
    with c3:
        max_v = st.number_input("الحد الأعلى الطبيعي", value=100.0)
        
    if st.button("✅ حفظ النتيجة وتحليلها"):
        if name and test:
            # تحديد الحالة تلقائياً
            status = "طبيعي"
            if res > max_v: status = "مرتفع ⚠️"
            elif res < min_v: status = "منخفض ⚠️"
            
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            c.execute("INSERT INTO patients (name, test, result, min_v, max_v, status, date) VALUES (?,?,?,?,?,?,?)",
                      (name, test, res, min_v, max_v, status, now))
            conn.commit()
            st.balloons() # تأثير احتفالي عند النجاح
            st.success(f"تم حفظ فحص المريض {name} بنجاح")
            st.rerun()

st.divider()

# --- عرض البيانات والبحث ---
st.subheader("🔍 سجل الفحوصات والبحث")
search_query = st.text_input("ابحث عن مريض بالاسم...")

query = "SELECT name as 'اسم المريض', test as 'الفحص', result as 'النتيجة', status as 'الحالة', date as 'التاريخ' FROM patients"
if search_query:
    query += f" WHERE name LIKE '%{search_query}%'"

df = pd.read_sql(query, conn)

if not df.empty:
    # تنسيق الجدول وتلوين الحالات
    def color_status(val):
        color = 'red' if '⚠️' in str(val) else 'green'
        return f'color: {color}'

    st.dataframe(df.style.applymap(color_status, subset=['الحالة']), use_container_width=True)
    
    # ميزة تصدير البيانات لملف Excel
    csv = df.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 تحميل السجل كملف Excel (CSV)", data=csv, file_name="lab_results.csv", mime="text/csv")
else:
    st.info("لا توجد فحوصات مسجلة حتى الآن.")
