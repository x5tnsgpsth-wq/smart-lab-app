import streamlit as st
import pandas as pd
from datetime import datetime
import os
import urllib.parse

# 1. إعدادات النظام والخطوط
st.set_page_config(page_title="نظام المختبر v15", layout="wide")
st.markdown("""
<style>
    * { direction: rtl; text-align: right; font-family: 'Arial'; }
    .thermal-receipt {
        width: 300px;
        margin: 0 auto;
        padding: 10px;
        border: 1px dashed #000;
        background: white;
        color: black;
        line-height: 1.2;
    }
    .status-badge { padding: 2px 5px; border-radius: 3px; color: white; font-weight: bold; }
    @media print { .no-print { display: none; } }
</style>
""", unsafe_allow_html=True)

# 2. إدارة قاعدة البيانات
DB_FILE = "lab_final_master.csv"
def save_db(data): pd.DataFrame(data).to_csv(DB_FILE, index=False, encoding='utf-8-sig')
def load_db(): return pd.read_csv(DB_FILE).to_dict('records') if os.path.exists(DB_FILE) else []

if 'patients' not in st.session_state: st.session_state.patients = load_db()
if 'inv' not in st.session_state: st.session_state.inv = {"Glucose": 100, "CBC": 100, "HbA1c": 50, "Urea": 50}

# 3. محرك الفحوصات
NR = {
    "Glucose": {"min": 70, "max": 126, "unit": "mg/dL"},
    "CBC": {"min": 12, "max": 16, "unit": "g/dL"},
    "HbA1c": {"min": 4, "max": 5.6, "unit": "%"},
    "Urea": {"min": 15, "max": 45, "unit": "mg/dL"}
}

tab1, tab2, tab3, tab4 = st.tabs(["➕ إدخال مريض", "🖨️ طباعة وصل", "📦 المخزن والديون", "🔐 الإدارة"])

# --- التبويب 1: التسجيل ---
with tab1:
    with st.form("entry_form", clear_on_submit=True):
        staff = st.text_input("👤 اسم الموظف")
        c1, c2 = st.columns(2)
        p_name = c1.text_input("اسم المريض")
        p_test = c1.selectbox("نوع الفحص", list(NR.keys()))
        p_res = c1.number_input("النتيجة", format="%.2f")
        p_paid = c2.number_input("المبلغ المدفوع", 10000)
        p_total = c2.number_input("السعر الكلي", 10000)
        p_phone = c2.text_input("رقم الهاتف")
        
        if st.form_submit_button("حفظ وإصدار"):
            if staff and p_name:
                st.session_state.inv[p_test] -= 1
                status, color = ("Normal", "green") if NR[p_test]["min"] <= p_res <= NR[p_test]["max"] else (("High", "red") if p_res > NR[p_test]["max"] else ("Low", "blue"))
                entry = {
                    "التاريخ": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "المريض": p_name, "الفحص": p_test, "النتيجة": p_res,
                    "الحالة": status, "اللون": color, "الموظف": staff,
                    "الواصل": p_paid, "الدين": p_total - p_paid, "الهاتف": p_phone
                }
                st.session_state.patients.append(entry)
                save_db(st.session_state.patients)
                st.success(f"تم التسجيل بنجاح - الحالة: {status}")

# --- التبويب 2: طباعة الوصل (Thermal Design) ---
with tab2:
    if st.session_state.patients:
        df = pd.DataFrame(st.session_state.patients)
        selected_p = st.selectbox("اختر المريض للطباعة:", df['المريض'].unique())
        if selected_p:
            d = df[df['المريض'] == selected_p].iloc[-1]
            qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=80x80&data={urllib.parse.quote(f'LabResult:{d['النتيجة']}')}"
            
            st.markdown(f"""
            <div class="thermal-receipt">
                <center>
                    <h2 style="margin:0;">مختبر التحليلات</h2>
                    <p style="font-size:12px;">{d['التاريخ']}</p>
                    <img src="{qr_url}">
                </center>
                <hr style="border:0.5px dashed #000">
                <p><b>المريض:</b> {d['المريض']}</p>
                <p><b>الفحص:</b> {d['الفحص']}</p>
                <p><b>النتيجة:</b> <span style="font-size:18px;">{d['النتيجة']}</span> ({d['الحالة']})</p>
                <p><b>المحلل:</b> {d['الموظف']}</p>
                <hr style="border:0.5px dashed #000">
                <p>الواصل: {d['الواصل']:,} | المتبقي: {d['الدين']:,}</p>
                <center><p style="font-size:10px;">نتمنى لكم السلامة</p></center>
            </div>
            """, unsafe_allow_html=True)
            st.button("🖨️ طباعة الآن", help="سيقوم بفتح نافذة الطباعة المتوافقة مع الطابعة الحرارية")
    else: st.info("لا توجد فحوصات.")

# --- التبويب 3: المخزن والديون ---
with tab3:
    st.subheader("الجرد والمخزون")
    st.table(pd.DataFrame(st.session_state.inv.items(), columns=["المادة", "الكمية"]))
    if st.session_state.patients:
        debt = pd.DataFrame(st.session_state.patients)['الدين'].sum()
        st.warning(f"مجموع ديون المختبر بالخارج: {debt:,} د.ع")

# --- التبويب 4: الإدارة ---
with tab4:
    pwd = st.text_input("كلمة مرور الإدارة", type="password")
    if pwd == "1234":
        df_admin = pd.DataFrame(st.session_state.patients)
        st.write("إجمالي الدخل حسب الموظف:")
        st.table(df_admin.groupby('الموظف').agg({'الواصل': 'sum', 'المريض': 'count'}))
        if st.button("🔴 مسح اليومية"):
            st.session_state.patients = []
            if os.path.exists(DB_FILE): os.remove(DB_FILE)
            st.rerun()
