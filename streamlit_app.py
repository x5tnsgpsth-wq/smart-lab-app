import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. إعدادات المنصة الاحترافية ---
st.set_page_config(page_title="BioLab Pro | Multi-User", page_icon="🧬", layout="wide")

# CSS لتصميم عصري ومنعزل
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .auth-container {
        max-width: 500px;
        margin: 100px auto;
        padding: 40px;
        background: white;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        text-align: center;
        border-top: 6px solid #2563eb;
    }
    .user-header {
        background: white; padding: 15px 25px; border-radius: 12px;
        display: flex; justify-content: space-between; align-items: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. إدارة الجلسة ---
if 'user_code' not in st.session_state:
    st.session_state.user_code = None

# --- 3. واجهة الدخول (تحديد الهوية الشخصية) ---
def login_screen():
    st.markdown('<div class="auth-container">', unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/3063/3063176.png", width=80)
    st.markdown("<h2>مرحباً بك في BioLab</h2><p style='color:64748b'>أدخل رمزك الشخصي للوصول لبياناتك المنعزلة</p>", unsafe_allow_html=True)
    
    # الرمز هو الذي يحدد ملف البيانات الخاص بالمستخدم
    u_code = st.text_input("رمز الدخول (مثلاً: 1234 أو اسمك)", type="password")
    
    if st.button("دخول لمساحتي الخاصة", use_container_width=True):
        if u_code:
            st.session_state.user_code = u_code
            st.rerun()
        else:
            st.error("يرجى إدخال رمز لفتح ملفك")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 4. واجهة البرنامج (لكل مستخدم ملفه الخاص) ---
def main_app():
    # تحديد مسار قاعدة البيانات بناءً على الرمز المدخل
    # أي شخص يدخل بنفس الرمز سيجد نفس البيانات، والرموز المختلفة تفتح ملفات مختلفة
    db_file = f"user_data_{st.session_state.user_code}.csv"
    
    # تحميل بيانات المستخدم الحالي فقط
    if 'df' not in st.session_state:
        if os.path.exists(db_file):
            st.session_state.df = pd.read_csv(db_file)
        else:
            st.session_state.df = pd.DataFrame(columns=["التاريخ", "المريض", "الفحص", "النتيجة", "الحالة"])

    # الهيدر
    st.markdown(f"""
        <div class="user-header">
            <div><h3 style="margin:0; color:#1e293b;">🧬 لوحة تحكم المختبر</h3></div>
            <div style="background:#dbeafe; color:#1e40af; padding:5px 15px; border-radius:20px; font-weight:bold;">
                👤 المستخدم: {st.session_state.user_code}
            </div>
        </div>
    """, unsafe_allow_html=True)

    # القائمة الجانبية
    with st.sidebar:
        st.title("⚙️ خيارات")
        if st.button("تسجيل الخروج 🚪"):
            # مسح الجلسة للعودة لشاشة الدخول
            del st.session_state.user_code
            if 'df' in st.session_state: del st.session_state.df
            st.rerun()

    # التبويبات
    t1, t2 = st.tabs(["📂 أرشيفي الخاص", "➕ إضافة فحص جديد"])

    with t1:
        if not st.session_state.df.empty:
            st.dataframe(st.session_state.df, use_container_width=True)
        else:
            st.info("مساحتك الخاصة فارغة حالياً. ابدأ بإضافة بياناتك.")

    with t2:
        with st.form("add_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            name = c1.text_input("اسم المريض")
            test = c2.selectbox("الفحص", ["CBC", "Glucose", "HbA1c"])
            res = c1.number_input("النتيجة")
            stat = c2.selectbox("الحالة", ["طبيعي", "مرتفع", "منخفض"])
            
            if st.form_submit_button("حفظ في ملفي الشخصي"):
                new_data = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), name, test, res, stat]], 
                                       columns=st.session_state.df.columns)
                st.session_state.df = pd.concat([st.session_state.df, new_data], ignore_index=True)
                # الحفظ في الملف الخاص بهذا الرمز فقط
                st.session_state.df.to_csv(db_file, index=False)
                st.success("تم الحفظ في مساحتك الخاصة بنجاح!")
                st.rerun()

# --- 5. منطق التشغيل ---
if st.session_state.user_code is None:
    login_screen()
else:
    main_app()
