import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# 1. إعدادات الهوية والجمالية
st.set_page_config(page_title="Smart Lab System v27", page_icon="🔬", layout="wide")

# تصميم CSS لجعل النتيجة تبدو كأنها ورقة رسمية مطبوعة
st.markdown("""
    <style>
    .report-box {
        border: 2px solid #333;
        padding: 20px;
        border-radius: 10px;
        background-color: white;
        color: black;
        direction: rtl;
        font-family: 'Arial';
    }
    .report-header { text-align: center; border-bottom: 2px solid #eee; padding-bottom: 10px; }
    .status-badge { padding: 5px 10px; border-radius: 5px; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. إدارة البيانات
DB_FILE = "lab_pro_v27.csv"
if 'df' not in st.session_state:
    if os.path.exists(DB_FILE):
        st.session_state.df = pd.read_csv(DB_FILE)
    else:
        st.session_state.df = pd.DataFrame(columns=["التاريخ", "المريض", "الفحص", "النتيجة", "الحالة", "المحلل", "الهاتف", "ملاحظات"])

# مرجع النطاقات الطبيعية
NR = {"Glucose": [70, 126], "CBC": [12, 16], "HbA1c": [4, 5.6], "Urea": [15, 45]}

# 3. واجهة التطبيق
st.title("🔬 منظومة المختبر الذكي - الإصدار v27")

tabs = st.tabs(["📝 إدخال وفحص", "📄 إصدار تقرير", "📊 إحصائيات المختبر"])

# --- التبويب 1: إدخال البيانات الذكي ---
with tabs[0]:
    with st.form("entry_form"):
        c1, c2 = st.columns(2)
        with c1:
            p_phone = st.text_input("رقم هاتف المريض")
            # ميزة التعبئة التلقائية إذا كان المريض مسجلاً سابقاً
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
            st.success("✅ تم الحفظ بنجاح")

# --- التبويب 2: إصدار التقرير الرسمي ---
with tabs[1]:
    st.subheader("📄 عرض وطباعة النتيجة")
    if not st.session_state.df.empty:
        target_name = st.selectbox("اختر المريض لعرض تقريره:", st.session_state.df['المريض'].unique())
        report_data = st.session_state.df[st.session_state.df['المريض'] == target_name].iloc[-1]
        
        # تصميم التقرير
        st.markdown(f"""
        <div class="report-box">
            <div class="report-header">
                <h2>مختبر التحليلات المرضية الذكي</h2>
                <p>تاريخ الفحص: {report_data['التاريخ']}</p>
            </div>
            <table style="width:100%; text-align:right; margin-top:20px;">
                <tr><td><b>اسم المريض:</b></td><td>{report_data['المريض']}</td></tr>
                <tr><td><b>نوع الفحص:</b></td><td>{report_data['الفحص']}</td></tr>
                <tr><td><b>النتيجة:</b></td><td><span style="font-size:20px; color:blue;">{report_data['النتيجة']}</span></td></tr>
                <tr><td><b>النطاق الطبيعي:</b></td><td>{NR[report_data['الفحص']][0]} - {NR[report_data['الفحص']][1]}</td></tr>
                <tr><td><b>الحالة:</b></td><td>{report_data['الحالة']}</td></tr>
            </table>
            <div style="margin-top:20px; border-top:1px solid #eee; padding-top:10px;">
                <b>ملاحظات الطبيب:</b> {report_data['ملاحظات']}
            </div>
            <div style="margin-top:30px; text-align:left;">
                <p>توقيع المحلل: {report_data['المحلل']}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("لا توجد بيانات لإصدار تقارير.")

# --- التبويب 3: الإحصائيات ---
with tabs[2]:
    if not st.session_state.df.empty:
        fig = px.pie(st.session_state.df, names='الحالة', title="تحليل الحالات العامة")
        st.plotly_chart(fig)
