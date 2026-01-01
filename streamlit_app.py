import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px

# --- 1. إعدادات المنصة الاحترافية ---
st.set_page_config(page_title="BioLab Pro v7.0", page_icon="🧬", layout="wide")

# CSS متقدم لتحسين مظهر الواجهة بالكامل
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .auth-container {
        max-width: 450px; margin: 80px auto; padding: 40px;
        background: white; border-radius: 20px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.1);
        text-align: center; border-top: 8px solid #2563eb;
    }
    .main-header {
        background: white; padding: 20px; border-radius: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05); margin-bottom: 25px;
        display: flex; justify-content: space-between; align-items: center;
        border-right: 6px solid #2563eb;
    }
    .stat-card {
        background: white; padding: 20px; border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        border: 1px solid #e2e8f0; text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. إدارة الجلسة ---
if 'user_code' not in st.session_state:
    st.session_state.user_code = None

# --- 3. بوابة الدخول الشخصية المنعزلة ---
def login_screen():
    st.markdown('<div class="auth-container">', unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/3063/3063176.png", width=70)
    st.markdown("<h2>مختبر BioLab الذكي</h2><p style='color:#64748b'>أدخل رمز الوصول الخاص بك لفتح مساحة العمل</p>", unsafe_allow_html=True)
    
    u_code = st.text_input("رمز الدخول الشخصي", type="password", placeholder="مثلاً: Lab_01")
    
    if st.button("دخول آمن", use_container_width=True):
        if u_code:
            st.session_state.user_code = u_code
            st.rerun()
        else:
            st.warning("يرجى إدخال رمز لفتح ملفك الخاص")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 4. لوحة التحكم المتكاملة ---
def main_app():
    # عزل الملفات بناءً على الرمز
    safe_id = "".join(x for x in st.session_state.user_code if x.isalnum())
    db_file = f"private_db_{safe_id}.csv"
    
    # تحميل البيانات
    if 'df' not in st.session_state:
        if os.path.exists(db_file):
            st.session_state.df = pd.read_csv(db_file)
        else:
            st.session_state.df = pd.DataFrame(columns=["التاريخ", "المريض", "الفحص", "النتيجة", "الحالة", "الهاتف"])

    # الهيدر العلوي المحترف
    st.markdown(f"""
        <div class="main-header">
            <div>
                <h2 style="margin:0; color:#1e293b;">🔬 لوحة تحكم المختبر</h2>
                <p style="margin:0; color:#64748b;">مساحة عمل منعزلة وآمنة</p>
            </div>
            <div style="background:#eff6ff; color:#2563eb; padding:8px 20px; border-radius:30px; font-weight:bold;">
                👤 الرمز الحالي: {st.session_state.user_code}
            </div>
        </div>
    """, unsafe_allow_html=True)

    # القائمة الجانبية (Sidebar)
    with st.sidebar:
        st.markdown("### ⚙️ إدارة الحساب")
        st.write(f"أنت تعمل الآن في ملف: \n`{db_file}`")
        
        # تصدير البيانات للاكسل
        if not st.session_state.df.empty:
            csv = st.session_state.df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 تحميل بياناتي (CSV)", data=csv, file_name=f"my_lab_data.csv", mime='text/csv', use_container_width=True)
        
        if st.button("تسجيل الخروج 🚪", use_container_width=True):
            del st.session_state.user_code
            if 'df' in st.session_state: del st.session_state.df
            st.rerun()

    # التبويبات الاحترافية
    t1, t2, t3 = st.tabs(["📊 البيانات والبحث", "➕ إضافة فحص", "📈 إحصائيات"])

    with t1:
        st.markdown("### 🔍 أرشيف المرضى والبحث المتقدم")
        if not st.session_state.df.empty:
            search_col1, search_col2 = st.columns([2, 1])
            search_query = search_col1.text_input("بحث باسم المريض أو الفحص...", placeholder="اكتب للبحث...")
            
            display_df = st.session_state.df
            if search_query:
                display_df = display_df[display_df['المريض'].str.contains(search_query, na=False) | 
                                        display_df['الفحص'].str.contains(search_query, na=False)]
            
            st.dataframe(display_df, use_container_width=True)
        else:
            st.info("لا توجد سجلات في مساحتك الخاصة بعد.")

    with t2:
        st.markdown("### ✍️ تسجيل فحص جديد")
        with st.form("add_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            name = c1.text_input("اسم المريض الثلاثي")
            test = c2.selectbox("نوع التحليل", ["CBC", "Glucose", "HbA1c", "Urea", "Creatinine"])
            res = c1.number_input("النتيجة المخبرية", format="%.2f")
            phone = c2.text_input("رقم هاتف المريض")
            
            if st.form_submit_button("حفظ البيانات في مساحتي"):
                if name:
                    # منطق الحالة التلقائي
                    status = "Normal" if 70 <= res <= 110 else "Check Required" # مثال بسيط
                    
                    new_entry = pd.DataFrame([[
                        datetime.now().strftime("%Y-%m-%d"), name, test, res, status, phone
                    ]], columns=st.session_state.df.columns)
                    
                    st.session_state.df = pd.concat([st.session_state.df, new_entry], ignore_index=True)
                    st.session_state.df.to_csv(db_file, index=False)
                    st.success(f"تمت إضافة {name} بنجاح إلى ملفك الشخصي!")
                    st.rerun()
                else:
                    st.error("يرجى كتابة اسم المريض")

    with t3:
        st.markdown("### 📈 التحليل الإحصائي")
        if not st.session_state.df.empty:
            m1, m2, m3 = st.columns(3)
            m1.metric("إجمالي الفحوصات", len(st.session_state.df))
            m2.metric("مرضى فريدون", st.session_state.df["المريض"].nunique())
            m3.metric("فحوصات اليوم", len(st.session_state.df[st.session_state.df['التاريخ'] == datetime.now().strftime("%Y-%m-%d")]))
            
            st.divider()
            # رسم بياني لتوزيع الفحوصات
            fig = px.pie(st.session_state.df, names='الفحص', title='توزيع أنواع التحاليل', hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("أضف بيانات لتظهر لك الإحصائيات هنا.")

# --- 5. منطق التشغيل الأساسي ---
if st.session_state.user_code is None:
    login_screen()
else:
    main_app()
