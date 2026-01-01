import streamlit as st
import pandas as pd
from datetime import datetime

# 1. إعدادات الصفحة
st.set_page_config(page_title="نظام المختبر الشامل v4.0", layout="wide")
st.markdown("<style> * { direction: rtl; text-align: right; } </style>", unsafe_allow_html=True)

# 2. تهيئة مخازن البيانات (Session State)
if 'patients' not in st.session_state: st.session_state.patients = []
if 'inventory' not in st.session_state:
    st.session_state.inventory = {
        "Glucose": {"qty": 50, "price": 5000, "cost": 1500},
        "CBC": {"qty": 30, "price": 10000, "cost": 4000},
        "HbA1c": {"qty": 20, "price": 15000, "cost": 6000}
    }

# 3. القائمة الجانبية (Sidebar)
st.sidebar.title("🏥 لوحة التحكم")
user = st.sidebar.selectbox("الموظف الحالي:", ["د. محمد", "المحلل علي", "المحللة سارة"])
menu = st.sidebar.radio("القائمة الرئيسية:", 
    ["➕ تسجيل فحص ودفع", "📋 سجل المرضى والديون", "📦 المخزن والنواقص", "📊 الأرباح والإحصائيات"])

# --- الشاشة 1: تسجيل فحص ودفع ---
if menu == "➕ تسجيل فحص ودفع":
    st.header(f"📝 تسجيل فحص جديد - المحلل: {user}")
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("اسم المريض")
            test = st.selectbox("نوع الفحص", list(st.session_state.inventory.keys()))
            res = st.number_input("النتيجة", format="%.2f")
        with col2:
            total_price = st.number_input("السعر المقرر", value=st.session_state.inventory[test]["price"])
            paid = st.number_input("المبلغ الواصل الآن", value=total_price)
            phone = st.text_input("رقم الهاتف (للواتساب)")
        
        if st.form_submit_button("حفظ البيانات"):
            if st.session_state.inventory[test]["qty"] > 0:
                # خصم من المخزن
                st.session_state.inventory[test]["qty"] -= 1
                # حساب الربح
                profit = paid - st.session_state.inventory[test]["cost"]
                # إضافة للسجل
                entry = {
                    "التاريخ": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "المريض": name, "الفحص": test, "النتيجة": res,
                    "الواصل": paid, "المتبقي": total_price - paid,
                    "الربح": profit, "المحلل": user, "الهاتف": phone
                }
                st.session_state.patients.append(entry)
                st.success(f"✅ تم الحفظ. المتبقي بذمة المريض: {total_price - paid} د.ع")
            else:
                st.error("⚠️ مادة الفحص نفدت من المخزن!")

# --- الشاشة 2: سجل المرضى والديون ---
elif menu == "📋 سجل المرضى والديون":
    st.header("📋 سجل المراجعات والديون")
    if st.session_state.patients:
        df = pd.DataFrame(st.session_state.patients)
        # فلتر للديون فقط
        show_debts = st.checkbox("عرض الديون فقط")
        if show_debts:
            df = df[df['المتبقي'] > 0]
        st.dataframe(df[['التاريخ', 'المريض', 'الفحص', 'النتيجة', 'الواصل', 'المتبقي', 'المحلل']], use_container_width=True)
        st.metric("إجمالي الديون المتبقية بالخارج", f"{df['المتبقي'].sum():,} د.ع")
    else: st.info("لا توجد بيانات سجلات.")

# --- الشاشة 3: المخزن والنواقص ---
elif menu == "📦 المخزن والنواقص":
    st.header("📦 حالة المخازن")
    inv_data = []
    for k, v in st.session_state.inventory.items():
        inv_data.append({"المادة": k, "الكمية المتبقية": v["qty"], "سعر الفحص": v["price"]})
    
    st.table(pd.DataFrame(inv_data))
    
    with st.expander("➕ تزويد المخزن"):
        item_add = st.selectbox("المادة:", list(st.session_state.inventory.keys()))
        qty_add = st.number_input("الكمية المضافة:", min_value=1)
        if st.button("تحديث الكمية"):
            st.session_state.inventory[item_add]["qty"] += qty_add
            st.rerun()

# --- الشاشة 4: الأرباح والإحصائيات ---
elif menu == "📊 الأرباح والإحصائيات":
    st.header("📊 التحليل المالي والإداري")
    if st.session_state.patients:
        df_fin = pd.DataFrame(st.session_state.patients)
        c1, c2, c3 = st.columns(3)
        c1.metric("إجمالي الإيراد (كاش)", f"{df_fin['الواصل'].sum():,} د.ع")
        c2.metric("صافي الربح الحقيقي", f"{df_fin['الربح'].sum():,} د.ع")
        c3.metric("عدد الفحوصات اليوم", len(df_fin))
        
        st.subheader("إنتاجية المحللين")
        st.bar_chart(df_fin['المحلل'].value_counts())
    else: st.warning("لا توجد بيانات مالية كافية.")
    st.header("⚙️ ضبط تكلفة الفحوصات")
    st.write("حدد سعر البيع وتكلفة المواد لكل فحص لضمان دقة الحسابات:")
    for test, info in st.session_state.inventory_costs.items():
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.inventory_costs[test]["price"] = st.number_input(f"سعر فحص {test}", value=info["price"])
        with col2:
            st.session_state.inventory_costs[test]["cost"] = st.number_input(f"تكلفة مواد {test}", value=info["cost"])
