import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# 1. إعدادات الهوية والجمالية مع السماح بالتمرير
st.set_page_config(page_title="Smart Lab System v30", page_icon="🔬", layout="wide")

# 2. إدارة البيانات والإعدادات
DB_FILE = "lab_pro_v30.csv"
SETTINGS_FILE = "settings.csv"

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            return pd.read_csv(SETTINGS_FILE)['lab_name'].iloc[0]
        except:
            return "مختبر التحليلات الافتراضي"
    return "مختبر التحليلات الافتراضي"

if 'lab_name' not in st.session_state:
    st.session_state.lab_name = load_settings()

if 'df' not in st.session_state:
    if os.path.exists(DB_FILE):
        st.session_state.df = pd.read_csv(DB_FILE)
    else:
        st.session_state.df = pd.DataFrame(columns=["التاريخ", "المريض", "الفحص", "النتيجة", "الحالة", "المحلل", "الهاتف", "ملاحظات"])

NR = {"Glucose": [70, 126], "CBC": [12, 16], "HbA1c": [4, 5.6], "Urea": [15, 45]}

# 3. تعديل CSS لحل مشكلة التجميد والتمرير (Scrolling Fix)
st.markdown(f"""
    <style>
    /* السماح بالتمرير العمودي ومنع تجميد الصفحة */
    .main .block-container {{
        overflow-y: auto !important;
        padding-bottom: 50px !important;
    }}
    
    /* تحسين شكل التقرير ليكون متجاوباً */
    .report-box {{
        border: 2px solid #333; 
        padding: 20px; 
        border-radius: 15px;
        background-color: white; 
        color: black; 
        direction: rtl;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }}
    
    .report-header {{ text-align: center; border-bottom: 3px double #333; padding-bottom: 10px; margin-bottom: 15px; }}
    
    /* ضبط اتجاه الصفحة بالكامل */
    .stApp {{ direction: rtl; text-align: right; }}
    
    /* تحسين أزرار التابلت */
    .stButton>button {{
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #007bff;
        color: white;
    }}
    </style>
    """, unsafe_allow_html=True)

# العنوان الرئيسي
st.title(f"🔬 {st.session_state.lab_name}")

# استخدام الحاويات لضمان عدم تداخل العناصر
tabs = st.tabs(["📝 إدخال وفحص", "📄 إصدار تقرير", "📊 إحصائيات", "⚙️ إعدادات المختبر"])

# --- التبويب 4: الإعدادات ---
with tabs[3]:
    st.subheader("⚙️ إعدادات هوية المختبر")
    new_name_input = st.text_input("اكتب اسم مختبرك هنا:", value=st.session_state.lab_name)
    if st.button("حفظ وتحديث اسم المختبر"):
        pd.DataFrame({'lab_name': [new_name_input]}).to_csv(SETTINGS_FILE, index=False)
        st.session_state.lab_name = new_name_input
        st.success("✅ تم تحديث الاسم!")
        st.rerun()

# --- التبويب 1: إدخال البيانات ---
with tabs[0]:
    with st.form("entry_form"):
        c1, c2 = st.columns(2)
        with c1:
            p_phone = st.text_input("رقم هاتف المريض")
            existing_p = st.session_state.df[st.session_state.df['الهاتف'] == p_phone]
            def_name = existing_p['المريض'].iloc[-1] if not existing_p.empty else ""
            p_name = st.text_input("اسم المريض", value=def_name)
            p_test = st.selectbox("نوع الفحص", list(NR.keys()))
        with c2:
            p_res = st.number_input("النتيجة", format="%.2f")
            p_note = st.text_area("ملاحظات إضافية")
            p_staff = st.text_input("اسم المحلل")

        if st.form_submit_button("حفظ ومعالجة البيانات"):
            status = "طبيعي"
            if p_res < NR[p_test][0]: status = "منخفض"
            elif p_res > NR[p_test][1]: status = "مرتفع"
            new_data = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), p_name, p_test, p_res, status, p_staff, p_phone, p_note]], columns=st.session_state.df.columns)
            st.session_state.df = pd.concat([st.session_state.df, new_data], ignore_index=True)
            st.session_state.df.to_csv(DB_FILE, index=False)
            st.success("✅ تم الحفظ بنجاح")

# --- التبويب 2: إصدار التقرير ---
with tabs[1]:
    if not st.session_state.df.empty:
        target = st.selectbox("اختر المريض:", st.session_state.df['المريض'].unique())
        data = st.session_state.df[st.session_state.df['المريض'] == target].iloc[-1]
        
        st.markdown(f"""
        <div class="report-box">
            <div class="report-header">
                <h2 style="margin:0;">{st.session_state.lab_name}</h2>
                <p>تقرير فحص مخبري</p>
            </div>
            <table style="width:100%; text-align:right;">
                <tr><td><b>المريض:</b></td><td>{data['المريض']}</td></tr>
                <tr><td><b>الفحص:</b></td><td>{data['الفحص']}</td></tr>
                <tr><td><b>النتيجة:</b></td><td style="color:red; font-size:20px;">{data['النتيجة']}</td></tr>
                <tr><td><b>النطاق:</b></td><td>{NR[data['الفحص']][0]} - {NR[data['الفحص']][1]}</td></tr>
            </table>
            <hr>
            <p>توقيع المحلل: {data['المحلل']}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("لا توجد بيانات حالياً.")

# --- التبويب 3: الإحصائيات ---
with tabs[2]:
    if not st.session_state.df.empty:
        fig = px.pie(st.session_state.df, names='الحالة', title="توزيع النتائج")
        st.plotly_chart(fig, use_container_width=True)
