import streamlit as st
import pandas as pd
import os
from datetime import datetime
import time

# 1. إعدادات الصفحة
st.set_page_config(page_title="Multi-User Lab System", page_icon="🔬", layout="wide")

# 2. إدارة المستخدمين والملفات
# كل مستخدم سيكون له ملف خاص باسمه (رمز دخوله)
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# 3. واجهة الدخول المنعزلة
def login_page():
    st.markdown("""
        <style>
        .stApp { background: #0f172a; }
        .login-card {
            background: #1e293b;
            padding: 40px;
            border-radius: 20px;
            border: 1px solid #334155;
            text-align: center;
            color: white;
            margin-top: 50px;
        }
        </style>
        <div class="login-card">
            <h1>🔬 نظام المختبرات المشترك</h1>
            <p>أدخل رمزك الخاص للوصول لبياناتك المنعزلة</p>
        </div>
    """, unsafe_allow_html=True)
    
    _, col, _ = st.columns([1,1,1])
    with col:
        # هنا الرمز هو نفسه "اسم المستخدم" الذي يحدد ملف البيانات
        user_code = st.text_input("رمز الدخول (User Code)", type="password", placeholder="مثلاً: user01")
        if st.button("دخول للنظام الشخصي", use_container_width=True):
            if user_code: # نتحقق أن الحقل ليس فارغاً
                st.session_state.user_id = user_code
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("يرجى إدخال رمز الوصول")

if not st.session_state.authenticated:
    login_page()
else:
    # --- إعداد مسار البيانات الخاص بهذا المستخدم فقط ---
    USER_DB = f"db_{st.session_state.user_id}.csv"
    
    # تحميل بيانات المستخدم الحالي فقط
    if 'df' not in st.session_state:
        if os.path.exists(USER_DB):
            st.session_state.df = pd.read_csv(USER_DB)
        else:
            st.session_state.df = pd.DataFrame(columns=["التاريخ", "المريض", "الفحص", "النتيجة", "الهاتف"])

    # واجهة البرنامج
    st.markdown(f"""
        <style>
        .stApp {{ background-color: #f8fafc !important; }}
        .user-header {{
            background: white; padding: 20px; border-radius: 15px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05); margin-bottom: 20px;
            border-right: 5px solid #2563eb;
        }}
        </style>
        <div class="user-header">
            <h2 style="margin:0;">👤 مساحة العمل: {st.session_state.user_id}</h2>
            <p style="color: #64748b; margin:0;">هذه البيانات خاصة بك ولا يمكن للمستخدمين الآخرين رؤيتها.</p>
        </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.info(f"المستخدم الحالي: {st.session_state.user_id}")
        if st.button("تسجيل الخروج (تبديل المستخدم)"):
            # تفريغ الجلسة عند الخروج لضمان الأمان
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    # التبويبات
    t1, t2 = st.tabs(["📝 إدخال البيانات", "📂 سجلاتي الخاصة"])

    with t1:
        st.markdown("### ✍️ إضافة فحص جديد")
        with st.form("user_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            name = c1.text_input("اسم المريض")
            test = c1.selectbox("الفحص", ["CBC", "Glucose", "Urea"])
            res = c2.number_input("النتيجة", format="%.2f")
            phone = c2.text_input("الهاتف")
            
            if st.form_submit_button("حفظ في قاعدة بياناتي"):
                new_data = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), name, test, res, phone]], 
                                      columns=st.session_state.df.columns)
                st.session_state.df = pd.concat([st.session_state.df, new_data], ignore_index=True)
                # الحفظ في الملف الخاص بالمستخدم فقط
                st.session_state.df.to_csv(USER_DB, index=False)
                st.toast(f"تم الحفظ في ملف {USER_DB}")

    with t2:
        st.markdown(f"### 📊 أرشيف المستخدم: {st.session_state.user_id}")
        if not st.session_state.df.empty:
            st.dataframe(st.session_state.df, use_container_width=True)
            
            # ميزة حذف السجلات (تؤثر فقط على ملف المستخدم)
            if st.button("مسح كافة سجلاتي نهائياً"):
                if os.path.exists(USER_DB):
                    os.remove(USER_DB)
                st.session_state.df = pd.DataFrame(columns=st.session_state.df.columns)
                st.rerun()
        else:
            st.warning("لا توجد بيانات في حسابك حالياً.")
