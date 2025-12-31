import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="المختبر الذكي", layout="wide")

# عنوان التطبيق
st.markdown("""
<h1 style='text-align: center;'>🧪 المختبر الذكي</h1>
<h3 style='text-align: center; color: gray;'>إعداد وتطوير: حسن روضه</h3>
<hr>
""", unsafe_allow_html=True)

DATA_FILE = "data.csv"

# تحميل البيانات من الملف إن وجد
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    df = pd.DataFrame(columns=["اسم المريض", "اسم الفحص", "النتيجة", "ملاحظات"])

# حفظ البيانات في session
if "data" not in st.session_state:
    st.session_state.data = df

# إدخال البيانات
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
        # حفظ تلقائي
        st.session_state.data.to_csv(DATA_FILE, index=False)
        st.success("تمت إضافة النتيجة وحفظها تلقائيًا ✅")
    else:
        st.warning("يرجى ملء جميع الحقول")

# عرض البيانات
st.subheader("النتائج المحفوظة")

# مربع البحث
search_name = st.text_input("🔍 ابحث باسم المريض")

if search_name:
    query = f"""
    SELECT * FROM results
    WHERE patient_name LIKE '%{search_name}%'
    """
    df = pd.read_sql_query(query, conn)
else:
    df = pd.read_sql_query("SELECT * FROM results", conn)

st.dataframe(df, use_container_width=True)

# تحميل Excel
if st.button("تحميل Excel"):
    st.session_state.data.to_excel("نتائج_المختبر.xlsx", index=False)
    st.success("تم إنشاء ملف Excel 📁"
