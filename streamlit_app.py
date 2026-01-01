import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import urllib.parse

# إعداد الصفحة وتنسيقها
st.set_page_config(page_title="المختبر الذكي Pro", layout="wide")
st.markdown("""<style> * { direction: rtl; text-align: right; } .stTabs [data-baseweb="tab"] { font-size: 18px; font-weight: bold; } </style>""", unsafe_allow_html=True)

# قاعدة البيانات
conn = sqlite3.connect("lab_final_v5.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS patients 
               (id INTEGER PRIMARY KEY, name TEXT, contact TEXT, test TEXT, result REAL, status TEXT, date TEXT)""")
conn.commit()

# واجهة التطبيق باستخدام التبويبات (Tabs) لتنظيم الشاشة
tab1, tab2, tab3 = st.tabs(["➕ تسجيل فحص", "📋 السجل والإرسال", "📈 تحليل مسار المريض"])

with tab1:
    st.header("إدخال فحص جديد")
    with st.form("entry_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("اسم المريض")
            contact = st.text_input("رقم الهاتف أو المعرّف")
        with col2:
            test = st.selectbox("نوع الفحص", ["Glucose", "HbA1c", "Urea", "Creatinine", "Cholesterol"])
            res = st.number_input("النتيجة المخبرية", format="%.2f")
        
        if st.form_submit_button("حفظ وإضافة للسجل"):
            if name and contact:
                status = "طبيعي" if res < 120 else "مرتفع ⚠️"
                dt = datetime.now().strftime("%Y-%m-%d %H:%M")
                cursor.execute("INSERT INTO patients (name, contact, test, result, status, date) VALUES (?,?,?,?,?,?)", 
                               (name, contact, test, res, status, dt))
                conn.commit()
                st.success("تم الحفظ!")

with tab2:
    st.header("سجل النتائج والتواصل")
    df = pd.read_sql("SELECT * FROM patients ORDER BY id DESC", conn)
    if not df.empty:
        # فلتر سريع للبحث
        search_q = st.text_input("🔍 ابحث باسم المريض في السجل")
        filtered_df = df[df['name'].str.contains(search_q, na=False)]
        st.dataframe(filtered_df, use_container_width=True)
        
        st.divider()
        # قسم الإرسال
        p_to_send = st.selectbox("اختر المريض للإرسال:", filtered_df['name'].unique())
        p_info = filtered_df[filtered_df['name'] == p_to_send].iloc[0]
        
        msg = f"النتائج لـ {p_info['name']}: {p_info['test']} = {p_info['result']} ({p_info['status']})"
        msg_enc = urllib.parse.quote(msg)
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f'<a href="https://wa.me/{p_info["contact"]}?text={msg_enc}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366; color:white; padding:10px; border-radius:10px; text-align:center;">WhatsApp</div></a>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<a href="https://t.me/share/url?url={msg_enc}&text={p_info["contact"]}" target="_blank" style="text-decoration:none;"><div style="background-color:#0088cc; color:white; padding:10px; border-radius:10px; text-align:center;">Telegram</div></a>', unsafe_allow_html=True)

with tab3:
    st.header("📈 مراقبة حالة مريض محدد")
    all_names = pd.read_sql("SELECT DISTINCT name FROM patients", conn)
    selected_p = st.selectbox("اختر المريض لمشاهدة تاريخه الصحي:", all_names['name'].unique())
    
    if selected_p:
        p_history = pd.read_sql(f"SELECT test, result, date FROM patients WHERE name = '{selected_p}'", conn)
        st.write(f"تاريخ الفحوصات لـ: {selected_p}")
        
        # رسم بياني إذا كان المريض له أكثر من فحص
        if len(p_history) > 1:
            st.line_chart(data=p_history, x='date', y='result')
        else:
            st.info("يحتاج المريض لأكثر من فحص واحد ليظهر الرسم البياني لتطور حالته.")
        st.table(p_history)
