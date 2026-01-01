import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime
import urllib.parse

# 1. إعدادات الهوية الفائقة (لتحسين شكل التطبيق على التابلت)
st.set_page_config(page_title="LabPro Smart System", page_icon="🔬", layout="wide")

# تصميم الواجهة لإخفاء عناصر المتصفح وجعلها تبدو كتطبيق أندرويد
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp { background-color: #f8f9fa; direction: rtl; text-align: right; }
    .wa-btn { background-color: #25D366; color: white; padding: 12px 20px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block; text-align: center; width: 100%; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { background-color: #ffffff; border-radius: 10px; padding: 10px 20px; border: 1px solid #ddd; }
    </style>
    """, unsafe_allow_html=True)

# 2. نظام إدارة البيانات (الحفظ التلقائي في ملف CSV)
DB_FILE = "advanced_lab_db.csv"

def save_data(df):
    df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["التاريخ", "المريض", "الفحص", "النتيجة", "الحالة", "المحلل", "الهاتف", "السعر", "الواصل"])

if 'df' not in st.session_state:
    st.session_state.df = load_data()

# المرجع الطبي للنتائج (Normal Ranges)
NR = {"Glucose": [70, 126], "CBC": [12, 16], "HbA1c": [4, 5.6], "Urea": [15, 45]}

# 3. واجهة التطبيق الرئيسية
st.title("🔬 منظومة إدارة المختبر الذكية")

tabs = st.tabs(["📝 تسجيل مريض", "🔍 البحث والمتابعة", "📊 التقارير المالية", "⚙️ الإدارة"])

# --- التبويب 1: إدخال البيانات الذكي ---
with tabs[0]:
    with st.form("main_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            p_name = st.text_input("اسم المريض الثلاثي")
            p_test = st.selectbox("نوع الفحص المخبري", list(NR.keys()))
            p_res = st.number_input("النتيجة المخبرية", format="%.2f")
        with c2:
            p_phone = st.text_input("رقم الهاتف (مثال: 964780...)")
            p_price = st.number_input("سعر الفحص (IQD)", value=15000, step=500)
            p_paid = st.number_input("المبلغ المدفوع (الواصل)", value=15000, step=500)
        
        staff = st.text_input("👤 اسم المحلل المسؤول")
        
        if st.form_submit_button("حفظ النتيجة وإصدار التقرير"):
            if p_name and staff:
                # منطق تشخيص الحالة آلياً
                status = "طبيعي"
                if p_res < NR[p_test][0]: status = "منخفض"
                elif p_res > NR[p_test][1]: status = "مرتفع"
                
                new_entry = pd.DataFrame([[
                    datetime.now().strftime("%Y-%m-%d %H:%M"), p_name, p_test, p_res, status, staff, p_phone, p_price, p_paid
                ]], columns=st.session_state.df.columns)
                
                st.session_state.df = pd.concat([st.session_state.df, new_entry], ignore_index=True)
                save_data(st.session_state.df)
                st.success(f"✅ تم حفظ بيانات المريض {p_name} بنجاح!")
                st.balloons()
            else:
                st.error("⚠️ يرجى تعبئة الحقول المطلوبة (الاسم والمحلل)")

# --- التبويب 2: محرك البحث والربط مع واتساب ---
with tabs[1]:
    search_query = st.text_input("🔍 ابحث عن مريض بالاسم أو رقم الهاتف:")
    if not st.session_state.df.empty:
        # تصفية البيانات بناءً على البحث
        f_df = st.session_state.df[
            st.session_state.df['المريض'].str.contains(search_query, na=False) | 
            st.session_state.df['الهاتف'].astype(str).str.contains(search_query, na=False)
        ]
        
        st.subheader("📋 السجلات الموجودة")
        st.dataframe(f_df.tail(15), use_container_width=True)
        
        if not f_df.empty:
            st.divider()
            sel_p = st.selectbox("اختر مريضاً لإرسال النتيجة إليه:", f_df['المريض'].unique())
            row = f_df[f_df['المريض'] == sel_p].iloc[-1]
            
            # زر واتساب الذكي
            msg = f"مرحباً {row['المريض']}%0Aفحصك لـ {row['الفحص']} جاهز.%0Aالنتيجة: {row['النتيجة']}%0Aالحالة: {row['الحالة']}"
            wa_link = f"https://wa.me/{row['الهاتف']}?text={msg}"
            st.markdown(f'<a href="{wa_link}" target="_blank" class="wa-btn">📲 إرسال النتيجة عبر WhatsApp</a>', unsafe_allow_html=True)
            
            # رسم بياني لتاريخ فحوصات هذا المريض
            st.subheader(f"📈 الرسم البياني لفحوصات {sel_p}")
            p_history = st.session_state.df[st.session_state.df['المريض'] == sel_p]
            fig_p = px.line(p_history, x='التاريخ', y='النتيجة', markers=True, title=f"تطور فحص {row['الفحص']}")
            st.plotly_chart(fig_p, use_container_width=True)

# --- التبويب 3: الإدارة المالية والإحصائيات ---
with tabs[2]:
    if not st.session_state.df.empty:
        total_income = st.session_state.df['الواصل'].sum()
        total_debt = (st.session_state.df['السعر'] - st.session_state.df['الواصل']).sum()
        
        col_m1, col_m2 = st.columns(2)
        col_m1.metric("إجمالي المبالغ المستلمة (IQD)", f"{total_income:,}")
        col_m2.metric("إجمالي الديون المتبقية", f"{total_debt:,}", delta_color="inverse")
        
        # مخطط دائري لتوزيع الحالات الطبية في المختبر
        st.subheader("📊 توزيع الحالات الطبية")
        fig_pie = px.pie(st.session_state.df, names='الحالة', color='الحالة',
                         color_discrete_map={'طبيعي':'#28a745', 'مرتفع':'#dc3545', 'منخفض':'#007bff'})
        st.plotly_chart(fig_pie, use_container_width=True)

# --- التبويب 4: الإعدادات والأمان ---
with tabs[3]:
    st.subheader("🔐 صلاحيات المسؤول")
    access_code = st.text_input("أدخل رمز الوصول للإدارة:", type="password")
    if access_code == "2026":
        st.success("تم تسجيل الدخول كمسؤول")
        st.download_button("📥 تحميل قاعدة البيانات بالكامل (Excel)", 
                           st.session_state.df.to_csv(index=False).encode('utf-8-sig'), 
                           "lab_data_backup.csv", "text/csv")
        
        if st.button("🔴 مسح كافة البيانات (حذف السجل)"):
            st.session_state.df = pd.DataFrame(columns=st.session_state.df.columns)
            save_data(st.session_state.df)
            st.rerun()
