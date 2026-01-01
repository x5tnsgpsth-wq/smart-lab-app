import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# 1. إعدادات الصفحة - تحسين الأداء
st.set_page_config(page_title="Smart Lab System v31", page_icon="🔬", layout="wide")

# 2. إدارة البيانات
DB_FILE = "lab_pro_v31.csv"
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

# 3. تعديلات CSS احترافية للسلاسة (Smooth Scrolling & Performance)
st.markdown(f"""
    <style>
    /* جعل التمرير ناعماً وسلساً */
    html {{
        scroll-behavior: smooth;
    }}
    
    /* منع تعليق الصفحة في أجهزة اللمس */
    .main {{
        overflow: auto;
        -webkit-overflow-scrolling: touch;
    }}

    /* تحسين وعاء العناصر ليكون مرناً */
    .block-container {{
        padding-top: 2rem;
        padding-bottom: 10rem;
    }}

    /* تصميم التقرير ليكون خفيفاً على المعالج */
    .report-box {{
        border: 1px solid #ddd;
        padding: 15px;
        border-radius: 12px;
        background-color: #ffffff;
        color: #000;
        direction: rtl;
        margin-bottom: 20px;
    }}

    .stApp {{ direction: rtl; text-align: right; }}
    
    /* تكبير الأزرار لتسهيل اللمس في التابلت */
    button {{
        min-height: 45px;
    }}
    </style>
    """, unsafe_allow_html=True)

# العنوان الرئيسي في حاوية مستقلة
with st.container():
    st.title(f"🔬 {st.session_state.lab_name}")

# استخدام التبويبات
tabs = st.tabs(["📝 إدخال وفحص", "📄 إصدار تقرير", "📊 إحصائيات", "⚙️ إعدادات"])

# --- التبويب 4: الإعدادات ---
with tabs[3]:
    with st.container():
        st.subheader("⚙️ إعدادات الهوية")
        new_name = st.text_input("اسم المختبر:", value=st.session_state.lab_name)
        if st.button("حفظ التغييرات"):
            pd.DataFrame({'lab_name': [new_name]}).to_csv(SETTINGS_FILE, index=False)
            st.session_state.lab_name = new_name
            st.success("تم التحديث!")
            st.rerun()

# --- التبويب 1: إدخال البيانات ---
with tabs[0]:
    with st.form("entry_form", clear_on_submit=False):
        c1, c2 = st.columns(2)
        with c1:
            p_phone = st.text_input("رقم الهاتف")
            existing = st.session_state.df[st.session_state.df['الهاتف'] == p_phone]
            def_name = existing['المريض'].iloc[-1] if not existing.empty else ""
            p_name = st.text_input("اسم المريض", value=def_name)
        with c2:
            p_test = st.selectbox("الفحص", list(NR.keys()))
            p_res = st.number_input("النتيجة", format="%.2f")
        
        p_note = st.text_input("ملاحظات")
        p_staff = st.text_input("المحلل")

        if st.form_submit_button("حفظ البيانات"):
            status = "طبيعي"
            if p_res < NR[p_test][0]: status = "منخفض"
            elif p_res > NR[p_test][1]: status = "مرتفع"
            
            new_row = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), p_name, p_test, p_res, status, p_staff, p_phone, p_note]], columns=st.session_state.df.columns)
            st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
            st.session_state.df.to_csv(DB_FILE, index=False)
            st.toast("✅ تم الحفظ بنجاح!")

# --- التبويب 2: التقرير ---
with tabs[1]:
    if not st.session_state.df.empty:
        target = st.selectbox("اختيار المريض:", st.session_state.df['المريض'].unique())
        data = st.session_state.df[st.session_state.df['المريض'] == target].iloc[-1]
        
        st.markdown(f"""
        <div class="report-box">
            <h3 style="text-align:center;">{st.session_state.lab_name}</h3>
            <hr>
            <p><b>المريض:</b> {data['المريض']}</p>
            <p><b>الفحص:</b> {data['الفحص']}</p>
            <p style="font-size:1.2rem; color:red;"><b>النتيجة:</b> {data['النتيجة']}</p>
            <p><b>الحالة:</b> {data['الحالة']}</p>
            <p><b>المحلل:</b> {data['المحلل']}</p>
        </div>
        """, unsafe_allow_html=True)

# --- التبويب 3: الإحصائيات ---
with tabs[2]:
    if not st.session_state.df.empty:
        # تقليل تفاصيل الرسم البياني لزيادة السلاسة
        fig = px.pie(st.session_state.df, names='الحالة', hole=0.4)
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)
