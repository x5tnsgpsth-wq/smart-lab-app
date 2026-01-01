import streamlit as st
import pandas as pd
from datetime import datetime
import os
import urllib.parse

# 1. إعدادات الصفحة والنمط العام
st.set_page_config(page_title="مختبر التحليلات المتكامل - النسخة المؤمنة", layout="wide")
st.markdown("<style> * { direction: rtl; text-align: right; } .stTabs [data-baseweb='tab-list'] { gap: 10px; } </style>", unsafe_allow_html=True)

# 2. وظائف تأمين البيانات (Backup System)
def save_data(data):
    df = pd.DataFrame(data)
    df.to_csv("lab_database_backup.csv", index=False, encoding='utf-8-sig')

def load_data():
    if os.path.exists("lab_database_backup.csv"):
        return pd.read_csv("lab_database_backup.csv").to_dict('records')
    return []

# 3. تهيئة البيانات من النسخة الاحتياطية
if 'patients' not in st.session_state:
    st.session_state.patients = load_data()

if 'inv' not in st.session_state:
    st.session_state.inv = {"Glucose": 100, "CBC": 100, "HbA1c": 50, "Urea": 50}

# 4. التبويبات الرئيسية
tab1, tab2, tab3, tab4 = st.tabs(["📝 تسجيل الفحوصات", "📜 الوصل والباركود", "📦 المخزن والمالية", "🛡️ الأمان والأرشيف"])

# --- التبويب 1: التسجيل ---
with tab1:
    st.subheader("إدخال بيانات مراجع")
    with st.form("main_form", clear_on_submit=True):
        staff_user = st.text_input("👤 اسم المحلل المسؤول (كتابة يدوية)")
        st.divider()
        c1, c2 = st.columns(2)
        p_name = c1.text_input("اسم المريض الكامل")
        p_test = c1.selectbox("نوع الفحص المجرى", list(st.session_state.inv.keys()))
        p_res = c1.number_input("النتيجة المخبرية", format="%.2f")
        
        p_price = c2.number_input("السعر الكلي", value=10000)
        p_paid = c2.number_input("المبلغ المدفوع", value=10000)
        p_phone = c2.text_input("رقم هاتف المريض")
        
        if st.form_submit_button("حفظ وتأمين البيانات"):
            if staff_user and p_name:
                st.session_state.inv[p_test] -= 1
                new_entry = {
                    "التاريخ": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "المريض": p_name, "الفحص": p_test, "النتيجة": p_res,
                    "الواصل": p_paid, "الدين": p_price - p_paid, 
                    "الموظف": staff_user, "الهاتف": p_phone
                }
                st.session_state.patients.append(new_entry)
                save_data(st.session_state.patients) # حفظ فوري في الملف
                st.success(f"✅ تم الحفظ وتأمين النسخة الاحتياطية بواسطة {staff_user}")
            else:
                st.error("يرجى إدخال اسم الموظف والمريض!")

# --- التبويب 2: الوصل والباركود ---
with tab2:
    if st.session_state.patients:
        df = pd.DataFrame(st.session_state.patients)
        p_sel = st.selectbox("اختر المريض لإصدار الوصل:", df['المريض'].unique())
        if p_sel:
            data = df[df['المريض'] == p_sel].iloc[-1]
            qr_text = f"Patient:{data['المريض']}|Result:{data['النتيجة']}|By:{data['الموظف']}"
            qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=120x120&data={urllib.parse.quote(qr_text)}"
            
            st.markdown(f"""
            <div style="border:3px solid #000; padding:15px; background:white; color:black; border-radius:10px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h2 style="margin:0;">مختبر التحليلات المرضية</h2>
                    <img src="{qr_url}">
                </div>
                <hr style="border:1px solid #000">
                <p><b>التاريخ:</b> {data['التاريخ']}</p>
                <p><b>المريض:</b> {data['المريض']}</p>
                <p><b>الفحص:</b> {data['الفحص']} | <b>النتيجة:</b> <span style="font-size:24px; color:red;">{data['النتيجة']}</span></p>
                <p><b>المحلل المسؤول:</b> {data['الموظف']}</p>
                <p><b>الحالة المالية:</b> مدفوع {data['الواصل']:,} | متبقي {data['الدين']:,}</p>
            </div>
            """, unsafe_allow_html=True)
            st.info("💡 يمكن تصوير الشاشة لإرسال الوصل للمريض.")
    else: st.info("لا توجد بيانات سجلات.")

# --- التبويب 3: المخزن والمالية ---
with tab3:
    if st.session_state.patients:
        df_fin = pd.DataFrame(st.session_state.patients)
        c1, c2 = st.columns(2)
        c1.metric("نقد الصندوق اليوم", f"{df_fin['الواصل'].sum():,} د.ع")
        c2.metric("الديون الخارجية", f"{df_fin['الدين'].sum():,} د.ع", delta_color="inverse")
    
    st.write("📦 حالة المخزن:")
    st.table(pd.DataFrame(st.session_state.inv.items(), columns=["المادة", "الكمية"]))

# --- التبويب 4: الأمان والأرشيف ---
with tab4:
    st.subheader("🛡️ مركز الأمان")
    if st.session_state.patients:
        df_arch = pd.DataFrame(st.session_state.patients)
        st.write("إدارة البيانات:")
        csv = df_arch.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 تحميل الأرشيف بالكامل (Excel)", csv, "lab_full_backup.csv", "text/csv")
        
        if st.button("🔄 تحديث يدوي للنسخة الاحتياطية"):
            save_data(st.session_state.patients)
            st.success("تم تحديث ملف النسخة الاحتياطية بنجاح!")
        
        st.dataframe(df_arch)
    else: st.warning("لا توجد بيانات للأرشفة.")
