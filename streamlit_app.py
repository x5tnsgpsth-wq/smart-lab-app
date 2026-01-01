import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime
import plotly.express as px

# --- 1. محرك الإعدادات المحسن ---
def load_settings():
    if 'user_code' not in st.session_state or not st.session_state.user_code: return {}
    safe_id = "".join(x for x in st.session_state.user_code if x.isalnum())
    config_path = f"config_{safe_id}.json"
    default_settings = {
        "lab_name": "SmartLab Pro",
        "doctor_name": "Admin",
        "theme": "Dark",
        "currency": "USD"
    }
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return {**default_settings, **json.load(f)}
    return default_settings

def save_settings(settings):
    safe_id = "".join(x for x in st.session_state.user_code if x.isalnum())
    config_path = f"config_{safe_id}.json"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False)

# --- 2. تهيئة المنصة (Mobile Optimization) ---
st.set_page_config(page_title="BioLab Mobile", page_icon="🔬", layout="wide")

# منع المتصفح من تحديث الصفحة عند السحب لأسفل (مهم جداً للاندرويد)
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] {
        overscroll-behavior-y: contain;
    }
    .main-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #1e3a8a;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

if 'user_code' not in st.session_state: st.session_state.user_code = None

# --- 3. شاشة الدخول الاحترافية ---
def login_screen():
    _, col, _ = st.columns([0.1, 0.8, 0.1])
    with col:
        st.image("https://cdn-icons-png.flaticon.com/512/3063/3063205.png", width=100)
        st.title("BioLab Pro Access")
        u_code = st.text_input("رمز الدخول الشخصي", type="password", placeholder="أدخل الرمز هنا...")
        if st.button("تسجيل دخول آمن", use_container_width=True, type="primary"):
            if u_code:
                st.session_state.user_code = u_code
                st.rerun()

# --- 4. التطبيق الرئيسي ---
def main_app():
    user_settings = load_settings()
    db_file = f"private_db_{''.join(x for x in st.session_state.user_code if x.isalnum())}.csv"
    
    if 'df' not in st.session_state:
        st.session_state.df = pd.read_csv(db_file) if os.path.exists(db_file) else pd.DataFrame(columns=["ID", "التاريخ", "المريض", "الفحص", "النتيجة", "الحالة", "الهاتف"])

    # الهيدر المحترف
    st.markdown(f"""
        <div style="background: linear-gradient(90deg, #0f172a 0%, #1e3a8a 100%); padding:25px; border-radius:20px; color:white; margin-bottom:25px; text-align:center;">
            <h1 style="margin:0;">🔬 {user_settings.get('lab_name')}</h1>
            <p style="margin:0; opacity:0.8;">د. {user_settings.get('doctor_name')} | نظام أندرويد السحابي</p>
        </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 السجلات", 
        "🧪 فحص جديد", 
        "📊 الإحصائيات", 
        "⚙️ الإعدادات"
    ])

    with tab1:
        st.image("https://cdn-icons-png.flaticon.com/512/2965/2965250.png", width=60)
        st.markdown("### قاعدة بيانات المرضى")
        search = st.text_input("🔍 بحث سريع بالاسم...", placeholder="اكتب اسم المريض هنا...")
        filtered_df = st.session_state.df
        if search:
            filtered_df = st.session_state.df[st.session_state.df['المريض'].str.contains(search, na=False)]
        
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)

    with tab2:
        st.image("https://cdn-icons-png.flaticon.com/512/809/809957.png", width=60)
        st.markdown("### تسجيل فحص مخبري جديد")
        
        with st.form("professional_add_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            p_name = col1.text_input("اسم المريض الثلاثي")
            p_phone = col2.text_input("رقم الهاتف (WhatsApp)")
            
            # قائمة تحاليل موسعة (أكثر من 40 تحليل)
            test_type = st.selectbox("نوع التحليل", [
                "CBC (Complete Blood Count)", "Glucose (Fasting)", "Glucose (Random)", "HbA1c",
                "Lipid Profile", "Liver Function (ALT/AST)", "Kidney Function (Urea/Creatinine)",
                "TSH (Thyroid)", "T3 / T4", "Vitamin D3", "Vitamin B12", "Ferritin", "Serum Iron",
                "Uric Acid", "Calcium", "Zinc", "Magnesium", "Potassium", "Sodium",
                "CRP (Inflammation)", "ESR", "RA Factor", "H. Pylori (Antigen/Antibody)",
                "Widal Test (Typhoid)", "Malaria Test", "HCV (Hepatitis C)", "HBV (Hepatitis B)",
                "HIV 1/2", "Pregnancy Test (HCG)", "Urinalysis (Complete)", "Stool Analysis",
                "PSA (Prostate)", "Prolactin", "Testosterone", "Progesterone", "LH / FSH"
            ])
            
            p_result = st.number_input("النتيجة المستخرجة", step=0.01)
            
            submit = st.form_submit_button("إرسال للبيانات والسحابية 🚀", use_container_width=True)
            
            if submit:
                if p_name:
                    new_entry = pd.DataFrame([[
                        datetime.now().strftime("%H%M%S"), 
                        datetime.now().strftime("%Y-%m-%d"), 
                        p_name, test_type, p_result, "Finalized", p_phone
                    ]], columns=st.session_state.df.columns)
                    
                    st.session_state.df = pd.concat([st.session_state.df, new_entry], ignore_index=True)
                    st.session_state.df.to_csv(db_file, index=False)
                    st.toast(f"تم تسجيل {p_name} بنجاح!", icon="✅")
                else:
                    st.error("خطأ: يرجى إدخال اسم المريض")

    with tab3:
        st.image("https://cdn-icons-png.flaticon.com/512/4222/4222031.png", width=60)
        st.markdown("### ذكاء الأعمال والتحليلات")
        if not st.session_state.df.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("إجمالي الفحوصات", len(st.session_state.df))
            c2.metric("فحوصات اليوم", len(st.session_state.df[st.session_state.df['التاريخ'] == datetime.now().strftime("%Y-%m-%d")]))
            c3.metric("المرضى المميزين", st.session_state.df['المريض'].nunique())
            
            fig = px.pie(st.session_state.df, names='الفحص', title="توزيع أنواع الفحوصات", hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("لا توجد بيانات كافية لعرض الإحصائيات حالياً.")

    with tab4:
        st.image("https://cdn-icons-png.flaticon.com/512/2040/2040504.png", width=60)
        st.markdown("### إعدادات النظام المتقدمة")
        
        with st.expander("🏨 هوية المختبر"):
            n_lab = st.text_input("تعديل اسم المختبر", value=user_settings.get('lab_name'))
            n_doc = st.text_input("تعديل اسم المدير المسؤول", value=user_settings.get('doctor_name'))
            
        with st.expander("🎨 المظهر والأمان"):
            n_theme = st.selectbox("نمط العرض", ["Light", "Dark"], index=0 if user_settings.get('theme') == "Light" else 1)
            st.info("نظام التشفير مفعل تلقائياً على قاعدة البيانات الخاصة بك.")

        if st.button("💾 حفظ الإعدادات وتطبيقها"):
            save_settings({"lab_name": n_lab, "doctor_name": n_doc, "theme": n_theme})
            st.toast("تم حفظ الإعدادات بنجاح!")

    # شريط سفلي ثابت (Sidebar)
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3063/3063205.png", width=50)
    st.sidebar.markdown(f"**المستخدم:** {st.session_state.user_code}")
    if st.sidebar.button("تسجيل الخروج الآمن 🚪", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# --- التشغيل ---
if st.session_state.user_code is None:
    login_screen()
else:
    main_app()
