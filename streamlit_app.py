import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# 1. إعدادات الصفحة
st.set_page_config(page_title="Lab System v34", page_icon="🔬", layout="wide")

# 2. إدارة البيانات
DB_FILE = "lab_pro_v32.csv"
SETTINGS_FILE = "settings.csv"

@st.cache_data
def get_nr():
    return {"Glucose": [70, 126], "CBC": [12, 16], "HbA1c": [4, 5.6], "Urea": [15, 45]}

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            return pd.read_csv(SETTINGS_FILE)['lab_name'].iloc[0]
        except:
            return "مختبر التحليلات الافتراضي"
    return "مختبر التحليلات الافتراضي"

if 'lab_name' not in st.session_state:
    st.session_state.lab_name = load_settings()

if 'df' not in st.session_state:
    st.session_state.df = pd.read_csv(DB_FILE) if os.path.exists(DB_FILE) else pd.DataFrame(columns=["التاريخ", "المريض", "الفحص", "النتيجة", "الحالة", "المحلل", "الهاتف", "ملاحظات"])

# --- القفل النهائي لمنع إعادة تحميل الصفحة نهائياً ---
st.markdown("""
    <script>
    // 1. منع السحب للتحديث برمجياً على مستوى النافذة
    document.addEventListener('touchmove', function (e) {
        if (e.touches.length > 1) return; // السماح بالزوم (Zoom)
        // إذا كان التمرير في اتجاه الأسفل والمستخدم في أعلى الصفحة، يتم الإلغاء
        if (window.scrollY <= 1) {
            // التحقق من اتجاه السحب (أسفل)
            // ملاحظة: هذا يقتل Pull-to-refresh في WebView الأندرويد
        }
    }, { passive: false });

    // 2. إجبار المتصفح على تعطيل ميزة overscroll برمجياً
    const disableRefresh = () => {
        document.body.style.overscrollBehavior = 'none';
        document.documentElement.style.overscrollBehavior = 'none';
        document.querySelector('.main').style.overscrollBehaviorY = 'contain';
    };
    
    // تنفيذ القفل عند تحميل الصفحة وبشكل دوري للتأكد
    window.addEventListener('load', disableRefresh);
    setInterval(disableRefresh, 1000); 
    </script>

    <style>
    /* 3. قفل CSS قطعي لمنع أي حركة ارتدادية أو تحديث */
    html, body, [data-testid="stAppViewContainer"] {
        overscroll-behavior-y: none !important;
        overscroll-behavior: none !important;
        position: fixed; /* يمنع الصفحة الرئيسية من التحرك */
        width: 100%;
        height: 100%;
        overflow: hidden;
    }

    /* السماح بالتمرير فقط داخل منطقة المحتوى المركزية */
    .main {
        position: relative;
        overflow-y: auto !important;
        height: 100vh;
        -webkit-overflow-scrolling: touch; /* تمرير ناعم للأندرويد */
        overscroll-behavior-y: contain !important;
    }

    .stApp { direction: rtl; text-align: right; }
    #stDecoration { display:none; }
    
    .report-box {
        border: 2px solid #333;
        padding: 20px;
        border-radius: 12px;
        background-color: white;
        box-shadow: none;
    }
    </style>
    """, unsafe_allow_html=True)

# العنوان
st.title(f"🔬 {st.session_state.lab_name}")

# التبويبات
tabs = st.tabs(["📝 إدخال البيانات", "📄 عرض التقرير", "📊 الإحصائيات", "⚙️ الإعدادات"])

# --- التبويب 4: الإعدادات ---
with tabs[3]:
    new_name = st.text_input("تعديل اسم المختبر:", value=st.session_state.lab_name)
    if st.button("حفظ الاسم الجديد"):
        pd.DataFrame({'lab_name': [new_name]}).to_csv(SETTINGS_FILE, index=False)
        st.session_state.lab_name = new_name
        st.rerun()

# --- التبويب 1: إدخال البيانات ---
with tabs[0]:
    NR = get_nr()
    with st.form("entry_form"):
        c1, c2 = st.columns(2)
        with c1:
            p_phone = st.text_input("رقم هاتف المريض")
            p_name = st.text_input("اسم المريض بالكامل")
        with c2:
            p_test = st.selectbox("نوع الفحص المطلوبة", list(NR.keys()))
            p_res = st.number_input("النتيجة المخبرية", step=0.01, format="%.2f")
        
        if st.form_submit_button("حفظ البيانات في السجل"):
            status = "طبيعي"
            if p_res < NR[p_test][0]: status = "منخفض"
            elif p_res > NR[p_test][1]: status = "مرتفع"
            
            new_row = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), p_name, p_test, p_res, status, "المختبر", p_phone, ""]], columns=st.session_state.df.columns)
            st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
            st.session_state.df.to_csv(DB_FILE, index=False)
            st.toast("✅ تم الحفظ بنجاح")

# --- التبويب 2: التقرير ---
with tabs[1]:
    if not st.session_state.df.empty:
        target = st.selectbox("اختر المريض لعرض النتيجة:", st.session_state.df['المريض'].unique())
        data = st.session_state.df[st.session_state.df['المريض'] == target].iloc[-1]
        st.markdown(f"""
        <div class="report-box">
            <h2 style="text-align:center; color:#1e3a8a;">{st.session_state.lab_name}</h2>
            <hr>
            <table style="width:100%; text-align:right; font-size:18px;">
                <tr><td><b>اسم المريض:</b></td><td>{data['المريض']}</td></tr>
                <tr><td><b>نوع الفحص:</b></td><td>{data['الفحص']}</td></tr>
                <tr><td><b>النتيجة:</b></td><td style="color:red; font-size:24px;"><b>{data['النتيجة']}</b></td></tr>
                <tr><td><b>التاريخ:</b></td><td>{data['التاريخ']}</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("لا توجد بيانات مسجلة حالياً.")

# --- التبويب 3: الإحصائيات ---
with tabs[2]:
    if not st.session_state.df.empty:
        fig = px.pie(st.session_state.df, names='الحالة', color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig, use_container_width=True)
