import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime, timedelta
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
    
    .patient-info-box {
        background: #f8fafc; border: 1px solid #e2e8f0; padding: 25px;
        border-radius: 20px; border-left: 8px solid #1e40af; margin-bottom: 25px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .info-label { font-weight: bold; color: #1e40af; margin-left: 5px; }
    
    .stability-badge {
        font-size: 0.8em; padding: 2px 8px; border-radius: 10px; font-weight: bold;
    }
    .expired { background: #fee2e2; color: #dc2626; border: 1px solid #dc2626; }
    .fresh { background: #dcfce7; color: #16a34a; border: 1px solid #16a34a; }

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
    "SYSTEM_VERSION": "v19.0 Ultimate Comprehensive Edition",
    "LICENSE_KEY": "PREMIUM-2026-X"
}

# --- 3. الموسوعة الطبية الشاملة (ثوابت النظام) ---
LAB_CATALOG = {
    "Hematology (أمراض الدم)": {
        "DefaultTube": "Purple (EDTA) 🟣", "Stability": 24,
        "Tests": {
            "CBC": (12, 16, "g/dL", 15), "HGB": (12, 18, "g/dL", 10), "PLT": (150, 450, "10^3/uL", 12),
            "WBC": (4, 11, "10^3/uL", 10), "ESR": (0, 20, "mm/hr", 8), "PCV": (37, 52, "%", 10),
            "PT": (11, 13.5, "sec", 15), "PTT": (25, 35, "sec", 15), "Blood Group": (0, 0, "Type", 5)
        }
    },
    "Biochemistry (الكيمياء الحيوية)": {
        "DefaultTube": "Yellow (Gel) 🟡", "Stability": 48,
        "Tests": {
            "Glucose (Fasting)": (70, 100, "mg/dL", 5), "HbA1c": (4, 5.6, "%", 25), "Urea": (15, 45, "mg/dL", 10),
            "Creatinine": (0.6, 1.2, "mg/dL", 15), "Albumin": (3.4, 5.4, "g/dL", 12), "Total Protein": (6.4, 8.3, "g/dL", 10),
            "S.Cholesterol": (125, 200, "mg/dL", 15), "Triglycerides": (50, 150, "mg/dL", 15), "Uric Acid": (3.5, 7.2, "mg/dL", 10)
        }
    },
    "Liver Function (وظائف الكبد)": {
        "DefaultTube": "Yellow (Gel) 🟡", "Stability": 24,
        "Tests": {
            "ALT (GPT)": (7, 56, "U/L", 12), "AST (GOT)": (10, 40, "U/L", 12), "ALP": (44, 147, "U/L", 15),
            "Total Bilirubin": (0.1, 1.2, "mg/dL", 10), "Direct Bilirubin": (0, 0.3, "mg/dL", 10)
        }
    },
    "Hormones & Vitamins": {
        "DefaultTube": "Red (Plain) 🔴", "Stability": 72,
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
    return {"lab_name": OWNER_INFO["PERMANENT_LAB_NAME"], "doc_name": OWNER_INFO["PERMANENT_DOC_NAME"], "title": "مدير المختبر", "currency": "$", "daily_target": 1000}

def get_result_analysis(cat, test, val):
    data = LAB_CATALOG[cat]["Tests"][test]
    low, high, unit, price = data
    if low == 0 and high == 0: return "طبيعي 🟢", "normal-green"
    if val < low: return "منخفض 🔵", "critical-red"
    if val > high: return "مرتفع 🔴", "critical-red"
    return "طبيعي 🟢", "normal-green"

def check_stability(timestamp_str, category):
    try:
        draw_time = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M")
        stability_hours = LAB_CATALOG[category]["Stability"]
        expiry_time = draw_time + timedelta(hours=stability_hours)
        remaining = expiry_time - datetime.now()
        if remaining.total_seconds() <= 0: return "منتهية (Expired) ❌", "expired"
        return f"صالحة لمدة {int(remaining.total_seconds() // 3600)} ساعة ✅", "fresh"
    except: return "غير محدد", ""

# --- 5. منطق واجهة المستخدم الرئيسي ---
if 'user_code' not in st.session_state: st.session_state.user_code = None

if st.session_state.user_code is None:
    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        st.markdown("<br><h1 style='text-align:center;'>🧬 BioLab Intelligence</h1>", unsafe_allow_html=True)
        code_input = st.text_input("أدخل رمز الوصول الخاص بك", type="password")
        if st.button("فتح النظام الآمن", use_container_width=True, type="primary"):
            st.session_state.user_code = code_input; st.rerun()
else:
    profile = load_user_profile()
    db_path, inv_path = get_file_path("csv"), get_file_path("inv.csv")
    
    # أعمدة قاعدة البيانات الكاملة لضمان عدم ضياع أي معلومة
    db_cols = ["PID", "Date", "Timestamp", "Patient", "Age", "Gender", "Category", "Test", "Result", "Unit", "Status", "Price", "Tube", "LabName", "DoctorName"]
    df = pd.read_csv(db_path) if os.path.exists(db_path) else pd.DataFrame(columns=db_cols)
    inv_df = pd.read_csv(inv_path) if os.path.exists(inv_path) else pd.DataFrame(columns=["Item", "Stock", "Expiry", "Unit"])

    st.markdown(f"""
        <div class="header-style">
            <div style="display:flex; justify-content:space-between;">
                <div><h1>{profile['lab_name']}</h1><p>{profile['doc_name']} | {profile.get('title', 'مدير المختبر')}</p></div>
                <div style="text-align:right;"><h3>{datetime.now().strftime('%Y-%m-%d')}</h3><code>ID: {st.session_state.user_code}</code></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    tabs = st.tabs(["📊 الإحصائيات", "🧪 تسجيل فحص", "👤 معلومات المريض", "📂 الأرشيف", "📄 التقارير", "📦 المخزون", "🧠 تحليل AI", "💰 المالية", "⚙️ الإعدادات"])

    with tabs[0]: # الإحصائيات والتحليل
        c1, c2, c3, c4 = st.columns(4)
        today_income = df[df['Date'] == datetime.now().strftime("%Y-%m-%d")]['Price'].sum()
        c1.metric("إجمالي المرضى", len(df['Patient'].unique()))
        c2.metric("فحوصات اليوم", len(df[df['Date'] == datetime.now().strftime("%Y-%m-%d")]))
        c3.metric("إجمالي الأرباح", f"{profile['currency']}{df['Price'].sum():,.0f}")
        c4.metric("نواقص المخزن", len(inv_df[inv_df['Stock'] < 5]) if not inv_df.empty else 0)
        
        st.write(f"📈 **الهدف المالي اليومي ({profile['currency']}{today_income} / {profile.get('daily_target', 1000)})**")
        st.progress(min(today_income / profile.get('daily_target', 1000), 1.0))
        if not df.empty: st.plotly_chart(px.line(df.groupby('Date').sum(numeric_only=True).reset_index(), x='Date', y='Price', title="النمو المالي"), use_container_width=True)

    with tabs[1]: # تسجيل فحص مع كافة البيانات الجديدة
        with st.form("entry_form", clear_on_submit=True):
            col_a, col_b, col_c = st.columns([2, 1, 1])
            p_name = col_a.text_input("اسم المريض بالكامل")
            p_age = col_b.number_input("العمر", 1, 120, 25)
            p_gender = col_c.selectbox("الجنس", ["ذكر", "أنثى"])
            
            p_id = st.text_input("كود المريض (PID)", value=datetime.now().strftime("%H%M%S"))
            
            col_d, col_e = st.columns(2)
            cat_sel = col_d.selectbox("القسم", list(LAB_CATALOG.keys()))
            test_sel = col_e.selectbox("التحليل", list(LAB_CATALOG[cat_sel]["Tests"].keys()))
            
            default_tube = LAB_CATALOG[cat_sel]["DefaultTube"]
            tube_sel = st.selectbox("نوع الأنبوب (Tube)", TUBE_TYPES, index=TUBE_TYPES.index(default_tube))
            res_val = st.number_input(f"النتيجة ({LAB_CATALOG[cat_sel]['Tests'][test_sel][2]})", format="%.2f")
            
            if st.form_submit_button("اعتماد وحفظ البيانات 🚀", use_container_width=True):
                if p_name:
                    status, _ = get_result_analysis(cat_sel, test_sel, res_val)
                    current_ts = datetime.now().strftime("%Y-%m-%d %H:%M")
                    
                    # خصم المخزن
                    if not inv_df.empty and test_sel in inv_df['Item'].values:
                        idx = inv_df[inv_df['Item'] == test_sel].index[0]
                        if inv_df.at[idx, 'Stock'] > 0: inv_df.at[idx, 'Stock'] -= 1
                        inv_df.to_csv(inv_path, index=False)

                    new_row = [p_id, datetime.now().strftime("%Y-%m-%d"), current_ts, p_name, p_age, p_gender, cat_sel, test_sel, res_val, LAB_CATALOG[cat_sel]["Tests"][test_sel][2], status, LAB_CATALOG[cat_sel]["Tests"][test_sel][3], tube_sel, profile['lab_name'], profile['doc_name']]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=df.columns)], ignore_index=True)
                    df.to_csv(db_path, index=False)
                    st.success(f"تم تسجيل {test_sel} للمريض {p_name}")
                else: st.error("يجب إدخال اسم المريض")

    with tabs[2]: # معلومات المريض (الجديد كلياً والشامل)
        st.subheader("👤 ملف المريض الرقمي")
        if not df.empty:
            p_search = st.selectbox("اختر المريض لاستعراض بياناته", df['Patient'].unique())
            p_data = df[df['Patient'] == p_search]
            p_latest = p_data.iloc[-1]
            
            st.markdown(f"""
                <div class="patient-info-box">
                    <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px;">
                        <div><span class="info-label">الاسم:</span> {p_latest['Patient']}</div>
                        <div><span class="info-label">العمر:</span> {p_latest['Age']}</div>
                        <div><span class="info-label">الجنس:</span> {p_latest['Gender']}</div>
                        <div><span class="info-label">المختبر:</span> {p_latest['LabName']}</div>
                        <div><span class="info-label">الطبيب:</span> {p_latest['DoctorName']}</div>
                        <div><span class="info-label">التاريخ:</span> {p_latest['Date']}</div>
                        <div><span class="info-label">آخر تحديث:</span> {p_latest['Timestamp']}</div>
                        <div><span class="info-label">رقم الملف:</span> {p_latest['PID']}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            st.write("🔬 **تاريخ التحاليل:**")
            st.dataframe(p_data[['Test', 'Result', 'Unit', 'Status', 'Timestamp']], use_container_width=True)
        else: st.info("لا توجد بيانات مرضى حالياً")

    with tabs[3]: # الأرشيف
        search = st.text_input("🔍 بحث سريـع في الأرشيف...")
        f_df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)] if search else df
        for idx, row in f_df.iloc[::-1].iterrows():
            _, style = get_result_analysis(row['Category'], row['Test'], row['Result'])
            stab_text, stab_class = check_stability(row['Timestamp'], row['Category'])
            st.markdown(f"""<div class="status-card {style}"><div style="display:flex; justify-content:space-between;"><b>👤 {row['Patient']} ({row['Age']} سنة)</b><span class="stability-badge {stab_class}">{stab_text}</span></div>{row['Test']}: {row['Result']} {row['Unit']} | {row['Timestamp']}</div>""", unsafe_allow_html=True)

    with tabs[4]: # التقارير
        if not df.empty:
            target = st.selectbox("اختر المريض للتقرير", df['Patient'].unique(), key="rep")
            if st.button("توليد التقرير الطبي"):
                st.markdown(f"### {profile['lab_name']} - تقرير طبي")
                st.table(df[df['Patient'] == target][['Test', 'Result', 'Unit', 'Status', 'Date']])

    with tabs[5]: # المخزن
        st.subheader("📦 إدارة المخزون")
        col_i1, col_i2 = st.columns([1, 2])
        with col_i1:
            with st.form("add_inv"):
                item = st.selectbox("المادة", [t for cat in LAB_CATALOG.values() for t in cat["Tests"].keys()])
                qty = st.number_input("الكمية", 1)
                exp = st.date_input("الصلاحية")
                if st.form_submit_button("إضافة"):
                    new_inv = pd.DataFrame([[item, qty, str(exp), "Test"]], columns=inv_df.columns)
                    inv_df = pd.concat([inv_df, new_inv], ignore_index=True)
                    inv_df.to_csv(inv_path, index=False); st.rerun()
        with col_i2:
            if not inv_df.empty:
                for i, r in inv_df.iterrows():
                    c_x, c_y = st.columns([3, 1])
                    c_x.write(f"🧪 {r['Item']} - المخزون: {r['Stock']}")
                    if c_y.button("➖", key=f"m{i}"):
                        inv_df.at[i, 'Stock'] -= 1; inv_df.to_csv(inv_path, index=False); st.rerun()

    with tabs[6]: # تحليل AI
        st.subheader("🧠 نظام الإنذار المبكر AI")
        st.info("النظام يراقب استقرار العينات وجودة النتائج بناءً على التاريخ المرضي للمريض.")

    with tabs[7]: # المالية
        st.subheader("💰 السجل المالي")
        st.dataframe(df[["Date", "Patient", "Test", "Price", "Status"]], use_container_width=True)
        st.success(f"إجمالي الأرباح: {df['Price'].sum()} {profile['currency']}")

    with tabs[8]: # الإعدادات
        st.subheader("⚙️ الإعدادات العامة")
        n_l = st.text_input("اسم المختبر", profile['lab_name'])
        n_d = st.text_input("اسم الطبيب", profile['doc_name'])
        target_val = st.number_input("الهدف المالي اليومي", value=profile.get('daily_target', 1000))
        if st.button("حفظ الإعدادات"):
            profile.update({"lab_name": n_l, "doc_name": n_d, "daily_target": target_val})
            with open(get_file_path("json"), "w", encoding="utf-8") as f: json.dump(profile, f)
            st.success("تم التحديث!")
        if st.button("تسجيل الخروج"): st.session_state.user_code = None; st.rerun()

    st.markdown(f"<center style='opacity:0.2; margin-top:40px;'>{OWNER_INFO['SYSTEM_VERSION']}</center>", unsafe_allow_html=True)
