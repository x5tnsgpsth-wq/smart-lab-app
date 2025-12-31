!pip install fpdf

import pandas as pd
import ipywidgets as widgets
from IPython.display import display, clear_output
from google.colab import files
from fpdf import FPDF

# DataFrame لتخزين النتائج
df = pd.DataFrame(columns=['اسم المريض', 'الاختبار', 'النتيجة', 'ملاحظات', 'الحالة'])

# مربعات نص لإدخال البيانات
patient_name = widgets.Text(description="اسم المريض:", layout=widgets.Layout(width='300px'))
test_name = widgets.Text(description="الاختبار:", layout=widgets.Layout(width='300px'))
result_value = widgets.FloatText(description="النتيجة:", layout=widgets.Layout(width='200px'))
notes = widgets.Text(description="ملاحظات:", layout=widgets.Layout(width='400px'))

# أزرار
add_button = widgets.Button(description="إضافة", button_style='success')
edit_index = widgets.IntText(description="رقم الصف:")
edit_field = widgets.Dropdown(options=['اسم المريض', 'الاختبار', 'النتيجة', 'ملاحظات'], description="حقل التعديل")
edit_value = widgets.Text(description="القيمة الجديدة")
edit_button = widgets.Button(description="تعديل", button_style='warning')
save_excel_button = widgets.Button(description="Excel", button_style='info')
save_pdf_button = widgets.Button(description="PDF", button_style='primary')
reset_button = widgets.Button(description="إعادة تعيين", button_style='danger')

# البحث وعدد النتائج
search_box = widgets.Text(description="بحث باسم المريض:")
total_label = widgets.Label(value="إجمالي النتائج: 0")
new_label = widgets.Label(value="جديدة: 0")
modified_label = widgets.Label(value="معدلة: 0")

# Output لعرض الجدول
output = widgets.Output()

# دالة لتلوين الجدول حسب الحالة
def color_table(df):
    def highlight(row):
        if row['الحالة'] == 'جديدة':
            return ['background-color: #b3ffb3']*len(row)
        elif row['الحالة'] == 'معدلة':
            return ['background-color: #ffff99']*len(row)
        else:
            return ['background-color: white']*len(row)
    return df.style.apply(highlight, axis=1).hide_columns(['الحالة'])

# تحديث الجدول وعدد النتائج لكل حالة
def update_table():
    with output:
        clear_output()
        display(color_table(df))
    total_label.value = f"إجمالي النتائج: {len(df)}"
    new_label.value = f"جديدة: {len(df[df['الحالة']=='جديدة'])}"
    modified_label.value = f"معدلة: {len(df[df['الحالة']=='معدلة'])}"

# إضافة نتيجة
def add_result(b):
    global df
    new_data = pd.DataFrame([{
        'اسم المريض': patient_name.value,
        'الاختبار': test_name.value,
        'النتيجة': result_value.value,
        'ملاحظات': notes.value,
        'الحالة': 'جديدة'
    }])
    df = pd.concat([df, new_data], ignore_index=True)
    update_table()

# تعديل نتيجة
def edit_result(b):
    global df
    idx = edit_index.value
    field = edit_field.value
    val = edit_value.value
    if idx >= 0 and idx < len(df):
        if field == 'النتيجة':
            df.at[idx, field] = float(val)
        else:
            df.at[idx, field] = val
        df.at[idx, 'الحالة'] = 'معدلة'
        update_table()

# إعادة تعيين البيانات
def reset_all(b):
    global df
    df = pd.DataFrame(columns=['اسم المريض', 'الاختبار', 'النتيجة', 'ملاحظات', 'الحالة'])
    update_table()

# حفظ Excel
def save_excel(b):
    df.drop(columns=['الحالة']).to_excel('نتائج_المختبر.xlsx', index=False)
    files.download('نتائج_المختبر.xlsx')

# تصدير PDF
def save_pdf(b):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, "نتائج المختبر", ln=True, align="C")
    pdf.ln(5)
    for i, row in df.iterrows():
        pdf.cell(0, 8, f"{i+1}. {row['اسم المريض']} - {row['الاختبار']} - {row['النتيجة']} - {row['ملاحظات']}", ln=True)
    pdf_file = "نتائج_المختبر.pdf"
    pdf.output(pdf_file)
    files.download(pdf_file)

# البحث
def search_patient(change):
    query = change['new'].strip()
    with output:
        clear_output()
        if query == "":
            display(color_table(df))
        else:
            display(color_table(df[df['اسم المريض'].str.contains(query)]))
    update_table()

# ربط الأحداث
add_button.on_click(add_result)
edit_button.on_click(edit_result)
reset_button.on_click(reset_all)
save_excel_button.on_click(save_excel)
save_pdf_button.on_click(save_pdf)
search_box.observe(search_patient, names='value')

# تنظيم الواجهة
input_box = widgets.VBox([patient_name, test_name, result_value, notes, add_button])
edit_box = widgets.VBox([edit_index, edit_field, edit_value, edit_button])
actions_box = widgets.HBox([save_excel_button, save_pdf_button, reset_button])
status_box = widgets.HBox([total_label, new_label, modified_label])
search_box_box = widgets.VBox([search_box])
ui = widgets.VBox([input_box, edit_box, search_box_box, actions_box, status_box, output])

# عرض الواجهة
display(ui)
update_table()
