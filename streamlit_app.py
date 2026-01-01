import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# 1. إعدادات الصفحة
st.set_page_config(page_title="Lab System v32", page_icon="🔬", layout="wide")

# 2. إدارة البيانات
DB_FILE = "lab_pro_v32.csv"
SETTINGS_FILE = "settings.csv"

@st.cache_data
def get_nr():
    return {"Glucose": [70, 126], "CBC": [12, 16], "HbA1c": [4, 5.6], "Urea": [15, 45]}

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        return pd.read_csv(SETTINGS_FILE)['lab_name'].iloc[0]
    return "مختبر التحليلات الافتراضي"

if 'lab_name' not in st.session_state:
    st.session_state.lab_name = load_settings()

if 'df' not in st.session_state:
    st.session_state.df = pd.read_csv(DB_FILE) if os.path.exists(DB_FILE) else pd.DataFrame(columns=["التاريخ", "المريض", "الفحص", "النتيجة", "الحالة", "المحلل", "الهاتف", "ملاحظات"])

# --- التعديل النهائي والقطعي لإلغاء إعادة تحميل الصفحة ---
st.markdown("""
    <script>
    // 1. تعطيل إيماءة السحب للتحديث برمجياً
    document.body.style.overscrollBehaviorY = 'none';
    document.documentElement.style.overscrollBehaviorY = 'none';

    // 2. منع المتصفح من تنفيذ عملية التحديث عند محاولة السحب للأسفل
    window.addEventListener('load', function() {
        var lastTouchY = 0;
        var preventPullToRefresh = false;

        document.addEventListener('touchstart', function(e) {
            if (e.touches.length !== 1) return;
            lastTouchY = e.touches[0].clientY;
            // التحقق مما إذا كان المستخدم في أعلى الصفحة
            preventPullToRefresh = window.pageYOffset === 0;
        }, {passive: false});

        document.addEventListener('touchmove', function(e) {
            var touchY = e.touches[0].clientY;
            var touchDiff = touchY - lastTouchY;
            lastTouchY = touchY;

            if (preventPullToRefresh && touchDiff > 0) {
                // إذا كان يحاول السحب للأسفل وهو في القمة، نمنعه نهائياً
                e.preventDefault();
            }
        }, {passive: false});
    });
    </script>

    <style>
    /* 3. إلغاء خاصية التحديث عبر CSS بشكل قطعي لكافة الحاويات */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        overscroll-behavior-y: none !important;
        overscroll-behavior: none !important;
        -webkit-overflow-scrolling: auto !important; /* تعطيل التمرير المطاطي */
    }

    /* ضمان سلاسة التمرير الداخلي فقط دون التأثير على الصفحة الأم */
    .main {
        overflow-y: auto !important;
        overscroll-behavior-y: contain !important;
    }

    .stApp {
        direction: rtl;
        text-align: right;
    }

    #stDecoration { display:none; }
    
    .report-box {
        border: 1px solid #ddd;
        padding: 15px;
        border-radius: 12px;
        background-color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# العنوان
st.title(f"🔬 {st.session_state.lab_name}")

# التبويبات
tabs = st.tabs(["📝 الإدخال", "📄 التقرير", "📊 الإحصائيات", "⚙️ الإعدادات"])

# --- التبويب 4: الإعدادات ---
with tabs[3]:
    new_name = st.text_input("اسم المختبر:", value=st.session_state.lab_name)
    if st.button("حفظ الاسم"):
        pd.DataFrame({'lab_name': [new_name]}).to_csv(SETTINGS_FILE, index=False)
        st.session_state.lab_name = new_name
        st.rerun()

# --- التبويب 1: إدخال البيانات ---
with tabs[0]:
    NR = get_nr()
    with st.form("entry_form"):
        c1, c2 = st.columns(2)
        with c1:
            p_phone = st.text_input("الهاتف")
            p_name = st.text_input("الاسم")
        with c2:
            p_test = st.selectbox("الفحص", list(NR.keys()))
            p_res = st.number_input("النتيجة", step=0.1)
        
        if st.form_submit_button("حفظ"):
            status = "طبيعي"
            if p_res < NR[p_test][0]: status = "منخفض"
            elif p_res > NR[p_test][1]: status = "مرتفع"
            
            new_row = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), p_name, p_test, p_res, status, "المحلل", p_phone, ""]], columns=st.session_state.df.columns)
            st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
            st.session_state.df.to_csv(DB_FILE, index=False)
            st.toast("تم الحفظ!")

# --- التبويب 2: التقرير ---
with tabs[1]:
    if not st.session_state.df.empty:
        target = st.selectbox("اختيار مريض:", st.session_state.df['المريض'].unique())
        data = st.session_state.df[st.session_state.df['المريض'] == target].iloc[-1]
        st.markdown(f'<div class="report-box"><h3>{st.session_state.lab_name}</h3><hr><p>الاسم: {data["المريض"]}</p><p>النتيجة: {data["النتيجة"]}</p></div>', unsafe_allow_html=True)

# --- التبويب 3: الإحصائيات ---
with tabs[2]:
    if not st.session_state.df.empty:
        fig = px.pie(st.session_state.df, names='الحالة')
        st.plotly_chart(fig, use_container_width=True)
