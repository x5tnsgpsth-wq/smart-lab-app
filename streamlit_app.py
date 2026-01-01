import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# 1. إعدادات الهوية والجمالية
st.set_page_config(page_title="Smart Lab System v29", page_icon="🔬", layout="wide")

# 2. إدارة البيانات والإعدادات
DB_FILE = "lab_pro_v29.csv"
SETTINGS_FILE = "settings.csv"

# وظيفة لتحميل الإعدادات وضمان تحديثها
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        return pd.read_csv(SETTINGS_FILE)['lab_name'].iloc[0]
    return "مختبر التحليلات الافتراضي"

# تخزين اسم المختبر في الـ session_state لضمان التحديث الفوري
if 'lab_name' not in st.session_state:
    st.session_state.lab_name = load_settings()

if 'df' not in st.session_state:
    if os.path.exists(DB_FILE):
        st.session_state.df = pd.read_csv(DB_FILE)
    else:
        st.session_state.df = pd.DataFrame(columns=["التاريخ", "المريض", "الفحص", "النتيجة", "الحالة", "المحلل", "الهاتف", "ملاحظات"])

# مرجع النطاقات الطبيعية
NR = {"Glucose": [70, 126], "CBC": [12, 16], "HbA1c": [4, 5.6], "Urea": [15, 45]}

# تصميم CSS
st.markdown(f"""
    <style>
    .report-box {{
        border: 2px solid #333; padding: 25px; border-radius: 15px;
        background-color: white; color: black; direction: rtl;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.1);
    }}
    .report-header {{ text-align: center; border-bottom: 3px double #333; padding-bottom: 15px; margin-bottom: 20px; }}
    .stApp {{ direction: rtl; text-align: right; }}
    </style>
    """, unsafe_allow_html=True)

# 3. واجهة التطبيق - العنوان يستخدم الاسم المخزن في الـ session
st.title(f"🔬 {st.session_state.lab_name}")

tabs = st.tabs(["📝 إدخال وفحص", "📄 إصدار تقرير", "📊 إحصائيات", "⚙️ إعدادات المختبر"])

# --- التبويب 4: إعدادات المختبر (نبدأ به للتأكد من التغيير) ---
with tabs[3]:
    st.subheader("⚙️ إعدادات هوية المختبر")
    # نستخدم text_input ونحدث الـ session_state مباشرة عند الحفظ
    new_name_input = st.text_input("اكتب اسم مختبرك هنا:", value=st.session_state.lab_name)
    if st.button("حفظ وتحديث اسم المختبر الآن"):
        # حفظ في ملف للدوام
        pd.DataFrame({'lab_name': [new_name_input]}).to_csv(SETTINGS_FILE, index=False)
        # تحديث الذاكرة فوراً
        st.session_state.lab_name = new_name_input
        st.success("✅ تم تحديث الاسم بنجاح في النظام والتقارير!")
        st.rerun()

# --- التبويب 1: إدخال البيانات ---
with tabs[0]:
    with st.form("entry_form"):
        c1, c2 = st.columns(2)
        with c1:
            p_phone = st.text_input("رقم هاتف المريض")
            existing_p = st.session_state.df[st.session_state.df['الهاتف'] == p_phone]
            default_name = existing_p['المريض'].iloc[-1] if not existing_p.empty else ""
            p_name = st.text_input("اسم المريض", value=default_name)
            p_test = st.selectbox("نوع الفحص", list(NR.keys()))
        with c2:
            p_res = st.number_input("النتيجة", format="%.2f")
            p_note = st.text_area("ملاحظات إضافية")
            p_staff = st.text_input("اسم المحلل")

        if st.form_submit_button("حفظ ومعالجة"):
            status = "طبيعي"
            if p_res < NR[p_test][0]: status = "منخفض"
            elif p_res > NR[p_test][1]: status = "مرتفع"
            new_data = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), p_name, p_test, p_res, status, p_staff, p_phone, p_note]], columns=st.session_state.df.columns)
            st.session_state.df = pd.concat([st.session_state.df, new_data], ignore_index=True)
            st.session_state.df.to_csv(DB_FILE, index=False)
            st.success("✅ تم حفظ البيانات")

# --- التبويب 2: إصدار التقرير الرسمي ---
with tabs[1]:
    if not st.session_state.df.empty:
        target_name = st.selectbox("اختر المريض:", st.session_state.df['المريض'].unique())
        report_data = st.session_state.df[st.session_state.df['المريض'] == target_name].iloc[-1]
        
        st.markdown(f"""
        <div class="report-box">
            <div class="report-header">
                <h1 style="margin:0;">{st.session_state.lab_name}</h1>
                <p>تقرير نتائج الفحوصات المختبرية</p>
            </div>
            <table style="width:100%; text-align:right;">
                <tr style="background-color:#f2f2f2;"><td><b>المريض:</b></td><td>{report_data['المريض']}</td></tr>
                <tr><td><b>الفحص:</b></td><td>{report_data['الفحص']}</td></tr>
                <tr style="background-color:#f2f2f2;"><td><b>النتيجة:</b></td><td style="font-size:22px; color:red;">{report_data['النتيجة']}</td></tr>
                <tr><td><b>النطاق الطبيعي:</b></td><td>{NR[report_data['الفحص']][0]} - {NR[report_data['الفحص']][1]}</td></tr>
            </table>
            <div style="margin-top:30px; border-top:1px solid #eee;">
                <span>توقيع المحلل: {report_data['المحلل']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# --- التبويب 3: الإحصائيات ---
with tabs[2]:
    if not st.session_state.df.empty:
        fig = px.pie(st.session_state.df, names='الحالة', title="توزيع النتائج")
        st.plotly_chart(fig)
