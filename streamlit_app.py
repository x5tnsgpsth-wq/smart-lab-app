import streamlit as st
import pandas as pd

st.set_page_config(page_title="المختبر الذكي", layout="wide")
st.markdown("""
<h1 style='text-align: center;'>🧪 المختبر الذكي</h1>
<h3 style='text-align: center; color: gray;'>إعداد وتطوير: حسن روضه</h3>
<hr>
""", unsafe_allow_html=True)

# إنشاء جدول النتائج
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(
        columns=["اسم المريض", "اسم الفحص", "النتيجة", "ملاحظات"]
    )

st.subheader("إدخال نتيجة جديدة")
name = st.text_input("اسم المريض")
test = st.text_input("اسم الفحص")
result = st.text_input("النتيجة")
notes = st.text_input("ملاحظات")

if st.button("إضافة النتيجة"):
    if name and test and result:
        new_row = {
            "اسم المريض": name,
            "اسم الفحص": test,
            "النتيجة": result,
            "ملاحظات": notes
        }
        st.session_state.data = pd.concat(
            [st.session_state.data, pd.DataFrame([new_row])],
            ignore_index=True
        )
        st.success("تمت إضافة النتيجة بنجاح ✅")
    else:
        st.warning("يرجى ملء جميع الحقول")

st.subheader("جدول النتائج")
st.dataframe(st.session_state.data, use_container_width=True)

if st.button("حفظ النتائج كملف Excel"):
    st.session_state.data.to_excel("نتائج_المختبر.xlsx", index=False)
    st.success("تم حفظ الملف بنجاح 📁")
