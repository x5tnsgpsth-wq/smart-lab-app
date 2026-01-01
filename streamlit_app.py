import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import urllib.parse

# 1. إعداد الصفحة (يجب أن يظل في الأعلى)
st.set_page_config(page_title="نظام المختبر الاحترافي", layout="wide")

# تنسيق للعربية
st.markdown("""<style> * { direction: rtl; text-align: right; } .stMetric {background-color: #f8f9fa; padding: 10px; border-radius: 10px; border: 1px solid #ddd;} </style>""", unsafe_allow_html=True)

# 2. قاعدة البيانات
conn = sqlite3.connect("lab_v6.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS patients 
               (id INTEGER PRIMARY KEY, name TEXT, contact TEXT, test TEXT, result REAL, status TEXT, date TEXT)""")
conn.commit()

# 3. القائمة الجانبية (Sidebar) - بديلة للتبويبات لضمان الظهور
st.sidebar.title("🧪 لوحة التحكم")
choice = st.sidebar.radio("انتقل إلى:", ["📊 الشاشة الرئيسية", "📥 تسجيل فحص", "📋 السجل والإرسال"])

# --- الشاشة الرئيسية (الإحصائيات) ---
if choice == "📊 الشاشة الرئيسية":
    st.title("لوحة بيانات المختبر")
    df_stat = pd.read_sql("SELECT * FROM patients", conn)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("إجمالي الفحوصات", len(df_stat))
    with col2:
        # حساب حالات اليوم
        today = datetime.now().strftime("%Y-%m-%d")
        today_count = len(df_stat[df_stat['date'].str.contains(today)])
        st.metric("فحوصات اليوم", today_count)
    with col3:
        high_cases = len(df_stat[df_stat['status'].str.contains("⚠️")])
        st.metric("نتائج مرتفعة", high_cases, delta_color="inverse")

    st.divider()
    if not df_stat.empty:
        st.subheader("📈 توزيع الفحوصات")
        st.bar_chart(df_stat['test'].value_counts())

# --- تسجيل فحص جديد ---
elif choice == "📥 تسجيل فحص":
    st.title("إضافة فحص جديد")
    with st.form("entry_form"):
        name = st.text_input("اسم المريض")
        contact = st.text_input("الرقم أو المعرف (تليجرام/واتساب)")
        test = st.selectbox("نوع الفحص", ["Glucose", "HbA1c", "Urea", "Creatinine", "Vitamin D"])
        res = st.number_input("النتيجة", format="%.2f")
        
        if st.form_submit_button("حفظ"):
            if name and contact:
                status = "طبيعي" if res < 120 else "مرتفع ⚠️"
                dt = datetime.now().strftime("%Y-%m-%d %H:%M")
                cursor.execute("INSERT INTO patients (name, contact, test, result, status, date) VALUES (?,?,?,?,?,?)", 
                               (name, contact, test, res, status, dt))
                conn.commit()
                st.success("تم الحفظ بنجاح")
                st.balloons()

# --- السجل والإرسال ---
elif choice == "📋 السجل والإرسال":
    st.title("سجل النتائج والتواصل")
    df = pd.read_sql("SELECT * FROM patients ORDER BY id DESC", conn)
    if not df.empty:
        search = st.text_input("🔍 ابحث باسم المريض")
        filtered_df = df[df['name'].str.contains(search, na=False)]
        st.dataframe(filtered_df, use_container_width=True)
        
        st.divider()
        sel_p = st.selectbox("اختر المريض للإرسال:", filtered_df['name'].unique())
        p_info = filtered_df[filtered_df['name'] == sel_p].iloc[0]
        
        msg = f"مرحباً {p_info['name']}، نتيجتك لفحص {p_info['test']} هي {p_info['result']} ({p_info['status']})."
        msg_enc = urllib.parse.quote(msg)
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f'<a href="https://wa.me/{p_info["contact"]}?text={msg_enc}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366; color:white; padding:15px; border-radius:10px; text-align:center;">WhatsApp</div></a>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<a href="https://t.me/share/url?url={msg_enc}&text={p_info["contact"]}" target="_blank" style="text-decoration:none;"><div style="background-color:#0088cc; color:white; padding:15px; border-radius:10px; text-align:center;">Telegram</div></a>', unsafe_allow_html=True)
