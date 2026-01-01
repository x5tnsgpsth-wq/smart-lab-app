import streamlit as st
import pandas as pd
from datetime import datetime
import os
import urllib.parse

# --- 1. إعدادات هوية التطبيق (يجب أن تكون في أول السطور) ---
st.set_page_config(
    page_title="LabPro Smart App", 
    page_icon="🧪", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. كود تحويل الواجهة إلى App (إخفاء عناصر المتصفح) ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    * { direction: rtl; text-align: right; }
    .stApp { background-color: #f4f7f6; }
    /* تنسيق زر الواتساب */
    .wa-btn {
        background-color: #25D366;
        color: white;
        padding: 12px 24px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        border-radius: 8px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. إدارة قاعدة البيانات ---
DB_FILE = "lab_database_v20.csv"
def save_db(data):
    pd.DataFrame(data).to_csv(DB_FILE, index=False, encoding='utf-8-sig')

def load_db():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE).to_dict('records')
    return []

if 'patients' not in st.session_state:
    st.session_state.patients = load_db()

if 'inv' not in st.session_state:
    st.session_state.inv = {"Glucose": 100, "CBC": 100, "HbA1c": 50, "Urea": 50}

NR = {"Glucose": [70, 126], "CBC": [12, 16], "HbA1c": [4, 5.6], "Urea": [15, 45]}

# --- 4. هيكل التطبيق (التبويبات) ---
tab1, tab2, tab3, tab4 = st.tabs(["🧪 تسجيل جديد", "📊 السجلات والواتساب", "📦 المخزن والديون", "⚙️ الإدارة"])

with tab1:
    with st.form("entry_form", clear_on_submit=True):
        staff = st.text_input("👤 اسم المحلل (يدوي)")
        c1, c2 = st.columns(2)
        p_name = c1.text_input("اسم المريض")
        p_test = c1.selectbox("نوع الفحص", list(NR.keys()))
        p_res = c1.number_input("النتيجة", format="%.2f")
        p_price = c2.number_input("السعر", 10000)
        p_paid = c2.number_input("الواصل", 10000)
        p_phone = c2.text_input("رقم الهاتف (9647xxxxxxxx)")
        
        if st.form_submit_button("حفظ وتأمين"):
            if staff and p_name:
                st.session_state.inv[p_test] -= 1
                status, color = ("طبيعي", "green") if NR[p_test][0] <= p_res <= NR[p_test][1] else (("مرتفع", "red") if p_res > NR[p_test][1] else ("منخفض", "blue"))
                entry = {
                    "التاريخ": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "المريض": p_name, "الفحص": p_test, "النتيجة": p_res,
                    "الحالة": status, "اللون": color, "الموظف": staff,
                    "الواصل": p_paid, "الدين": p_price - p_paid, "الهاتف": p_phone
                }
                st.session_state.patients.append(entry)
                save_db(st.session_state.patients)
                st.success("✅ تم الحفظ بنجاح")

with tab2:
    if st.session_state.patients:
        df = pd.DataFrame(st.session_state.patients)
        selected_p = st.selectbox("اختر المريض:", df['المريض'].unique())
        if selected_p:
            d = df[df['المريض'] == selected_p].iloc[-1]
            
            # قسم الواتساب
            msg = f"نتائج فحص {d['الفحص']}: {d['النتيجة']} ({d['الحالة']})"
            wa_url = f"https://wa.me/{d['الهاتف']}?text={urllib.parse.quote(msg)}"
            st.markdown(f'<a href="{wa_url}" class="wa-btn">📲 إرسال عبر واتساب</a>', unsafe_allow_html=True)
            
            # المخطط البياني
            p_history = df[df['المريض'] == selected_p].copy()
            st.line_chart(p_history.set_index('التاريخ')['النتيجة'])
    else: st.info("لا توجد سجلات")

with tab3:
    st.table(pd.DataFrame(st.session_state.inv.items(), columns=["المادة", "الكمية"]))

with tab4:
    if st.text_input("رمز الإدارة", type="password") == "1234":
        if st.button("🔴 تصفير البيانات"):
            st.session_state.patients = []
            save_db([])
            st.rerun()
