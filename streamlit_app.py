import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# 1. إعدادات الهوية الفائقة
st.set_page_config(page_title="LabPro Smart System v26", page_icon="🧪", layout="wide")

# تصميم الواجهة المحسن
st.markdown("""
    <style>
    .stApp { background-color: #f0f2f6; direction: rtl; text-align: right; }
    .wa-btn { background-color: #25D366; color: white; padding: 10px; border-radius: 8px; text-decoration: none; font-weight: bold; display: block; text-align: center; }
    .medical-note { background-color: #fff3cd; padding: 10px; border-right: 5px solid #ffc107; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 2. إدارة البيانات والمخزن
DB_FILE = "advanced_lab_v26.csv"
if 'df' not in st.session_state:
    st.session_state.df = pd.read_csv(DB_FILE) if os.path.exists(DB_FILE) else pd.DataFrame(columns=["التاريخ", "المريض", "الفحص", "النتيجة", "الحالة", "التوصية", "المحلل", "الهاتف", "السعر", "الواصل"])

if 'inventory' not in st.session_state:
    st.session_state.inventory = {"Glucose Strips": 100, "CBC Reagent": 50, "HbA1c Kits": 20}

# خوارزمية التشخيص الذكي
def get_advice(test, val):
    limits = {"Glucose": [70, 126], "CBC": [12, 16], "HbA1c": [4, 5.6], "Urea": [15, 45]}
    if val < limits[test][0]: return "⚠️ النتيجة منخفضة: يرجى مراجعة الطبيب لتقييم الحالة."
    if val > limits[test][1]: return "🚨 النتيجة مرتفعة: تنبيه لمراجعة فورية واتباع الحمية."
    return "✅ النتيجة ضمن النطاق الطبيعي."

# 3. واجهة التطبيق
st.title("🔬 منظومة المختبر الذكي - الإصدار v26")

tabs = st.tabs(["📝 الإدخال والتشخيص", "🔍 سجل المرضى", "📦 المستودع", "📊 الأداء المالي"])

# --- التبويب 1: الإدخال مع التشخيص الذكي ---
with tabs[0]:
    with st.form("main_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("اسم المريض")
            test_type = st.selectbox("نوع الفحص", ["Glucose", "CBC", "HbA1c", "Urea"])
            res = st.number_input("النتيجة", format="%.2f")
        with c2:
            phone = st.text_input("رقم الواتساب")
            price = st.number_input("السعر", value=15000)
            paid = st.number_input("الواصل", value=15000)
        
        staff = st.text_input("👤 المحلل المسؤول")
        
        if st.form_submit_button("تحليل وحفظ"):
            if name and staff:
                advice = get_advice(test_type, res)
                status = "طبيعي" if "ضمن النطاق" in advice else ("مرتفع" if "مرتفعة" in advice else "منخفض")
                
                # تحديث المخزن تلقائياً
                inv_key = f"{test_type} Kits" if test_type != "Glucose" else "Glucose Strips"
                if inv_key in st.session_state.inventory: st.session_state.inventory[inv_key] -= 1
                
                new_data = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d %H:%M"), name, test_type, res, status, advice, staff, phone, price, paid]], columns=st.session_state.df.columns)
                st.session_state.df = pd.concat([st.session_state.df, new_data], ignore_index=True)
                st.session_state.df.to_csv(DB_FILE, index=False)
                
                st.success("✅ تم الحفظ")
                st.info(f"💡 التوصية الطبية: {advice}")

# --- التبويب 2: السجلات مع مخطط التتبع ---
with tabs[1]:
    search = st.text_input("🔍 ابحث بالاسم:")
    filtered = st.session_state.df[st.session_state.df['المريض'].str.contains(search, na=False)]
    st.dataframe(filtered.tail(10), use_container_width=True)
    
    if not filtered.empty:
        sel_p = st.selectbox("اختر مريضاً لمتابعة تاريخه:", filtered['المريض'].unique())
        p_history = st.session_state.df[st.session_state.df['المريض'] == sel_p]
        fig_line = px.line(p_history, x='التاريخ', y='النتيجة', color='الفحص', title=f"📈 مسار نتائج {sel_p}")
        st.plotly_chart(fig_line, use_container_width=True)

# --- التبويب 3: إدارة المستودع الذكية ---
with tabs[2]:
    st.subheader("📦 حالة المخزون الحالية")
    for item, qty in st.session_state.inventory.items():
        if qty < 10: st.error(f"🚨 {item}: {qty} (يرجى الطلب فوراً!)")
        else: st.success(f"✅ {item}: {qty}")

# --- التبويب 4: التقارير المالية المتقدمة ---
with tabs[3]:
    if not st.session_state.df.empty:
        col1, col2 = st.columns(2)
        col1.metric("إجمالي الدخل", f"{st.session_state.df['الواصل'].sum():,} IQD")
        col2.metric("الديون المتبقية", f"{(st.session_state.df['السعر'] - st.session_state.df['الواصل']).sum():,} IQD")
        
        # مخطط نمو الدخل حسب الأيام
        daily_revenue = st.session_state.df.groupby(st.session_state.df['التاريخ'].str[:10])['الواصل'].sum().reset_index()
        fig_revenue = px.area(daily_revenue, x='التاريخ', y='الواصل', title="📊 منحنى الدخل اليومي")
        st.plotly_chart(fig_revenue, use_container_width=True)
