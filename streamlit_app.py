import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. إعدادات ثابتة جداً للأداء العالي
st.set_page_config(page_title="Lab System v33", layout="wide")

# 2. الحل الجذري لمنع إعادة التحميل (JavaScript + CSS)
# هذا الكود يمنع المتصفح من الاستجابة لإيماءات السحب للتحديث
st.markdown("""
    <script>
    // تعطيل السحب للتحديث برمجياً
    document.body.style.overscrollBehaviorY = 'contain';
    document.documentElement.style.overscrollBehaviorY = 'contain';
    </script>
    
    <style>
    /* تعطيل التحديث بالسحب عبر CSS */
    html, body, [data-testid="stAppViewContainer"] {
        overscroll-behavior-y: contain !important;
        overflow-y: auto !important;
        position: fixed;
        width: 100%;
        height: 100%;
    }
    
    /* جعل منطقة المحتوى قابلة للتمرير الداخلي فقط لمنع اهتزاز الصفحة */
    .main {
        overflow-y: auto !important;
        -webkit-overflow-scrolling: touch;
        height: 100vh;
    }

    /* إخفاء أي عناصر تسبب بطء في المعالجة */
    #stDecoration, header { display: none !important; }
    
    /* تبسيط الألوان لزيادة سرعة الاستجابة */
    .stApp { background-color: #f4f7f6; direction: rtl; }
    
    /* تكبير الحقول لتناسب اللمس السريع */
    input { font-size: 18px !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. إدارة البيانات (مبسطة جداً للسلاسة)
DB_FILE = "lab_pro_v33.csv"
SETTINGS_FILE = "settings.csv"

def get_lab_name():
    if os.path.exists(SETTINGS_FILE):
        return pd.read_csv(SETTINGS_FILE)['lab_name'].iloc[0]
    return "مختبر التحليلات الذكي"

if 'lab_name' not in st.session_state:
    st.session_state.lab_name = get_lab_name()

if 'df' not in st.session_state:
    st.session_state.df = pd.read_csv(DB_FILE) if os.path.exists(DB_FILE) else pd.DataFrame(columns=["التاريخ", "المريض", "الفحص", "النتيجة", "الهاتف"])

# 4. الواجهة البرمجية (قائمة جانبية بدلاً من التبويبات لزيادة الثبات)
menu = ["تسجيل فحص", "عرض تقرير", "إعدادات المختبر"]
choice = st.sidebar.radio("القائمة الرئيسية", menu)

st.header(f"🔬 {st.session_state.lab_name}")

# --- الخيار 1: تسجيل فحص ---
if choice == "تسجيل فحص":
    with st.form("my_form"):
        name = st.text_input("اسم المريض")
        phone = st.text_input("رقم الهاتف")
        test = st.selectbox("نوع الفحص", ["Glucose", "CBC", "HbA1c", "Urea"])
        res = st.number_input("النتيجة", step=0.1)
        
        if st.form_submit_button("حفظ النتيجة"):
            if name:
                new_data = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), name, test, res, phone]], columns=st.session_state.df.columns)
                st.session_state.df = pd.concat([st.session_state.df, new_data], ignore_index=True)
                st.session_state.df.to_csv(DB_FILE, index=False)
                st.toast("✅ تم الحفظ بنجاح")
            else:
                st.error("يرجى كتابة الاسم")

# --- الخيار 2: عرض تقرير ---
elif choice == "عرض تقرير":
    if not st.session_state.df.empty:
        p_list = st.session_state.df['المريض'].unique()
        selected_p = st.selectbox("اختر اسم المريض", p_list)
        row = st.session_state.df[st.session_state.df['المريض'] == selected_p].iloc[-1]
        
        st.markdown(f"""
        <div style="background:white; padding:20px; border-radius:10px; border:2px solid #000;">
            <h2 style="text-align:center;">{st.session_state.lab_name}</h2>
            <hr>
            <p><b>الاسم:</b> {row['المريض']}</p>
            <p><b>الفحص:</b> {row['الفحص']}</p>
            <p style="color:red; font-size:24px;"><b>النتيجة:</b> {row['النتيجة']}</p>
            <p><b>التاريخ:</b> {row['التاريخ']}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("لا توجد بيانات")

# --- الخيار 3: الإعدادات ---
elif choice == "إعدادات المختبر":
    new_name = st.text_input("تغيير اسم المختبر:", value=st.session_state.lab_name)
    if st.button("تحديث"):
        pd.DataFrame({'lab_name': [new_name]}).to_csv(SETTINGS_FILE, index=False)
        st.session_state.lab_name = new_name
        st.rerun()
