import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import io

# --- 1. هندسة الواجهة والمنع المطلق للتحديث ---
st.set_page_config(page_title="BioLab Intelligence Pro", page_icon="🧬", layout="wide")

st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] {
        overflow: hidden !important; position: fixed !important;
        width: 100% !important; height: 100% !important;
        overscroll-behavior: none !important; touch-action: none !important;
    }
    [data-testid="stMainViewContainer"] {
        overflow-y: auto !important; height: 100vh !important;
        -webkit-overflow-scrolling: touch !important;
        overscroll-behavior-y: contain !important;
    }
    .status-card {
        padding: 15px; border-radius: 12px; margin-bottom: 10px;
        border-right: 8px solid; transition: transform 0.3s;
    }
    .status-card:hover { transform: scale(1.01); }
    .critical-red { background: #fef2f2; border-right-color: #ef4444; color: #991b1b; }
    .warning-yellow { background: #fffbeb; border-right-color: #f59e0b; color: #92400e; }
    .normal-green { background: #f0fdf4; border-right-color: #10b981; color: #065f46; }
    
    .user-profile-box {
        background: rgba(255,255,255,0.1); padding: 10px; border-radius: 15px;
        border: 1px solid rgba(255,255,255,0.2); margin-top: 10px;
    }

    .header-style {
        background: linear-gradient(135deg, #0f172a 0%, #1e40af 100%);
        padding: 35px; border-radius: 25px; color: white;
        margin-bottom: 30px; box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    }
    header { visibility: hidden !important; }
    </style>
""", unsafe_allow_html=True)

# --- 2. نظام الهوية الثابتة ---
OWNER_INFO = {
    "PERMANENT_LAB_NAME": "مختبر النخبة التخصصي",
    "PERMANENT_DOC_NAME": "د. أحمد المصطفى",
    "SYSTEM_VERSION": "v15.0 Absolute Full Edition",
    "LICENSE_KEY": "PREMIUM-2026-X"
}

# --- 3. الموسوعة الطبية الشاملة (جميع التحاليل المذكورة سابقاً) ---
LAB_CATALOG = {
    "Hematology (أمراض الدم)": {
        "DefaultTube": "Purple (EDTA) 🟣",
        "Tests": {
            "CBC": (12, 16, "g/dL", 15), "HGB": (12, 18, "g/dL", 10), "PLT": (150, 450, "10^3/uL", 12),
            "WBC": (4, 11, "10^3/uL", 10), "ESR": (0, 20, "mm/hr", 8), "PCV": (37, 52, "%", 10),
            "PT": (11, 13.5, "sec", 15), "PTT": (25, 35, "sec", 15), "Blood Group": (0, 0, "Type", 5)
        }
    },
    "Biochemistry (الكيمياء الحيوية)": {
        "DefaultTube": "Yellow (Gel) 🟡",
        "Tests": {
            "Glucose (Fasting)": (70, 100, "mg/dL", 5), "HbA1c": (4, 5.6, "%", 25), "Urea": (15, 45, "mg/dL", 10),
            "Creatinine": (0.6, 1.2, "mg/dL", 15), "Albumin": (3.4, 5.4, "g/dL", 12), "Total Protein": (6.4, 8.3, "g/dL", 10),
            "S.Cholesterol": (125, 200, "mg/dL", 15), "Triglycerides": (50, 150, "mg/dL", 15), "Uric Acid": (3.5, 7.2, "mg/dL", 10)
        }
    },
    "Liver Function (وظائف الكبد)": {
        "DefaultTube": "Yellow (Gel) 🟡",
        "Tests": {
            "ALT (GPT)": (7, 56, "U/L", 12), "AST (GOT)": (10, 40, "U/L", 12), "ALP": (44, 147, "U/L", 15),
            "Total Bilirubin": (0.1, 1.2, "mg/dL", 10), "Direct Bilirubin": (0, 0.3, "mg/dL", 10)
        }
    },
    "Hormones & Vitamins": {
        "DefaultTube": "Red (Plain) 🔴",
        "Tests": {
            "TSH": (0.4, 4.0, "mIU/L", 30), "Vitamin D3": (30, 100, "ng/mL", 50), "Ferritin": (20, 250, "ng/mL", 25),
            "Vitamin B12": (200, 900, "pg/mL", 40), "Prolactin": (2, 29, "ng/mL", 35)
        }
    }
}

TUBE_TYPES = ["Purple (EDTA) 🟣", "Yellow (Gel) 🟡", "Red (Plain) 🔴", "Blue (Citrate) 🔵", "Green (Heparin) 🟢", "Grey (Fluoride) ⚪", "Black (ESR) ⚫"]

# --- 4. إدارة الملفات والبيانات ---
def get_file_path(extension):
    user_id = "".join(x for x in (st.session_state.get('user_code', 'default')) if x.isalnum())
    return f"biolab_data_{user_id}.{extension}"

def load_user_profile():
    path = get_file_path("json")
    if os.path.exists(path): return json.load(open(path, "r", encoding="utf-8"))
    return {"lab_name": OWNER_INFO["PERMANENT_LAB_NAME"], "doc_name": OWNER_INFO["PERMANENT_DOC_NAME"], "title": "مدير المختبر", "bio": "أخصائي تحليلات", "currency": "$", "joined": datetime.now().strftime("%Y-%m-%d")}

def get_result_analysis(cat, test, val):
    data = LAB_CATALOG[cat]["Tests"][test]
    low, high, unit, price = data
    if low == 0 and high == 0: return "طبيعي 🟢", "normal-green"
    if val < low: return "منخفض 🔵", "critical-red"
    if val > high: return "مرتفع 🔴", "critical-red"
    return "طبيعي 🟢", "normal-green"

# --- 5. منطق واجهة المستخدم الرئيسي ---
if 'user_code' not in st.session_state: st.session_state.user_code = None

if st.session_state.user_code is None:
    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        st.markdown("<br><h1 style='text-align:center;'>🧬 BioLab Intelligence</h1>", unsafe_allow_html=True)
        code_input = st.text_input("أدخل رمز الوصول الخاص بك", type="password")
        if st.button("فتح النظام الآمن", use_container_width=True, type="primary"):
            st.session_state.user_code = code_input
            st.rerun()
else:
    # تحميل كافة قواعد البيانات
    profile = load_user_profile()
    db_path, inv_path = get_file_path("csv"), get_file_path("inv.csv")
    
    df = pd.read_csv(db_path) if os.path.exists(db_path) else pd.DataFrame(columns=["PID", "Date", "Patient", "Category", "Test", "Result", "Unit", "Status", "Price", "Tube"])
    inv_df = pd.read_csv(inv_path) if os.path.exists(inv_path) else pd.DataFrame(columns=["Item", "Stock", "Expiry", "Unit"])

    # الهيدر الاحترافي
    st.markdown(f"""
        <div class="header-style">
            <div style="display:flex; justify-content:space-between;">
                <div><h1>{profile['lab_name']}</h1><p>{profile['doc_name']} | {profile['title']}</p></div>
                <div style="text-align:right;"><h3>{datetime.now().strftime('%Y-%m-%d')}</h3><code>ID: {st.session_state.user_code}</code></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    tabs = st.tabs(["📊 الإحصائيات", "🧪 تسجيل فحص", "📂 الأرشيف", "📄 التقارير", "📦 المخزون", "🧠 تحليل AI", "💰 المالية", "⚙️ الإعدادات"])

    with tabs[0]: # الإحصائيات
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("إجمالي المرضى", len(df['Patient'].unique()))
        c2.metric("فحوصات اليوم", len(df[df['Date'] == datetime.now().strftime("%Y-%m-%d")]))
        c3.metric("إجمالي الإيرادات", f"{profile['currency']}{df['Price'].sum():,.0f}")
        c4.metric("نواقص المخزن", len(inv_df[inv_df['Stock'] < 5]) if not inv_df.empty else 0)
        if not df.empty:
            st.plotly_chart(px.line(df.groupby('Date').sum(numeric_only=True).reset_index(), x='Date', y='Price', title="منحنى النمو المالي"), use_container_width=True)

    with tabs[1]: # تسجيل فحص
        with st.form("entry_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            p_name = col1.text_input("اسم المريض")
            p_id = col2.text_input("كود المريض (PID)", value=datetime.now().strftime("%H%M%S"))
            
            cat_sel = st.selectbox("القسم", list(LAB_CATALOG.keys()))
            test_sel = st.selectbox("التحليل", list(LAB_CATALOG[cat_sel]["Tests"].keys()))
            
            # زر اختيار نوع الأنبوب
            default_tube = LAB_CATALOG[cat_sel]["DefaultTube"]
            tube_sel = st.selectbox("نوع الأنبوب (Tube)", TUBE_TYPES, index=TUBE_TYPES.index(default_tube))
            
            res_val = st.number_input(f"النتيجة ({LAB_CATALOG[cat_sel]['Tests'][test_sel][2]})", format="%.2f")
            
            if st.form_submit_button("اعتماد وحفظ 🚀", use_container_width=True):
                if p_name:
                    status, _ = get_result_analysis(cat_sel, test_sel, res_val)
                    unit, price = LAB_CATALOG[cat_sel]["Tests"][test_sel][2], LAB_CATALOG[cat_sel]["Tests"][test_sel][3]
                    
                    # خصم المخزن تلقائي
                    if not inv_df.empty and test_sel in inv_df['Item'].values:
                        idx = inv_df[inv_df['Item'] == test_sel].index[0]
                        if inv_df.at[idx, 'Stock'] > 0: inv_df.at[idx, 'Stock'] -= 1
                        inv_df.to_csv(inv_path, index=False)

                    new_row = pd.DataFrame([[p_id, datetime.now().strftime("%Y-%m-%d"), p_name, cat_sel, test_sel, res_val, unit, status, price, tube_sel]], columns=df.columns)
                    df = pd.concat([df, new_row], ignore_index=True)
                    df.to_csv(db_path, index=False)
                    st.success(f"تم تسجيل {test_sel} بنجاح!")
                else: st.error("أدخل اسم المريض")

    with tabs[2]: # الأرشيف
        search = st.text_input("🔍 بحث سريـع في السجلات...")
        f_df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)] if search else df
        for idx, row in f_df.iloc[::-1].iterrows():
            _, style = get_result_analysis(row['Category'], row['Test'], row['Result'])
            st.markdown(f"""<div class="status-card {style}"><b>👤 {row['Patient']}</b> | {row['Test']}: {row['Result']} {row['Unit']} | الأنبوب: {row['Tube']}</div>""", unsafe_allow_html=True)

    with tabs[3]: # التقارير
        if not df.empty:
            target = st.selectbox("اختر المريض لإصدار تقريره", df['Patient'].unique())
            if st.button("توليد التقرير الطبي"):
                p_res = df[df['Patient'] == target]
                st.markdown(f"### تقرير مختبري: {profile['lab_name']}")
                st.write(f"المريض: {target} | التاريخ: {p_res.iloc[0]['Date']}")
                st.table(p_res[['Test', 'Result', 'Unit', 'Status']])

    with tabs[4]: # المخزن (مع التحكم اليدوي)
        st.subheader("📦 إدارة المحاليل والمستهلكات")
        col_inv1, col_inv2 = st.columns([1, 2])
        with col_inv1:
            with st.form("add_inv_manual"):
                st.write("إضافة مادة جديدة")
                item = st.selectbox("المادة", [t for cat in LAB_CATALOG.values() for t in cat["Tests"].keys()])
                qty = st.number_input("الكمية", min_value=1)
                exp = st.date_input("انتهاء الصلاحية")
                if st.form_submit_button("إضافة للمخزن"):
                    new_inv = pd.DataFrame([[item, qty, str(exp), "Test"]], columns=inv_df.columns)
                    inv_df = pd.concat([inv_df, new_inv], ignore_index=True)
                    inv_df.to_csv(inv_path, index=False)
                    st.rerun()
        with col_inv2:
            st.write("الجرد الحالي والتحكم اليدوي")
            if not inv_df.empty:
                for i, row in inv_df.iterrows():
                    c_i1, c_i2, c_i3, c_i4 = st.columns([2, 1, 1, 1])
                    c_i1.write(f"🧪 {row['Item']}")
                    c_i2.write(f"المخزون: **{row['Stock']}**")
                    if c_i3.button("➕", key=f"p{i}"):
                        inv_df.at[i, 'Stock'] += 1
                        inv_df.to_csv(inv_path, index=False); st.rerun()
                    if c_i4.button("➖", key=f"m{i}"):
                        if inv_df.at[i, 'Stock'] > 0:
                            inv_df.at[i, 'Stock'] -= 1
                            inv_df.to_csv(inv_path, index=False); st.rerun()
            else: st.info("المخزن فارغ")

    with tabs[5]: # تحليل AI
        st.subheader("🧠 نظام الإنذار المبكر (AI)")
        if not df.empty:
            p_ai = st.selectbox("اختر مريضاً للتحليل التنبؤي", df['Patient'].unique())
            p_data = df[df['Patient'] == p_ai]
            if len(p_data) > 1:
                st.plotly_chart(px.line(p_data, x="Date", y="Result", color="Test"))
            else: st.warning("نحتاج لأكثر من زيارة للتحليل.")

    with tabs[6]: # المالية
        st.subheader("💰 السجل المالي")
        st.dataframe(df[["Date", "Patient", "Test", "Price", "Status"]], use_container_width=True)
        st.write(f"**إجمالي الأرباح: {df['Price'].sum()} {profile['currency']}**")

    with tabs[7]: # الإعدادات
        st.subheader("⚙️ إعدادات الملف الشخصي")
        n_l = st.text_input("اسم المختبر", profile['lab_name'])
        n_d = st.text_input("اسم الطبيب", profile['doc_name'])
        n_t = st.text_input("المسمى الوظيفي", profile['title'])
        if st.button("حفظ التغييرات"):
            profile.update({"lab_name": n_l, "doc_name": n_d, "title": n_t})
            with open(get_file_path("json"), "w", encoding="utf-8") as f: json.dump(profile, f)
            st.success("تم الحفظ!")
            st.rerun()
        if st.button("تسجيل الخروج"):
            st.session_state.user_code = None
            st.rerun()

    st.markdown(f"<center style='opacity:0.2; margin-top:40px;'>{OWNER_INFO['SYSTEM_VERSION']}</center>", unsafe_allow_html=True)
