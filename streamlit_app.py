import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime
import plotly.express as px
import io

# --- 1. إعدادات المنصة (يجب أن تكون في البداية) ---
st.set_page_config(page_title="BioLab Ultra", page_icon="🧬", layout="wide")

# --- 2. محرك منع التحديث واللمس (الحل الجذري) ---
# هذا الكود يمنع المتصفح من استلام أوامر السحب لأسفل نهائياً
st.components.v1.html("""
    <script>
    // 1. منع السحب للتحديث (Pull-to-Refresh)
    document.body.style.overscrollBehavior = 'none';
    
    // 2. اعتراض حركة اللمس
    window.addEventListener('touchstart', function(e) {
        this.startY = e.touches[0].pageY;
    }, {passive: false});

    window.addEventListener('touchmove', function(e) {
        const moveY = e.touches[0].pageY;
        const scrollTop = document.documentElement.scrollTop || document.body.scrollTop;
        
        // إذا كان المستخدم يسحب لأسفل وهو في أعلى الصفحة، نقتل العملية فوراً
        if (scrollTop <= 0 && moveY > this.startY) {
            e.preventDefault();
        }
    }, {passive: false});

    // 3. منع الخروج من التطبيق عند السحب من الحواف (Back Gesture)
    history.pushState(null, null, location.href);
    window.onpopstate = function () {
        history.go(1);
    };
    </script>
""", height=0)

st.markdown("""
    <style>
    /* قفل كلي لأبعاد الشاشة */
    html, body, [data-testid="stAppViewContainer"] {
        overflow: hidden !important;
        position: fixed !important;
        width: 100vw !important;
        height: 100vh !important;
        overscroll-behavior-y: none !important;
        overscroll-behavior: none !important;
        touch-action: pan-x pan-y;
    }

    /* إنشاء حاوية تمرير داخلية محصنة */
    [data-testid="stMainViewContainer"] {
        overflow-y: auto !important;
        height: 100vh !important;
        -webkit-overflow-scrolling: touch;
        overscroll-behavior-y: contain !important;
    }

    /* تنسيق البطاقات */
    .patient-card {
        background: #ffffff; padding: 15px; border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 10px;
        border-right: 5px solid #1e3a8a; color: #1e293b;
    }
    
    /* إخفاء شريط الأدوات العلوي الذي يسبب الارتداد */
    header, footer { visibility: hidden !important; height: 0px !important; }
    </style>
""", unsafe_allow_html=True)

# --- 3. إدارة الجلسة والبيانات ---
if 'user_code' not in st.session_state: 
    st.session_state.user_code = None

def load_settings():
    safe_id = "".join(x for x in (st.session_state.user_code or "default") if x.isalnum())
    p = f"config_{safe_id}.json"
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8") as f: return json.load(f)
    return {"lab_name": "SmartLab Pro", "doctor_name": "Admin"}

# --- 4. شاشة الدخول ---
if st.session_state.user_code is None:
    _, col, _ = st.columns([0.1, 0.8, 0.1])
    with col:
        st.markdown("<br><br><center><img src='https://cdn-icons-png.flaticon.com/512/3063/3063205.png' width='100'></center>", unsafe_allow_html=True)
        st.title("BioLab Ultra")
        u = st.text_input("رمز الدخول", type="password")
        if st.button("فتح النظام آمن", use_container_width=True, type="primary"):
            st.session_state.user_code = u
            st.rerun()
else:
    # --- 5. التطبيق الرئيسي ---
    user_settings = load_settings()
    safe_id = "".join(x for x in st.session_state.user_code if x.isalnum())
    db_file = f"private_db_{safe_id}.csv"
    
    if 'df' not in st.session_state:
        st.session_state.df = pd.read_csv(db_file) if os.path.exists(db_file) else pd.DataFrame(columns=["ID", "التاريخ", "المريض", "الفحص", "النتيجة", "الحالة", "الهاتف"])

    st.markdown(f"""<div style="background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); padding:20px; border-radius:20px; color:white; margin-bottom:20px;">
        <h2 style="margin:0;">{user_settings.get('lab_name')}</h2><p style="margin:0; opacity:0.8;">بإشراف: د. {user_settings.get('doctor_name')}</p></div>""", unsafe_allow_html=True)

    t1, t2, t3, t4 = st.tabs(["📋 الأرشيف", "🧪 فحص جديد", "📊 الذكاء", "⚙️ الإعدادات"])

    with t1:
        search = st.text_input("🔍 بحث فوري...", key="search_main")
        filtered = st.session_state.df
        if search: filtered = filtered[filtered['المريض'].str.contains(search, na=False)]
        
        for i, r in filtered.iloc[::-1].head(15).iterrows():
            st.markdown(f'<div class="patient-card"><b>👤 {r["المريض"]}</b><br>{r["الفحص"]}: {r["النتيجة"]} <span style="float:left;">{r["الحالة"]}</span></div>', unsafe_allow_html=True)

    with t2:
        with st.form("add_form", clear_on_submit=True):
            n = st.text_input("اسم المريض")
            test = st.selectbox("نوع التحليل", ["CBC", "Glucose", "HbA1c", "Lipid Profile", "TSH", "Urea"])
            res = st.number_input("النتيجة", format="%.2f")
            if st.form_submit_button("حفظ السجل فوراً", use_container_width=True):
                if n:
                    new_entry = pd.DataFrame([[datetime.now().strftime("%H%M%S"), datetime.now().strftime("%Y-%m-%d"), n, test, res, "Normal", ""]], columns=st.session_state.df.columns)
                    st.session_state.df = pd.concat([st.session_state.df, new_entry], ignore_index=True)
                    st.session_state.df.to_csv(db_file, index=False)
                    st.toast("✅ تم الحفظ بنجاح")
                else: st.error("يرجى إدخال اسم المريض")

    with t4:
        if st.button("خروج من النظام 🚪", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    st.markdown("<p style='text-align:center; color:gray; font-size:10px; margin-top:20px;'>BioLab Ultra v3.0 - Anti-Refresh Secured</p>", unsafe_allow_html=True)
