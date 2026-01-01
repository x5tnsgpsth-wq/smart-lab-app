import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# --- إعدادات الواجهة الاحترافية ---
st.set_page_config(page_title="Smart Lab AI", layout="wide")

# وظائف ذكية للتشخيص
def get_medical_advice(test, result):
    if test == "Glucose":
        if result > 200: return "⚠️ حرج: سكر مرتفع جداً. يرجى مراجعة الطبيب فوراً."
        if result < 60: return "⚠️ حرج: هبوط حاد في السكر."
    if test == "CBC" and result < 8:
        return "⚠️ تنبيه: فقر دم حاد (Anemia)."
    return "✅ النتيجة ضمن النطاق المقبول حالياً."

# --- قاعدة البيانات ---
DB_FILE = "smart_lab_v25.csv"
if 'df' not in st.session_state:
    if os.path.exists(DB_FILE):
        st.session_state.df = pd.read_csv(DB_FILE)
    else:
        st.session_state.df = pd.DataFrame(columns=["التاريخ", "المريض", "الفحص", "النتيجة", "الحالة", "النصيحة", "الهاتف"])

# --- واجهة الإدخال ---
st.title("🧪 مختبر الذكاء الاصطناعي - v25")

with st.expander("➕ تسجيل فحص جديد (اضغط للفتح)", expanded=True):
    with st.form("smart_form"):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("اسم المريض")
            test_type = st.selectbox("نوع الفحص", ["Glucose", "CBC", "HbA1c", "Urea"])
        with c2:
            res_val = st.number_input("النتيجة", format="%.2f")
            phone = st.text_input("رقم الواتساب")
        
        if st.form_submit_button("تحليل وحفظ النتيجة"):
            advice = get_medical_advice(test_type, res_val)
            status = "طبيعي" # يمكن تطوير المنطق هنا أكثر
            
            new_row = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), name, test_type, res_val, status, advice, phone]], 
                                    columns=st.session_state.df.columns)
            st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
            st.session_state.df.to_csv(DB_FILE, index=False)
            st.success("تم الحفظ والتحليل بنجاح")

# --- عرض البيانات والتحليل ---
st.subheader("📊 السجل الطبي الذكي")
st.dataframe(st.session_state.df.tail(10), use_container_width=True)

# إضافة رسم بياني تلقائي لأكثر الفحوصات طلباً
if not st.session_state.df.empty:
    fig = px.bar(st.session_state.df, x="الفحص", title="إحصائيات الفحوصات اليومية", color="الفحص")
    st.plotly_chart(fig, use_container_width=True)
