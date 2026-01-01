import streamlit as st
import pandas as pd
from datetime import datetime
import os
import urllib.parse

# 1. إعدادات هوية التطبيق
st.set_page_config(page_title="LabPro v18", page_icon="🧪", layout="wide")

# 2. إدارة قاعدة البيانات
DB_FILE = "lab_pro_v18.csv"
def save_db(data): pd.DataFrame(data).to_csv(DB_FILE, index=False, encoding='utf-8-sig')
def load_db(): return pd.read_csv(DB_FILE).to_dict('records') if os.path.exists(DB_FILE) else []

if 'patients' not in st.session_state: st.session_state.patients = load_db()
if 'inv' not in st.session_state: st.session_state.inv = {"Glucose": 100, "CBC": 100, "HbA1c": 50, "Urea": 50}

NR = {"Glucose": [70, 126], "CBC": [12, 16], "HbA1c": [4, 5.6], "Urea": [15, 45]}

tab1, tab2, tab3, tab4 = st.tabs(["🧪 تسجيل الفحص", "📊 السجل والمخطط", "📦 المخزن والديون", "⚙️ الإدارة"])

# التبويب 1: التسجيل (لم يتغير لضمان الاستقرار)
with tab1:
    with st.form("main_entry", clear_on_submit=True):
        staff = st.text_input("👤 اسم المحلل (يدوي)")
        c1, c2 = st.columns(2)
        p_name = c1.text_input("اسم المريض")
        p_test = c1.selectbox("نوع الفحص", list(NR.keys()))
        p_res = c1.number_input("النتيجة", format="%.2f")
        p_price, p_paid = c2.number_input("السعر", 10000), c2.number_input("الواصل", 10000)
        p_phone = c2.text_input("رقم الهاتف")
        if st.form_submit_button("حفظ النتيجة"):
            if staff and p_name:
                st.session_state.inv[p_test] -= 1
                status, color = ("طبيعي", "green") if NR[p_test][0] <= p_res <= NR[p_test][1] else (("مرتفع", "red") if p_res > NR[p_test][1] else ("منخفض", "blue"))
                entry = {"التاريخ": datetime.now().strftime("%Y-%m-%d %H:%M"), "المريض": p_name, "الفحص": p_test, "النتيجة": p_res, "الحالة": status, "اللون": color, "الموظف": staff, "الواصل": p_paid, "الدين": p_price - p_paid, "الهاتف": p_phone}
                st.session_state.patients.append(entry)
                save_db(st.session_state.patients)
                st.success(f"تم الحفظ بنجاح!")

# التبويب 2: السجل والمخطط البياني (التحديث الجديد هنا)
with tab2:
    if st.session_state.patients:
        df = pd.DataFrame(st.session_state.patients)
        selected_p = st.selectbox("اختر مريضاً لعرض تاريخه الصحي:", df['المريض'].unique())
        if selected_p:
            p_history = df[df['المريض'] == selected_p].copy()
            p_history['التاريخ'] = pd.to_datetime(p_history['التاريخ'])
            
            # عرض الوصل الأخير
            d = p_history.iloc[-1]
            st.markdown(f'<div style="border:2px solid {d["اللون"]}; padding:10px; border-radius:10px;"><b>أحدث نتيجة:</b> {d["النتيجة"]} ({d["الحالة"]})</div>', unsafe_allow_html=True)
            
            # المخطط البياني لتطور الحالة
            st.subheader(f"📈 منحنى تطور فحص {d['الفحص']} لـ {selected_p}")
            chart_data = p_history[p_history['الفحص'] == d['الفحص']].set_index('التاريخ')['النتيجة']
            if len(chart_data) > 1:
                st.line_chart(chart_data)
            else:
                st.info("سجل المريض يحتوي على فحص واحد فقط. سيظهر المخطط عند إضافة فحوصات مستقبلية.")
            
            st.write("📋 السجل التاريخي:")
            st.dataframe(p_history[['التاريخ', 'الفحص', 'النتيجة', 'الحالة', 'الموظف']])
    else: st.info("لا توجد بيانات سجلات.")

# التبويب 3 والتبويب 4 (المخزن والإدارة - كما في الكود السابق)
with tab3:
    st.table(pd.DataFrame(st.session_state.inv.items(), columns=["المادة", "الكمية"]))
    if st.session_state.patients:
        st.error(f"إجمالي ديون المختبر: {pd.DataFrame(st.session_state.patients)['الدين'].sum():,} د.ع")

with tab4:
    pwd = st.text_input("رمز الإدارة", type="password")
    if pwd == "1234":
        if st.session_state.patients:
            df_admin = pd.DataFrame(st.session_state.patients)
            st.table(df_admin.groupby('الموظف').agg({'الواصل': 'sum', 'المريض': 'count'}))
            if st.button("🔴 تصفير اليومية"):
                st.session_state.patients = []; save_db([]); st.rerun()
