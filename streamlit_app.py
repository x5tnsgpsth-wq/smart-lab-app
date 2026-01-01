import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import urllib.parse

# إعداد الصفحة
st.set_page_config(page_title="المختبر الذكي Pro", layout="wide")

# تنسيق الواجهة
st.markdown("""<style> * { direction: rtl; text-align: right; } </style>""", unsafe_allow_html=True)

# قاعدة البيانات
conn = sqlite3.connect("lab_final_v7.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS patients 
               (id INTEGER PRIMARY KEY, name TEXT, contact TEXT, test TEXT, result REAL, status TEXT, date TEXT)""")
conn.commit()

# القائمة الجانبية
st.sidebar.title("🧪 التحكم بالمختبر")
choice = st.sidebar.radio("انتقل إلى:", ["📊 لوحة الإحصائيات", "📥 تسجيل فحص", "📋 السجل والتواصل", "⚙️ إدارة البيانات"])

# --- الشاشة الرئيسية ---
if choice == "📊 لوحة الإحصائيات":
    st.title("لوحة بيانات المختبر")
    df_stat = pd.read_sql("SELECT * FROM patients", conn)
    col1, col2 = st.columns(2)
    with col1:
        st.metric("إجمالي الفحوصات المسجلة", len(df_stat))
    with col2:
        high_risk = len(df_stat[df_stat['status'].str.contains("⚠️")])
        st.metric("الحالات المرتفعة", high_risk)
    
    if not df_stat.empty:
        st.subheader("توزيع الفحوصات حسب النوع")
        st.bar_chart(df_stat['test'].value_counts())

# --- تسجيل فحص جديد ---
elif choice == "📥 تسجيل فحص":
    st.title("إضافة فحص جديد")
    with st.form("entry_form"):
        name = st.text_input("اسم المريض")
        contact = st.text_input("رقم الهاتف أو المعرف")
        test = st.selectbox("نوع الفحص", ["Glucose", "HbA1c", "Urea", "Creatinine", "TSH", "Lipid Profile"])
        res = st.number_input("النتيجة المخبرية", format="%.2f")
        
        if st.form_submit_button("حفظ"):
            if name and contact:
                status = "طبيعي" if res < 120 else "مرتفع ⚠️"
                dt = datetime.now().strftime("%Y-%m-%d %H:%M")
                cursor.execute("INSERT INTO patients (name, contact, test, result, status, date) VALUES (?,?,?,?,?,?)", 
                               (name, contact, test, res, status, dt))
                conn.commit()
                st.success(f"تم تسجيل المريض {name}")
                st.balloons()

# --- السجل والتواصل ---
elif choice == "📋 السجل والتواصل":
    st.title("البحث والتواصل")
    df = pd.read_sql("SELECT * FROM patients ORDER BY id DESC", conn)
    if not df.empty:
        search = st.text_input("🔍 ابحث باسم المريض")
        filtered_df = df[df['name'].str.contains(search, na=False)]
        st.dataframe(filtered_df, use_container_width=True)
        
        st.divider()
        sel_p = st.selectbox("اختر المريض للإرسال:", filtered_df['name'].unique())
        p_info = filtered_df[filtered_df['name'] == sel_p].iloc[0]
        msg = f"مرحباً {p_info['name']}، نتيجتك لفحص {p_info['test']} هي {p_info['result']}."
        msg_enc = urllib.parse.quote(msg)
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f'<a href="https://wa.me/{p_info["contact"]}?text={msg_enc}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366; color:white; padding:15px; border-radius:10px; text-align:center;">إرسال WhatsApp</div></a>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<a href="https://t.me/share/url?url={msg_enc}&text={p_info["contact"]}" target="_blank" style="text-decoration:none;"><div style="background-color:#0088cc; color:white; padding:15px; border-radius:10px; text-align:center;">إرسال Telegram</div></a>', unsafe_allow_html=True)

# --- إدارة البيانات (الميزة الجديدة) ---
elif choice == "⚙️ إدارة البيانات":
    st.title("إدارة قاعدة البيانات")
    df_export = pd.read_sql("SELECT * FROM patients", conn)
    
    if not df_export.empty:
        st.subheader("💾 النسخ الاحتياطي")
        # تحويل البيانات لملف Excel (CSV)
        csv = df_export.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 تحميل سجل المختبر بالكامل (Excel)",
            data=csv,
            file_name=f'lab_report_{datetime.now().strftime("%Y-%m-%d")}.csv',
            mime='text/csv',
        )
        
        st.divider()
        st.subheader("🗑️ تنظيف السجل")
        if st.button("حذف كافة السجلات (تحذير!)"):
            cursor.execute("DELETE FROM patients")
            conn.commit()
            st.warning("تم مسح السجل بالكامل!")
            st.rerun()
    else:
        st.info("لا توجد بيانات حالياً لتصديرها.")
