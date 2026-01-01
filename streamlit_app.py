import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse

# 1. إعداد الصفحة وتنسيق الوصل
st.set_page_config(page_title="مختبر برو - إصدار التقارير", layout="wide")
st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    .receipt-card {
        border: 2px dashed #000;
        padding: 20px;
        background-color: #fff;
        color: #000;
        font-family: 'Courier New', Courier, monospace;
        border-radius: 5px;
        line-height: 1.6;
    }
    .status-normal { color: green; font-weight: bold; }
    .status-alert { color: red; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# 2. إدارة البيانات
if 'data_list' not in st.session_state:
    st.session_state.data_list = []

# 3. واجهة التطبيق
st.sidebar.title("💳 نظام الفواتير والنتائج")
menu = st.sidebar.radio("القائمة", ["إدخال وحفظ", "عرض الوصل والتقرير", "الإحصائيات المالية"])

if menu == "إدخال وحفظ":
    st.header("📝 تسجيل بيانات المراجع")
    with st.form("main_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("اسم المريض")
            test = st.selectbox("الفحص", ["CBC", "Glucose", "Urea", "HbA1c"])
            price = st.number_input("سعر الفحص", value=10000, step=500)
        with col2:
            res = st.number_input("النتيجة", format="%.2f")
            paid = st.number_input("المبلغ الواصل", value=10000, step=500)
            phone = st.text_input("رقم الهاتف")
            
        if st.form_submit_button("حفظ البيانات"):
            status = "🚨 مرتفع" if res > 110 else "✅ طبيعي"
            entry = {
                "التاريخ": datetime.now().strftime("%Y-%m-%d %I:%M %p"),
                "المريض": name, "الفحص": test, "النتيجة": res,
                "الحالة": status, "السعر": price, "المدفوع": paid,
                "المتبقي": price - paid, "الهاتف": phone
            }
            st.session_state.data_list.append(entry)
            st.success("تم تسجيل البيانات بنجاح!")

elif menu == "عرض الوصل والتقرير":
    st.header("📄 معاينة الوصل / التقرير")
    if st.session_state.data_list:
        df = pd.DataFrame(st.session_state.data_list)
        p_name = st.selectbox("اختر اسم المريض لعرض وصله:", df['المريض'].unique())
        
        if p_name:
            data = df[df['المريض'] == p_name].iloc[-1]
            st.markdown(f"""
            <div class="receipt-card">
                <h2 style="text-align:center;">مختبر التحليلات المرضية</h2>
                <p style="text-align:center;">{data['التاريخ']}</p>
                <hr>
                <p><b>اسم المريض:</b> {data['المريض']}</p>
                <p><b>نوع الفحص:</b> {data['الفحص']}</p>
                <p><b>النتيجة:</b> <span style="font-size:20px;">{data['النتيجة']}</span></p>
                <p><b>الحالة:</b> {data['الحالة']}</p>
                <hr>
                <p><b>المبلغ الكلي:</b> {data['السعر']:,} د.ع</p>
                <p><b>الواصل:</b> {data['المدفوع']:,} د.ع</p>
                <p><b>المتبقي بذمته:</b> <span style="color:red;">{data['المتبقي']:,} د.ع</span></p>
                <hr>
                <p style="text-align:center;">شكراً لثقتكم بنا</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.info("💡 نصيحة: يمكنك التقاط صورة للشاشة (Screenshot) وإرسالها للمريض مباشرة.")
    else:
        st.info("لا توجد بيانات لعرضها.")

elif menu == "الإحصائيات المالية":
    st.header("📊 ملخص الحسابات")
    if st.session_state.data_list:
        df = pd.DataFrame(st.session_state.data_list)
        st.metric("إجمالي الديون (المبالغ المتبقية)", f"{df['المتبقي'].sum():,} د.ع")
        st.dataframe(df[['المريض', 'الفحص', 'المتبقي', 'التاريخ']])
