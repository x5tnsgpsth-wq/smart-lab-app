import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime
import urllib.parse

# 1. إعدادات الهوية الفائقة (لجعل التطبيق يبدو احترافياً على الأندرويد)
st.set_page_config(page_title="LabPro Enterprise", page_icon="🔬", layout="wide")

# تحسين مظهر الواجهة بالـ CSS (لإخفاء عناصر المتصفح)
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp { background-color: #f8f9fa; direction: rtl; text-align: right; }
    .wa-btn { background-color: #25D366; color: white; padding: 12px 20px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #e9ecef; border-radius: 5px; padding: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. نظام قاعدة البيانات المطور (حفظ آلي)
DB_FILE = "advanced_lab_db.csv"

def save_data(df):
    df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["التاريخ", "المريض", "الفحص", "النتيجة", "الحالة", "المحلل", "الهاتف", "السعر", "الواصل"])

if 'df' not in st.session_state:
    st.session_state.df = load_data()

# المرجع الطبي (Normal Ranges)
NR = {"Glucose": [70, 126], "CBC": [12, 16], "HbA1c": [4, 5.6], "Urea": [15, 45]}

# 3. واجهة التطبيق الرئيسية
st.title("🔬 منظومة المختبر الذكية - الإصدار الاحترافي")

tabs = st.tabs(["📝 تسجيل مريض", "🔍 البحث والسجلات", "💰 التقارير المالية", "⚙️ الإدارة"])

# --- التبويب 1: التسجيل الذكي ---
with tabs[0]:
    with st.form("main_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            p_name = st.text_input("اسم المريض")
            p_test = st.selectbox("نوع الفحص", list(NR.keys()))
            p_res = st.number_input("النتيجة", format="%.2f")
        with c2:
            p_phone = st.text_input("رقم الهاتف (964xxxxxxxxx)")
            p_price = st.number_input("سعر الفحص (IQD)", value=15000)
            p_paid = st.number_input("المبلغ الواصل", value=15000)
        
        staff = st.text_input("👤 توقيع المحلل المسؤول")
        
        if st.form_submit_button("إصدار النتيجة وحفظ البيانات"):
            if p_name and staff:
                # منطق التشخيص التلقائي
                status = "طبيعي"
                if p_res < NR[p_test][0]: status = "منخفض"
                elif p_res > NR[p_test][1]: status = "مرتفع"
                
                new_entry = pd.DataFrame([[
                    datetime.now().strftime("%Y-%m-%d %H:%M"), p_name, p_test, p_res, status, staff, p_phone, p_price, p_paid
                ]], columns=st.session_state.df.columns)
                
                st.session_state.df = pd.concat([st.session_state.df, new_entry], ignore_index=True)
                save_data(st.session_state.df)
                st.success(f"✅ تم الحفظ بنجاح للمريض: {p_name}")
                st.balloons()
            else:
                st.error("⚠️ يرجى ملء الاسم واسم المحلل")

# --- التبويب 2: البحث المطور والواتساب ---
with tabs[1]:
    search = st.text_input("🔍 ابحث بالاسم أو برقم الهاتف:")
    if not st.session_state.df.empty:
        # تصفية البحث
        f_df = st.session_state.df[
            st.session_state.df['المريض'].str.contains(search, na=False) | 
            st.session_state.df['الهاتف'].astype(str).str.contains(search, na=False)
        ]
        
        st.dataframe(f_df.tail(10), use_container_width=True)
        
        if not f_df.empty:
            sel_p = st.selectbox("اختر مريضاً لإرسال النتيجة:", f_df['المريض'].unique())
            row = f_df[f_df['المريض'] == sel_p].iloc[-1]
            
            # رابط الواتساب المحسن
            msg = f"مرحباً {row['المريض']}%0Aفحص: {row['الفحص']}%0Aالنتيجة: {row['النتيجة']}%0Aالحالة: {row['الحالة']}"
            wa_link = f"https://wa.me/{row['الهاتف']}?text={msg}"
            st.markdown(f'<a href="{wa_link}" target="_blank" class="wa-btn">📲 إرسال عبر واتساب</a>', unsafe_allow_html=True)
            
            # مخطط بياني لمتابعة حالة المريض نفسه
            st.subheader(f"📈 تاريخ فحص {row['الفحص']} لـ {sel_p}")
            p_history = st.session_state.df[st.session_state.df['المريض'] == sel_p]
            fig_p = px.line(p_history, x='التاريخ', y='النتيجة', markers=True)
            st.plotly_chart(fig_p, use_container_width=True)

# --- التبويب 3: الإحصائيات المالية ---
with tabs[2]:
    if not st.session_state.df.empty:
        total_in = st.session_state.df['الواصل'].sum()
        total_debt = (st.session_state.df['السعر'] - st.session_state.df['الواصل']).sum()
        
        m1, m2 = st.columns(2)
        m1.metric("إجمالي الإيرادات (IQD)", f"{total_in:,}")
        m2.metric("إجمالي الديون (باقي)", f"{total_debt:,}")
        
        # مخطط توزيع الفحوصات
        fig_pie = px.pie(st.session_state.df, names='الفحص', title="نسبة طلب الفحوصات")
        st.plotly_chart(fig_pie, use_container_width=True)

# --- التبويب 4: الإدارة ---
with tabs[3]:
    pwd = st.text_input("رمز الإدارة", type="password")
    if pwd == "2026":
        st.download_button("📥 تحميل قاعدة البيانات (Excel)", 
                           st.session_state.df.to_csv(index=False).encode('utf-8-sig'), 
                           "lab_backup.csv", "text/csv")
        if st.button("🔴 تصفير البيانات نهائياً"):
            st.session_state.df = pd.DataFrame(columns=st.session_state.df.columns)
            save_data(st.session_state.df)
            st.rerun()
