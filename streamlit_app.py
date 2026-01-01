import streamlit as st
import pandas as pd
from datetime import datetime
import os
import urllib.parse

# 1. إعدادات التطبيق
st.set_page_config(page_title="مختبر برو v19", page_icon="🧪", layout="wide")
st.markdown("<style> * { direction: rtl; text-align: right; } </style>", unsafe_allow_html=True)

# 2. إدارة البيانات
DB_FILE = "lab_pro_v19.csv"
def save_db(data): pd.DataFrame(data).to_csv(DB_FILE, index=False, encoding='utf-8-sig')
def load_db(): return pd.read_csv(DB_FILE).to_dict('records') if os.path.exists(DB_FILE) else []

if 'patients' not in st.session_state: st.session_state.patients = load_db()
if 'inv' not in st.session_state: st.session_state.inv = {"Glucose": 100, "CBC": 100, "HbA1c": 50, "Urea": 50}

NR = {"Glucose": [70, 126], "CBC": [12, 16], "HbA1c": [4, 5.6], "Urea": [15, 45]}

tab1, tab2, tab3, tab4 = st.tabs(["🧪 تسجيل جديد", "📊 السجل والواتساب", "📦 المخزن والديون", "⚙️ الإدارة"])

# التبويب 1: التسجيل
with tab1:
    with st.form("main_entry", clear_on_submit=True):
        staff = st.text_input("👤 اسم المحلل (يدوي)")
        c1, c2 = st.columns(2)
        p_name = c1.text_input("اسم المريض")
        p_test = c1.selectbox("نوع الفحص", list(NR.keys()))
        p_res = c1.number_input("النتيجة", format="%.2f")
        p_price, p_paid = c2.number_input("السعر", 10000), c2.number_input("الواصل", 10000)
        p_phone = c2.text_input("رقم الهاتف (مثال: 9647xxxxxxxx)")
        
        if st.form_submit_button("حفظ النتيجة"):
            if staff and p_name:
                st.session_state.inv[p_test] -= 1
                status, color = ("طبيعي", "green") if NR[p_test][0] <= p_res <= NR[p_test][1] else (("مرتفع", "red") if p_res > NR[p_test][1] else ("منخفض", "blue"))
                entry = {"التاريخ": datetime.now().strftime("%Y-%m-%d %H:%M"), "المريض": p_name, "الفحص": p_test, "النتيجة": p_res, "الحالة": status, "اللون": color, "الموظف": staff, "الواصل": p_paid, "الدين": p_price - p_paid, "الهاتف": p_phone}
                st.session_state.patients.append(entry)
                save_db(st.session_state.patients)
                st.success("تم الحفظ بنجاح!")

# التبويب 2: السجل والمخطط وإرسال واتساب
with tab2:
    if st.session_state.patients:
        df = pd.DataFrame(st.session_state.patients)
        selected_p = st.selectbox("اختر المريض:", df['المريض'].unique())
        if selected_p:
            p_history = df[df['المريض'] == selected_p].copy()
            d = p_history.iloc[-1]
            
            # زر الواتساب الذكي
            phone_num = str(d['الهاتف']).replace(" ", "")
            if not phone_num.startswith('964') and len(phone_num) > 9:
                phone_num = '964' + phone_num[-10:] # تحويل الرقم للترميز الدولي العراقي
            
            msg = f"مرحباً سيد/ة {d['المريض']}\nنتائج فحص {d['الفحص']} هي: {d['النتيجة']}\nالحالة: {d['الحالة']}\nشكراً لزيارتكم مختبرنا."
            wa_link = f"https://wa.me/{phone_num}?text={urllib.parse.quote(msg)}"
            
            st.markdown(f'<a href="{wa_link}" target="_blank" style="background-color:#25D366; color:white; padding:10px 20px; text-decoration:none; border-radius:5px; font-weight:bold;">📲 إرسال النتيجة عبر واتساب</a>', unsafe_allow_html=True)
            
            st.divider()
            # المخطط البياني لتطور الحالة
            st.subheader(f"📈 مخطط {d['الفحص']}")
            chart_data = p_history[p_history['الفحص'] == d['الفحص']].set_index('التاريخ')['النتيجة']
            if len(chart_data) > 1: st.line_chart(chart_data)
            st.dataframe(p_history[['التاريخ', 'الفحص', 'النتيجة', 'الحالة', 'الموظف']])
    else: st.info("لا توجد سجلات.")

# التبويب 3 و 4 (المخزن والإدارة)
with tab3:
    st.table(pd.DataFrame(st.session_state.inv.items(), columns=["المادة", "الكمية"]))
    if st.session_state.patients: st.error(f"إجمالي ديون المختبر: {pd.DataFrame(st.session_state.patients)['الدين'].sum():,} د.ع")

with tab4:
    pwd = st.text_input("رمز الإدارة", type="password")
    if pwd == "1234":
        if st.session_state.patients:
            df_admin = pd.DataFrame(st.session_state.patients)
            st.table(df_admin.groupby('الموظف').agg({'الواصل': 'sum', 'المريض': 'count'}))
            if st.button("🔴 تصفير اليومية"):
                st.session_state.patients = []; save_db([]); st.rerun()
