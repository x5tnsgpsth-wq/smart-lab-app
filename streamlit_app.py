import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse

# 1. إعدادات الصفحة (ثيم فاتح وبسيط لسرعة التحميل)
st.set_page_config(page_title="Lab System Pro", layout="wide")

# تنسيق CSS للعربية ولتحسين مظهر الأزرار
st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; }
    .status-box { padding: 10px; border-radius: 5px; margin-bottom: 10px; border: 1px solid #ddd; }
</style>
""", unsafe_allow_html=True)

# 2. إدارة البيانات (باستخدام Session State لضمان السرعة وعدم الضياع)
if 'data_list' not in st.session_state:
    st.session_state.data_list = []

# 3. واجهة التطبيق
st.title("🧪 نظام إدارة المختبر المتكامل")

# القائمة الجانبية
menu = st.sidebar.radio("القائمة الرئيسية", ["إضافة فحص جديد", "سجل الفحوصات والحسابات", "تصدير البيانات"])

if menu == "إضافة فحص جديد":
    st.subheader("📝 تسجيل بيانات المريض")
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("اسم المريض الثلاثي")
            contact = st.text_input("رقم الهاتف (أو المعرف)")
            test_type = st.selectbox("نوع الفحص", ["CBC", "Glucose", "TSH", "Urea", "Creatinine", "Vitamin D"])
        with col2:
            result = st.number_input("النتيجة", format="%.2f")
            total_price = st.number_input("السعر الكلي (د.ع)", step=500)
            paid_amount = st.number_input("المبلغ المدفوع (د.ع)", step=500)
        
        submit = st.form_submit_button("حفظ وإرسال")
        
        if submit and name:
            new_entry = {
                "التاريخ": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "المريض": name,
                "التواصل": contact,
                "الفحص": test_type,
                "النتيجة": result,
                "السعر": total_price,
                "المدفوع": paid_amount,
                "المتبقي": total_price - paid_amount,
                "الحالة": "مرتفع ⚠️" if result > 110 else "طبيعي ✅"
            }
            st.session_state.data_list.append(new_entry)
            st.success(f"تم حفظ بيانات {name} بنجاح!")

elif menu == "سجل الفحوصات والحسابات":
    st.subheader("📋 سجل المرضى")
    if st.session_state.data_list:
        df = pd.DataFrame(st.session_state.data_list)
        
        # محرك بحث بسيط
        search = st.text_input("🔍 بحث عن مريض")
        if search:
            df = df[df['المريض'].str.contains(search)]
            
        st.dataframe(df, use_container_width=True)
        
        st.divider()
        st.subheader("📤 إرسال النتائج")
        patient_sel = st.selectbox("اختر مريضاً لإرسال نتيجته:", df['المريض'].unique())
        
        if patient_sel:
            row = df[df['المريض'] == patient_sel].iloc[-1]
            msg = f"مرحباً {row['المريض']}، نتيجتك لفحص {row['الفحص']} هي {row['النتيجة']}. المتبقي بذمتكم: {row['المتبقي']} د.ع."
            msg_encoded = urllib.parse.quote(msg)
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f'<a href="https://wa.me/{row["التواصل"]}?text={msg_encoded}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366; color:white; padding:15px; border-radius:10px; text-align:center;">WhatsApp</div></a>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<a href="https://t.me/share/url?url={msg_encoded}&text={row["التواصل"]}" target="_blank" style="text-decoration:none;"><div style="background-color:#0088cc; color:white; padding:15px; border-radius:10px; text-align:center;">Telegram</div></a>', unsafe_allow_html=True)
    else:
        st.info("السجل فارغ حالياً.")

elif menu == "تصدير البيانات":
    st.subheader("💾 حفظ نسخة Excel")
    if st.session_state.data_list:
        df_export = pd.DataFrame(st.session_state.data_list)
        csv = df_export.to_csv(index=False).encode('utf-8-sig')
        
        # الطريقة الأكثر استقراراً للتحميل
        st.download_button(
            label="📥 اضغط هنا لتحميل الملف فوراً",
            data=csv,
            file_name=f"lab_report_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
        
        st.divider()
        if st.button("🗑️ مسح السجل بالكامل"):
            st.session_state.data_list = []
            st.rerun()
    else:
        st.warning("لا توجد بيانات لتصديرها.")
