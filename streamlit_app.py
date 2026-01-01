import streamlit as st
import pandas as pd
from datetime import datetime
import os
import urllib.parse

# 1. إعدادات النظام
st.set_page_config(page_title="مختبر برو v16 - البحث الذكي", layout="wide")
st.markdown("<style> * { direction: rtl; text-align: right; } </style>", unsafe_allow_html=True)

# 2. إدارة البيانات
DB_FILE = "lab_pro_v16.csv"
def save_db(data): pd.DataFrame(data).to_csv(DB_FILE, index=False, encoding='utf-8-sig')
def load_db(): return pd.read_csv(DB_FILE).to_dict('records') if os.path.exists(DB_FILE) else []

if 'patients' not in st.session_state: st.session_state.patients = load_db()
if 'inv' not in st.session_state: st.session_state.inv = {"Glucose": 100, "CBC": 100, "HbA1c": 50, "Urea": 50}

# المعدلات الطبيعية
NR = {"Glucose": [70, 126], "CBC": [12, 16], "HbA1c": [4, 5.6], "Urea": [15, 45]}

tab1, tab2, tab3, tab4 = st.tabs(["🔍 البحث والتسجيل", "🖨️ الوصل والباركود", "📦 المخزن والديون", "🔐 الإدارة"])

# --- التبويب 1: البحث الذكي والتسجيل ---
with tab1:
    st.subheader("البحث عن مريض سابق أو تسجيل جديد")
    all_names = list(set([p['المريض'] for p in st.session_state.patients])) if st.session_state.patients else []
    search_query = st.selectbox("ابحث عن اسم المريض (اتركه فارغاً للمريض الجديد):", [""] + all_names)

    with st.form("entry_form", clear_on_submit=True):
        staff = st.text_input("👤 اسم الموظف الحالي (يدوي)")
        st.divider()
        c1, c2 = st.columns(2)
        # إذا تم اختيار اسم من البحث، يتم وضعه تلقائياً
        p_name = c1.text_input("اسم المريض", value=search_query if search_query else "")
        p_test = c1.selectbox("نوع الفحص", list(NR.keys()))
        p_res = c1.number_input("النتيجة", format="%.2f")
        p_paid = c2.number_input("المبلغ الواصل", 10000)
        p_total = c2.number_input("السعر الكلي", 10000)
        p_phone = c2.text_input("رقم الهاتف")
        
        if st.form_submit_button("حفظ النتيجة"):
            if staff and p_name:
                st.session_state.inv[p_test] -= 1
                status, color = ("طبيعي", "green") if NR[p_test][0] <= p_res <= NR[p_test][1] else (("مرتفع", "red") if p_res > NR[p_test][1] else ("منخفض", "blue"))
                entry = {
                    "التاريخ": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "المريض": p_name, "الفحص": p_test, "النتيجة": p_res,
                    "الحالة": status, "اللون": color, "الموظف": staff,
                    "الواصل": p_paid, "الدين": p_total - p_paid, "الهاتف": p_phone
                }
                st.session_state.patients.append(entry)
                save_db(st.session_state.patients)
                st.success(f"تم الحفظ! النتيجة: {status}")

# --- التبويب 2: تاريخ المريض والوصل ---
with tab2:
    if st.session_state.patients:
        df = pd.DataFrame(st.session_state.patients)
        p_sel = st.selectbox("اختر المريض لعرض تاريخه الطبي:", df['المريض'].unique())
        if p_sel:
            p_history = df[df['المريض'] == p_sel]
            st.write(f"التاريخ الطبي للمريض: {p_sel}")
            st.table(p_history[['التاريخ', 'الفحص', 'النتيجة', 'الحالة', 'الموظف']])
            
            # عرض الوصل الأخير فقط للطباعة
            d = p_history.iloc[-1]
            qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=90x90&data={urllib.parse.quote(f'Patient:{d['المريض']}')}"
            st.markdown(f'<div style="border:2px solid {d["اللون"]}; padding:15px; background:white; color:black; border-radius:10px;"><h4>وصل المختبر</h4><img src="{qr_url}" style="float:left;"><p>المريض: {d["المريض"]}</p><p>النتيجة: {d["النتيجة"]} ({d["الحالة"]})</p><p>الموظف: {d["الموظف"]}</p></div>', unsafe_allow_html=True)
    else: st.info("لا توجد بيانات سجلات.")

# --- التبويب 3: المخزن والديون ---
with tab3:
    st.subheader("الجرد والمستودع")
    st.table(pd.DataFrame(st.session_state.inv.items(), columns=["المادة", "الكمية"]))
    if st.session_state.patients:
        st.warning(f"إجمالي ديون المراجعين: {pd.DataFrame(st.session_state.patients)['الدين'].sum():,} د.ع")

# --- التبويب 4: الإدارة ---
with tab4:
    pwd = st.text_input("رمز الدخول (Admin Only)", type="password")
    if pwd == "1234":
        df_admin = pd.DataFrame(st.session_state.patients)
        st.write("ملخص الإيرادات:")
        st.table(df_admin.groupby('الموظف').agg({'الواصل': 'sum', 'المريض': 'count'}))
        if st.button("🔴 مسح اليومية"):
            st.session_state.patients = []; save_db([]); st.rerun()
