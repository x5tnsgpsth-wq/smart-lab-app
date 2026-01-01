import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from PIL import Image
import os

# إعدادات الصفحة
st.set_page_config(page_title="مختبر برو - النسخة الآمنة", layout="wide")

# --- نظام تسجيل الدخول البسيط ---
def check_password():
    if "password_correct" not in st.session_state:
        st.title("🔒 تسجيل الدخول للمختبر")
        password = st.text_input("أدخل كلمة المرور الخاصة بالمختبر", type="password")
        if st.button("دخول"):
            if password == "lab2024": # يمكنك تغيير كلمة المرور هنا
                st.session_state.password_correct = True
                st.rerun()
            else:
                st.error("❌ كلمة المرور غير صحيحة")
        return False
    return True

if check_password():
    # تصميم الواجهة
    st.markdown("""<style> body { text-align: right; direction: rtl; } </style>""", unsafe_allow_html=True)

    # قاعدة البيانات (تحديث الجدول لإضافة حقل الصور)
    conn = sqlite3.connect("secure_lab.db", check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS records 
                 (id INTEGER PRIMARY KEY, name TEXT, test TEXT, result REAL, date TEXT, image_path TEXT)''')
    conn.commit()

    # القائمة الجانبية
    st.sidebar.title("🛡️ لوحة التحكم")
    page = st.sidebar.selectbox("اختر المهمة:", ["السجل العام", "إدخال نتائج جديدة", "الأرشفة الرقمية"])

    if page == "إدخال نتائج جديدة":
        st.header("📝 تسجيل فحص جديد")
        with st.form("lab_form"):
            p_name = st.text_input("اسم المريض")
            t_name = st.selectbox("نوع الفحص", ["CBC", "Vitamin D", "COVID-19", "Lipid Profile"])
            res = st.number_input("النتيجة الرقمية")
            
            # ميزة رفع صورة الفحص
            uploaded_file = st.file_uploader("ارفق صورة الفحص (اختياري)", type=['jpg', 'png', 'pdf'])
            
            submit = st.form_submit_button("حفظ البيانات")
            
            if submit and p_name:
                img_path = "none"
                if uploaded_file:
                    # حفظ الصورة في مجلد مؤقت
                    img_path = f"img_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
                    with open(img_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                
                now = datetime.now().strftime("%Y-%m-%d %H:%M")
                c.execute("INSERT INTO records (name, test, result, date, image_path) VALUES (?,?,?,?,?)",
                          (p_name, t_name, res, now, img_path))
                conn.commit()
                st.success(f"✅ تم الحفظ بنجاح للمريض: {p_name}")

    elif page == "السجل العام":
        st.header("🔍 سجل فحوصات المختبر")
        search = st.text_input("بحث باسم المريض")
        df = pd.read_sql(f"SELECT name, test, result, date FROM records WHERE name LIKE '%{search}%'", conn)
        st.dataframe(df, use_container_width=True)

    elif page == "الأرشفة الرقمية":
        st.header("📂 أرشيف الصور والوثائق")
        search_p = st.selectbox("اختر المريض لعرض وثائقه", pd.read_sql("SELECT DISTINCT name FROM records", conn))
        
        if search_p:
            res_data = pd.read_sql(f"SELECT * FROM records WHERE name = '{search_p}'", conn)
            for i, row in res_data.iterrows():
                st.write(f"📄 فحص: {row['test']} بتاريخ {row['date']}")
                if row['image_path'] != "none" and os.path.exists(row['image_path']):
                    st.image(row['image_path'], width=400)
                else:
                    st.info("لا توجد صورة مرفقة لهذا الفحص")

    # زر تسجيل الخروج
    if st.sidebar.button("تسجيل الخروج"):
        del st.session_state.password_correct
        st.rerun()

