import streamlit as st
import pandas as pd
from datetime import datetime
import os
import urllib.parse

# إعدادات الواجهة
st.set_page_config(page_title="مختبر برو v12", layout="wide")
st.markdown("<style> * { direction: rtl; text-align: right; } .stTabs [data-baseweb='tab-list'] { gap: 15px; font-weight: bold; color: #1e88e5; } </style>", unsafe_allow_html=True)

# إدارة البيانات
def save_db(data): pd.DataFrame(data).to_csv("master_db.csv", index=False, encoding='utf-8-sig')
def load_db(): return pd.read_csv("master_db.csv").to_dict('records') if os.path.exists("master_db.csv") else []

if 'patients' not in st.session_state: st.session_state.patients = load_db()
if 'inv' not in st.session_state: st.session_state.inv = {"Glucose": 100, "CBC": 100, "HbA1c": 50, "Urea": 50}

NR = {
    "Glucose": {"min": 70, "max": 126, "unit": "mg/dL"},
    "CBC": {"min": 12, "max": 16, "unit": "g/dL"},
    "HbA1c": {"min": 4, "max": 5.6, "unit": "%"},
    "Urea": {"min": 15, "max": 45, "unit": "mg/dL"}
}

tab1, tab2, tab3, tab4 = st.tabs(["➕ إدخال وتحليل", "📜 وصل وباركود", "📦 مخزن وديون", "📊 أداء وأرشيف"])

with tab1:
    with st.form("main_form", clear_on_submit=True):
        staff = st.text_input("👤 اسم المحلل (يدوي)")
        c1, c2 = st.columns(2)
        name = c1.text_input("اسم المريض")
        test = c1.selectbox("الفحص", list(NR.keys()))
        res = c1.number_input("النتيجة", format="%.2f")
        price, paid = c2.number_input("السعر", 10000), c2.number_input("الواصل", 10000)
        phone = c2.text_input("الهاتف")
        if st.form_submit_button("حفظ النتيجة"):
            if staff and name:
                st.session_state.inv[test] -= 1
                status, color = ("طبيعي", "green") if NR[test]["min"] <= res <= NR[test]["max"] else (("مرتفع", "red") if res > NR[test]["max"] else ("منخفض", "blue"))
                entry = {"التاريخ": datetime.now().strftime("%Y-%m-%d %H:%M"), "المريض": name, "الفحص": test, "النتيجة": res, "الحالة": status, "اللون": color, "الموظف": staff, "الواصل": paid, "الدين": price-paid, "الهاتف": phone}
                st.session_state.patients.append(entry)
                save_db(st.session_state.patients)
                st.success(f"تم الحفظ! الحالة: {status}")

with tab2:
    if st.session_state.patients:
        df = pd.DataFrame(st.session_state.patients)
        p = st.selectbox("اختر المريض:", df['المريض'].unique())
        if p:
            d = df[df['المريض'] == p].iloc[-1]
            qr = f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data={urllib.parse.quote(f'P:{d['المريض']}|R:{d['النتيجة']}')}"
            st.markdown(f'<div style="border:3px solid {d["اللون"]}; padding:15px; background:white; color:black; border-radius:10px;"><div style="display:flex; justify-content:space-between;"><h3>وصل مختبرنا</h3><img src="{qr}"></div><hr><p><b>المريض:</b> {d["المريض"]} | <b>المحلل:</b> {d["الموظف"]}</p><p><b>النتيجة:</b> <span style="font-size:24px; color:{d["اللون"]};">{d["النتيجة"]} ({d["الحالة"]})</span></p><p><b>المالية:</b> واصل {d["الواصل"]:,} | متبقي {d["الدين"]:,}</p></div>', unsafe_allow_html=True)

with tab3:
    for k, v in st.session_state.inv.items():
        if v < 5: st.error(f"⚠️ انتباه: مادة {k} شارفت على النفاذ (المتبقي: {v})")
    st.table(pd.DataFrame(st.session_state.inv.items(), columns=["المادة", "الكمية"]))
    if st.session_state.patients: st.warning(f"إجمالي ديون المرضى: {pd.DataFrame(st.session_state.patients)['الدين'].sum():,} د.ع")

with tab4:
    if st.session_state.patients:
        df_all = pd.DataFrame(st.session_state.patients)
        st.bar_chart(df_all['الموظف'].value_counts())
        st.download_button("📥 تحميل الأرشيف Excel", df_all.to_csv(index=False).encode('utf-8-sig'), "lab.csv")
        st.dataframe(df_all)
