# streamlit_app.py
import streamlit as st
import pandas as pd
from fpdf import FPDF

# إعداد DataFrame لتخزين النتائج
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=['اسم المريض', 'الاختبار', 'النتيجة', 'ملاحظات', 'الحالة'])

st.set_page_config(page_title="المختبر الذكي", layout="wide")
st.title("المختبر الذكي - تطبيق ويب")

# --- إدخال البيانات ---
st.subheader("إدخال نتيجة جديدة")
patient_name = st.text_input("اسم المريض")
test_name = st.text_input("الاختبار")
result_value = st.number_input("النتيجة")
notes = st.text_input("ملاحظات")

if st.button("إضافة النتيجة"):
    st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([{
        'اسم المريض': patient_name,
        'الاختبار': test_name,
        'النتيجة': result_value,
        'ملاحظات': notes,
        'الحالة': 'جديدة'
    }])], ignore_index=True)
    st.success(f"تمت إضافة نتيجة {patient_name}!")

# --- عرض النتائج ---
st.subheader("النتائج")
st.dataframe(st.session_state.df)

# --- تعديل نتيجة ---
st.subheader("تعديل نتيجة")
if not st.session_state.df.empty:
    idx = st.number_input("رقم الصف للتعديل", min_value=0, max_value=len(st.session_state.df)-1, step=1)
    field = st.selectbox("اختر الحقل للتعديل", ['اسم المريض', 'الاختبار', 'النتيجة', 'ملاحظات'])
    new_value = st.text_input("القيمة الجديدة")
    if st.button("تعديل"):
        if field == 'النتيجة':
            st.session_state.df.at[idx, field] = float(new_value)
        else:
            st.session_state.df.at[idx, field] = new_value
        st.session_state.df.at[idx, 'الحالة'] = 'معدلة'
        st.success(f"تم تعديل الصف {idx}!")

# --- حفظ Excel ---
if st.button("حفظ Excel"):
    st.session_state.df.drop(columns=['الحالة']).to_excel("نتائج_المختبر.xlsx", index=False)
    st.success("تم حفظ Excel بنجاح!")

# --- تصدير PDF ---
if st.button("تصدير PDF"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, "نتائج المختبر", ln=True, align="C")
    pdf.ln(5)
    for i, row in st.session_state.df.iterrows():
        pdf.cell(0, 8, f"{i+1}. {row['اسم المريض']} - {row['الاختبار']} - {row['النتيجة']} - {row['ملاحظات']}", ln=True)
    pdf.output("نتائج_المختبر.pdf")
    st.success("تم تصدير PDF بنجاح!")
