import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse

# 1. إعدادات الصفحة والستايل الاحترافي للوصل
st.set_page_config(page_title="نظام المختبر الذكي - v6", layout="wide")
st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    .receipt-box {
        border: 2px solid #4A90E2;
        padding: 20px;
        border-radius: 15px;
        background-color: #f9f9f9;
        box-shadow: 2px 2px 12px rgba(0,0,0,0.1);
    }
    .staff-tag { background-color: #e1f5fe; padding: 5px 10px; border-radius: 5px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# 2. تهيئة البيانات
if 'patients' not in st.session_state: st.session_state.patients = []
if 'inv' not in st.session_state: st.session_state.inv = {"Glucose": 100, "CBC": 100, "HbA1c": 50}

# 3. التبويبات
tab1, tab2, tab3 = st.tabs(["📝 إدخال النتائج", "📜 المعاينة والباركود", "📦 الإدارة المالية"])

with tab1:
    st.subheader("تسجيل مراجع جديد")
    with st.form("entry_form", clear_on_submit=True):
        staff_name = st.text_input("اسم الموظف المسؤول (يدوياً)")
        st.divider()
        col1, col2 = st.columns(2)
        p_name = col1.text_input("اسم المريض")
        p_test = col1.selectbox("نوع الفحص", list(st.session_state.inv.keys()))
        p_res = col1.number_input("النتيجة المباشرة", format="%.2f")
        p_price = col2.number_input("سعر الفحص", value=10000)
        p_paid = col2.number_input("المبلغ الواصل", value=10000)
        p_phone = col2.text_input("رقم الهاتف")
        
        if st.form_submit_button("حفظ وإصدار"):
            if staff_name and p_name:
                st.session_state.inv[p_test] -= 1
                st.session_state.patients.append({
                    "id": len(st.session_state.patients) + 1,
                    "التاريخ": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "المريض": p_name, "الفحص": p_test, "النتيجة": p_res,
                    "الواصل": p_paid, "الدين": p_price - p_paid, 
                    "الموظف": staff_name, "الهاتف": p_phone
                })
                st.success(f"تم تسجيل البيانات بنجاح بواسطة {staff_name}")
            else:
                st.error("يرجى إكمال البيانات الأساسية")

with tab2:
    st.subheader("🔍 معاينة الوصل والباركود")
    if st.session_state.patients:
        df = pd.DataFrame(st.session_state.patients)
        p_sel = st.selectbox("اختر المريض لعرض تفاصيله:", df['المريض'].unique())
        
        if p_sel:
            data = df[df['المريض'] == p_sel].iloc[-1]
            # إنشاء رابط الباركود (يحتوي على ملخص البيانات)
            qr_data = f"Patient: {data['المريض']} | Test: {data['الفحص']} | Result: {data['النتيجة']} | Staff: {data['الموظف']}"
            qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={urllib.parse.quote(qr_data)}"
            
            # عرض الوصل الاحترافي
            st.markdown(f"""
            <div class="receipt-box">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h3>مختبر التحليلات المتقدم</h3>
                        <p>تاريخ الفحص: {data['التاريخ']}</p>
                    </div>
                    <img src="{qr_url}" width="100">
                </div>
                <hr>
                <p><b>اسم المريض:</b> {data['المريض']}</p>
                <p><b>نوع الفحص:</b> {data['الفحص']} | <b>النتيجة:</b> <span style="color:red; font-size:20px;">{data['النتيجة']}</span></p>
                <p><b>الموظف المسؤول:</b> <span class="staff-tag">{data['الموظف']}</span></p>
                <hr>
                <p>الحالة المالية: الواصل {data['الواصل']:,} د.ع | المتبقي {data['الدين']:,} د.ع</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.info("💡 يمكنك الآن أخذ لقطة شاشة للوصل وإرسالها للمريض.")
    else:
        st.info("لا توجد فحوصات مسجلة")

with tab3:
    st.subheader("📊 الجرد والمخزن")
    # ميزة عرض الديون باللون الأحمر
    if st.session_state.patients:
        df_fin = pd.DataFrame(st.session_state.patients)
        total_debt = df_fin['الدين'].sum()
        st.error(f"⚠️ إجمالي الديون التي لم تسدد بعد: {total_debt:,} د.ع")
        st.write("حالة المواد في المخزن:")
        st.table(pd.DataFrame(st.session_state.inv.items(), columns=["المادة", "الكمية المتبقية"]))
