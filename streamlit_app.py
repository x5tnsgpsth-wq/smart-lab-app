import streamlit as st
import pandas as pd
import plotly.express as px # للمخططات الاحترافية
from datetime import datetime
import os
import urllib.parse

# 1. إعدادات الهوية الفائقة
st.set_page_config(page_title="LabPro Enterprise", page_icon="🔬", layout="wide")

# 2. إدارة البيانات
DB_FILE = "lab_pro_v21.csv"
def save_db(data): pd.DataFrame(data).to_csv(DB_FILE, index=False, encoding='utf-8-sig')
def load_db(): return pd.read_csv(DB_FILE).to_dict('records') if os.path.exists(DB_FILE) else []

if 'patients' not in st.session_state: st.session_state.patients = load_db()
if 'inv' not in st.session_state: st.session_state.inv = {"Glucose": 100, "CBC": 100, "HbA1c": 50, "Urea": 50}

NR = {"Glucose": [70, 126], "CBC": [12, 16], "HbA1c": [4, 5.6], "Urea": [15, 45]}

# --- تصميم الواجهة الاحترافية ---
st.title("🔬 منظومة المختبر الذكي - الإصدار الاحترافي")
tabs = st.tabs(["➕ الإدخال السريع", "📊 لوحة التحليل", "📦 المستودع", "🔐 الإدارة المالية"])

# التبويب 1: الإدخال مع نظام "البحث المسبق"
with tabs[0]:
    c1, c2 = st.columns([2, 1])
    with c1:
        with st.form("pro_entry"):
            staff = st.text_input("👤 الموظف المسؤول")
            p_name = st.text_input("اسم المريض")
            test_type = st.selectbox("نوع الفحص", list(NR.keys()))
            res = st.number_input("النتيجة المخبرية", format="%.2f")
            submitted = st.form_submit_button("حفظ ومعالجة البيانات")
            
            if submitted and p_name:
                st.session_state.inv[test_type] -= 1
                status, color = ("طبيعي", "green") if NR[test_type][0] <= res <= NR[test_type][1] else (("مرتفع", "red") if res > NR[test_type][1] else ("منخفض", "blue"))
                entry = {"التاريخ": datetime.now().strftime("%Y-%m-%d"), "المريض": p_name, "الفحص": test_type, "النتيجة": res, "الحالة": status, "اللون": color, "الموظف": staff, "الواصل": 15000, "الدين": 0}
                st.session_state.patients.append(entry)
                save_db(st.session_state.patients)
                st.balloons()
    with c2:
        st.info("💡 نصيحة: تأكد من تعقيم الأجهزة بعد كل فحص CBC لضمان دقة النتائج.")

# التبويب 2: لوحة التحليل (المخططات البيانية الاحترافية)
with tabs[1]:
    if st.session_state.patients:
        df = pd.DataFrame(st.session_state.patients)
        st.subheader("📈 تحليل أداء المختبر")
        col1, col2 = st.columns(2)
        
        with col1:
            # مخطط توزيع الفحوصات
            fig1 = px.pie(df, names='الفحص', title='أكثر الفحوصات طلباً', hole=0.4)
            st.plotly_chart(fig1, use_container_width=True)
            
        with col2:
            # مخطط الحالات الطبية
            fig2 = px.bar(df, x='الحالة', color='الحالة', title='توزيع النتائج الطبية')
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("لا توجد بيانات كافية للتحليل حالياً.")

# التبويب 3: المستودع الذكي
with tabs[2]:
    st.subheader("📦 مراقبة المواد الكيميائية")
    inv_df = pd.DataFrame(list(st.session_state.inv.items()), columns=['المادة', 'الكمية المتبقية'])
    st.data_editor(inv_df) # يسمح للمدير بتعديل المخزون يدوياً بضغطة زر
    
    for mat, qty in st.session_state.inv.items():
        if qty < 20:
            st.error(f"🚨 تنبيه: مخزون {mat} منخفض جداً ({qty})! يرجى الطلب فوراً.")

# التبويب 4: الإدارة المالية والأمان
with tabs[3]:
    if st.text_input("رمز وصول المسؤول", type="password") == "2024":
        st.success("تم تأكيد هويتك")
        df_all = pd.DataFrame(st.session_state.patients)
        total_income = df_all['الواصل'].sum()
        st.metric("إجمالي الدخل (IQD)", f"{total_income:,}")
        st.dataframe(df_all)
