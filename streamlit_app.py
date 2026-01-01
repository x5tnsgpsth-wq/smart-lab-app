import streamlit as st
import pandas as pd
from datetime import datetime
import os
import urllib.parse

# 1. إعدادات هوية التطبيق (تظهر عند التثبيت على الشاشة)
st.set_page_config(
    page_title="LabPro v17", 
    page_icon="🧪", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. إخفاء عناصر المتصفح ليظهر كتطبيق حقيقي
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    * { direction: rtl; text-align: right; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #f0f2f6; 
        border-radius: 5px; 
        padding: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. إدارة قاعدة البيانات
DB_FILE = "lab_pro_v17.csv"
def save_db(data):
    pd.DataFrame(data).to_csv(DB_FILE, index=False, encoding='utf-8-sig')

def load_db():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE).to_dict('records')
    return []

# تهيئة البيانات
if 'patients' not in st.session_state:
    st.session_state.patients = load_db()

if 'inv' not in st.session_state:
    st.session_state.inv = {"Glucose": 100, "CBC": 100, "HbA1c": 50, "Urea": 50}

# المعدلات الطبيعية للتشخيص التلقائي
NR = {
    "Glucose": {"min": 70, "max": 126, "unit": "mg/dL"},
    "CBC": {"min": 12, "max": 16, "unit": "g/dL"},
    "HbA1c": {"min": 4, "max": 5.6, "unit": "%"},
    "Urea": {"min": 15, "max": 45, "unit": "mg/dL"}
}

# --- تقسيم التطبيق إلى تبويبات ---
tab1, tab2, tab3, tab4 = st.tabs(["🧪 تسجيل الفحص", "📜 الفواتير والباركود", "📦 المخزن والديون", "⚙️ الإدارة والأمان"])

# التبويب 1: التسجيل والتشخيص
with tab1:
    st.subheader("📝 إدخال بيانات المراجع")
    with st.form("main_entry", clear_on_submit=True):
        staff = st.text_input("👤 اسم المحلل المسؤول (يدوي)")
        st.divider()
        c1, c2 = st.columns(2)
        p_name = c1.text_input("اسم المريض الثلاثي")
        p_test = c1.selectbox("نوع الفحص", list(NR.keys()))
        p_res = c1.number_input(f"النتيجة ({NR[p_test]['unit']})", format="%.2f")
        
        p_price = c2.number_input("السعر الكلي (د.ع)", value=10000)
        p_paid = c2.number_input("المبلغ المدفوع (الواصل)", value=10000)
        p_phone = c2.text_input("رقم الهاتف")
        
        if st.form_submit_button("حفظ النتيجة وتحديث المخزن"):
            if staff and p_name:
                # التشخيص التلقائي
                status, color = "طبيعي", "green"
                if p_res < NR[p_test]["min"]: status, color = "منخفض", "blue"
                elif p_res > NR[p_test]["max"]: status, color = "مرتفع", "red"
                
                # خصم المخزن
                st.session_state.inv[p_test] -= 1
                
                # إضافة السجل
                entry = {
                    "التاريخ": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "المريض": p_name, "الفحص": p_test, "النتيجة": p_res,
                    "الحالة": status, "اللون": color, "الموظف": staff,
                    "الواصل": p_paid, "الدين": p_price - p_paid, "الهاتف": p_phone
                }
                st.session_state.patients.append(entry)
                save_db(st.session_state.patients)
                st.success(f"تم الحفظ بنجاح! الحالة الطبية: {status}")
            else:
                st.error("يرجى كتابة اسم الموظف واسم المريض!")

# التبويب 2: الفواتير والباركود
with tab2:
    if st.session_state.patients:
        df = pd.DataFrame(st.session_state.patients)
        selected_p = st.selectbox("اختر مريضاً لعرض الوصل:", df['المريض'].unique())
        if selected_p:
            d = df[df['المريض'] == selected_p].iloc[-1]
            qr_text = f"P:{d['المريض']}|Res:{d['النتيجة']}|Staff:{d['الموظف']}"
            qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data={urllib.parse.quote(qr_text)}"
            
            st.markdown(f"""
            <div style="border:3px solid {d['اللون']}; padding:20px; border-radius:10px; background:white; color:black;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h3 style="margin:0; color:#333;">وصل مختبر التحليلات</h3>
                    <img src="{qr_url}">
                </div>
                <hr>
                <p><b>المريض:</b> {d['المريض']} | <b>المحلل:</b> {d['الموظف']}</p>
                <p><b>الفحص:</b> {d['الفحص']} | <b>النتيجة:</b> <span style="font-size:24px; color:{d['اللون']};">{d['النتيجة']} ({d['الحالة']})</span></p>
                <p><b>تاريخ الفحص:</b> {d['التاريخ']}</p>
                <hr>
                <p><b>الحساب:</b> واصل {d['الواصل']:,} | متبقي {d['الدين']:,} د.ع</p>
            </div>
            """, unsafe_allow_html=True)
    else: st.info("السجل فارغ حالياً.")

# التبويب 3: المخزن والديون
with tab3:
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("📦 حالة المواد")
        st.table(pd.DataFrame(st.session_state.inv.items(), columns=["المادة", "الكمية"]))
        for k, v in st.session_state.inv.items():
            if v < 10: st.warning(f"⚠️ مادة {k} شارفت على النفاذ!")
    with col_b:
        st.subheader("💰 الديون المتبقية")
        if st.session_state.patients:
            total_debt = pd.DataFrame(st.session_state.patients)['الدين'].sum()
            st.error(f"إجمالي ديون المختبر بالخارج: {total_debt:,} د.ع")

# التبويب 4: الإدارة والأمان
with tab4:
    pwd = st.text_input("أدخل رمز الإدارة", type="password")
    if pwd == "1234":
        df_admin = pd.DataFrame(st.session_state.patients)
        st.write("📈 إحصائيات الموظفين:")
        st.table(df_admin.groupby('الموظف').agg({'الواصل': 'sum', 'المريض': 'count'}))
        
        csv = df_admin.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 تحميل الأرشيف الشامل (Excel)", csv, "lab_archive.csv")
        
        if st.button("🔴 تصفير السجل اليومي"):
            st.session_state.patients = []
            if os.path.exists(DB_FILE): os.remove(DB_FILE)
            st.rerun()
