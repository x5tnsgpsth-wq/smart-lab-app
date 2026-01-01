import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime
import urllib.parse

# 1. إعدادات الهوية الفائقة (لجعل الـ APK يبدو احترافياً)
st.set_page_config(page_title="LabPro Smart System", page_icon="🔬", layout="wide")

# إخفاء عناصر المتصفح وتحسين الشكل
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp { background-color: #f8f9fa; direction: rtl; text-align: right; }
    .wa-btn { background-color: #25D366; color: white; padding: 10px; border-radius: 5px; text-decoration: none; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. نظام قاعدة البيانات المطور
DB_FILE = "advanced_lab_db.csv"

def save_data(df):
    df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["التاريخ", "المريض", "الفحص", "النتيجة", "الحالة", "المحلل", "الهاتف", "السعر", "الواصل"])

if 'df' not in st.session_state:
    st.session_state.df = load_data()

# المرجع الطبي للنتائج
NR = {"Glucose": [70, 126], "CBC": [12, 16], "HbA1c": [4, 5.6], "Urea": [15, 45]}

# 3. واجهة التطبيق الرئيسية
st.title("🔬 منظومة إدارة المختبر الذكية")

tabs = st.tabs(["📝 تسجيل مريض", "📊 لوحة التحكم والنتائج", "💰 التقارير المالية", "⚙️ الإعدادات"])

# --- التبويب 1: التسجيل المطور ---
with tabs[0]:
    with st.form("main_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            p_name = st.text_input("اسم المريض الثلاثي")
            p_test = st.selectbox("نوع الفحص المخبري", list(NR.keys()))
            p_res = st.number_input("النتيجة", format="%.2f")
        with c2:
            p_phone = st.text_input("رقم الهاتف (964xxxxxxxxx)")
            p_price = st.number_input("سعر الفحص (IQD)", value=15000, step=500)
            p_paid = st.number_input("المبلغ الواصل", value=15000, step=500)
        
        staff = st.text_input("👤 توقيع المحلل")
        
        if st.form_submit_button("إصدار النتيجة وحفظها"):
            if p_name and staff:
                # منطق تشخيص الحالة تلقائياً
                status = "طبيعي"
                if p_res < NR[p_test][0]: status = "منخفض"
                elif p_res > NR[p_test][1]: status = "مرتفع"
                
                new_entry = pd.DataFrame([[
                    datetime.now().strftime("%Y-%m-%d %H:%M"), p_name, p_test, p_res, status, staff, p_phone, p_price, p_paid
                ]], columns=st.session_state.df.columns)
                
                st.session_state.df = pd.concat([st.session_state.df, new_entry], ignore_index=True)
                save_data(st.session_state.df)
                st.success(f"✅ تم تسجيل حالة {p_name} بنجاح!")
            else:
                st.error("⚠️ يرجى ملء الحقول الأساسية (الاسم والمحلل)")

# --- التبويب 2: التحليل البياني والواتساب ---
with tabs[1]:
    if not st.session_state.df.empty:
        col_list, col_chart = st.columns([1, 1])
        
        with col_list:
            st.subheader("📋 السجلات الأخيرة")
            st.dataframe(st.session_state.df.tail(10), use_container_width=True)
            
            # اختيار مريض لإرسال واتساب أو رؤية تاريخه
            target_p = st.selectbox("اختر مريضاً لإرسال النتيجة:", st.session_state.df['المريض'].unique())
            p_row = st.session_state.df[st.session_state.df['المريض'] == target_p].iloc[-1]
            
            msg = f"مرحبا {p_row['المريض']}%0Aفحصك: {p_row['الفحص']}%0Aالنتيجة: {p_row['النتيجة']}%0Aالحالة: {p_row['الحالة']}"
            wa_link = f"https://wa.me/{p_row['الهاتف']}?text={msg}"
            st.markdown(f'<a href="{wa_link}" target="_blank" class="wa-btn">📲 إرسال إلى واتساب المريض</a>', unsafe_allow_html=True)

        with col_chart:
            st.subheader("📈 إحصائيات الحالات")
            fig = px.pie(st.session_state.df, names='الحالة', color='الحالة', 
                         color_discrete_map={'طبيعي':'green', 'مرتفع':'red', 'منخفض':'blue'})
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("لا توجد بيانات للعرض حالياً.")

# --- التبويب 3: الإدارة المالية ---
with tabs[2]:
    if not st.session_state.df.empty:
        total_income = st.session_state.df['الواصل'].sum()
        total_debts = (st.session_state.df['السعر'] - st.session_state.df['الواصل']).sum()
        
        m1, m2 = st.columns(2)
        m1.metric("إجمالي الإيرادات", f"{total_income:,} IQD")
        m2.metric("إجمالي الديون (باقي)", f"{total_debts:,} IQD", delta_color="inverse")
        
        fig_revenue = px.bar(st.session_state.df, x='التاريخ', y='الواصل', title="حركة الدخل اليومية")
        st.plotly_chart(fig_revenue, use_container_width=True)

# --- التبويب 4: الإعدادات ---
with tabs[3]:
    st.subheader("⚙️ إدارة النظام")
    if st.button("📥 تحميل قاعدة البيانات كملف Excel"):
        st.session_state.df.to_csv("backup.csv", index=False)
        st.write("تم تجهيز نسخة احتياطية باسم backup.csv في السيرفر.")
