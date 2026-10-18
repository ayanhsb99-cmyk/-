import streamlit as st
from google import genai
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
import io

# ==========================================
# 1. إعدادات الواجهة والصفحة
# ==========================================
st.set_page_config(
    page_title="نظام تحليل محادثات الواتساب الأسبوعي",
    page_icon="📊",
    layout="wide"
)

st.title("📊 نظام تحليل الرأي العام والتقارير الأسبوعية")
st.subheader("قم برفع ملفات المحادثات للجروبات الثلاثة لتوليد التقرير المدمج")

# إدخال مفتاح API في الشريط الجانبي
with st.sidebar:
    st.header("⚙️ إعدادات النظام")
    api_key = st.text_input(
        "أدخل مفتاح Gemini API الخاص بك:", 
        type="password",
        help="احصل على مفتاح مجاني من https://aistudio.google.com/app/apikey"
    )
    st.info("💡 المفتاح يتم استخدامه لتشغيل عمليات التحليل فقط.")

# ==========================================
# 2. دالة تنظيف وقراءة المحادثات
# ==========================================
def parse_whatsapp_chat(file_content):
    lines = file_content.decode('utf-8', errors='ignore').splitlines()
    messages = []
    
    for line in lines:
        line_str = line.strip()
        if not line_str or "<Media omitted>" in line_str or "Messages and calls are end-to-end encrypted" in line_str:
            continue
        
        if ":" in line_str:
            parts = line_str.split(":", 1)
            if len(parts) > 1 and len(parts[1].strip()) > 0:
                messages.append(parts[1].strip())
        else:
            if messages:
                messages[-1] += " " + line_str
                
    return messages

def get_balanced_sample(msgs, max_count=600):
    if len(msgs) <= max_count:
        return msgs
    step = len(msgs) // max_count
    return msgs[::step][:max_count]

# ==========================================
# 3. دالة إنشاء مستند Word (DOCX) وتنسيقه
# ==========================================
def create_docx_report(report_text):
    doc = docx.Document()
    
    # تحويل النص إلى أسطر لإنشاء الهيكلية
    lines = report_text.splitlines()
    
    for line in lines:
        line_str = line.strip()
        if not line_str:
            continue
            
        # العناوين الرئيسية
        if line_str.startswith("# "):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            run = p.add_run(line_str.replace("# ", ""))
            run.font.size = Pt(18)
            run.font.bold = True
            run.font.color.rgb = RGBColor(0, 51, 102)
        elif line_str.startswith("## "):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            run = p.add_run(line_str.replace("## ", ""))
            run.font.size = Pt(16)
            run.font.bold = True
            run.font.color.rgb = RGBColor(0, 102, 153)
        elif line_str.startswith("### "):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            run = p.add_run(line_str.replace("### ", ""))
            run.font.size = Pt(14)
            run.font.bold = True
        else:
            # الفقرات العادية
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            run = p.add_run(line_str.replace("**", ""))
            run.font.size = Pt(12)
            
    # حفظ المستند في الذاكرة
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# ==========================================
# 4. دالة التحليل وبناء التقرير
# ==========================================
def generate_combined_report(chat1_msgs, chat2_msgs, chat3_msgs, user_api_key):
    client = genai.Client(api_key=user_api_key.strip())
    
    s1 = get_balanced_sample(chat1_msgs, 600)
    s2 = get_balanced_sample(chat2_msgs, 600)
    s3 = get_balanced_sample(chat3_msgs, 600)
    
    combined_text = "=== محتوى الجروب الأول ===\n" + "\n".join([f"- {m}" for m in s1]) + "\n\n"
    combined_text += "=== محتوى الجروب الثاني ===\n" + "\n".join([f"- {m}" for m in s2]) + "\n\n"
    combined_text += "=== محتوى الجروب الثالث ===\n" + "\n".join([f"- {m}" for m in s3])

    prompt = f"""
أنت خبير إستراتيجي في تحليل العمليات النفسية والرأي العام.
لديك المحتوى المستخرج من (3) جروبات رصد محادثات مختلفة:

---
{combined_text}
---

المطلوب منك تحليل كافة المحادثات والمنشورات بالكامل بدون استثناء، وتوليد التقرير النهائي باللغة العربية مع الالتزام بالواجهة والهيكلية أدناه بالضبط:

==================================================
جهاز الأمن الوطني
مديرية أمن بغداد
قسم الوقائي
العمليات النفسية

التقرير الأسبوعي
==================================================

قائمة المحتويات:
1. الإيجاز العام
2. موقف العمليات النفسية وأبرز الشائعات والرأي العام والمرصد
3. تحليل شامل لكافة المواضيع المرصودة بدون استثناء
4. موقف الخطاب الديني والاجتماعي
5. القراءة الاستشرافية والتهديدات المحتملة
6. المعالجات والتوصيات المقترحة
7. جدول ملخص كافة المواضيع وتصنيفاتها

--------------------------------------------------

### 1. الإيجاز العام:
ملخص تنفيذي شامل لكافة ما تم رصده في المحادثات لهذا الأسبوع.

### 2. موقف العمليات النفسية وأبرز الشائعات والرأي العام والمرصد:
تحليل دقيق لكافة تحركات التضليل الإعلامي والحملات الموجهة والشائعات المنتشرة.

### 3. تحليل شامل لكافة المواضيع المرصودة (شامل لجميع المواضيع الفرعية والرئيسية المذكورة في الرسائل):
قم باستخراج وتحليل **جميع** المواضيع المطروحة في الجروبات الثلاثة دون حذف أو اختصار لمواضيع معينة، ولكل موضوع اكتب:
- **عنوان الموضوع**:
- **شرح وتفاصيل الموضوع**:
- **المنصة / المصدر**:
- **الحلول المقترحة**:
- **الاستنتاجات**:
- **التوصيات**:

### 4. موقف الخطاب الديني والاجتماعي:
رصد التوجهات في الخطاب الديني أو العشائري أو الاجتماعي.

### 5. القراءة الاستشرافية والتهديدات المحتملة:
توقع التهديدات والسيناريوهات القادمة بناءً على كل ما تم رصده.

### 6. المعالجات والتوصيات المقترحة:
التوصيات التنفيذية المقترحة للتعامل مع الشائعات وإدارة الرأي العام.

### 7. جدول ملخص كافة المواضيع وتصنيفاتها:
أنشئ جدول Markdown شامل يحتوي على **كافة المواضيع المذكورة في المحادثات**:
| الرقم | الموضوع | نوع التصنيف (شائعة / رأي عام / رصد) | التقييم (إيجابي / سلبي / محايد) | المنصة / المصدر | مستوى التفاعل | المعالجة المقترحة |
"""

    response = client.models.generate_content(
        model='gemini-3.8-flash',
        contents=prompt
    )
    return response.text

# ==========================================
# 5. أيقونات واجهة رفع الملفات الثلاثة
# ==========================================
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 💬 الجروب الأول")
    file1 = st.file_uploader("يرجى رفع ملف Chat 1 (.txt)", type=["txt"], key="file1")

with col2:
    st.markdown("### 💬 الجروب الثاني")
    file2 = st.file_uploader("يرجى رفع ملف Chat 2 (.txt)", type=["txt"], key="file2")

with col3:
    st.markdown("### 💬 الجروب الثالث")
    file3 = st.file_uploader("يرجى رفع ملف Chat 3 (.txt)", type=["txt"], key="file3")

st.markdown("---")

# ==========================================
# 6. زر المعالجة واستخراج النتائج
# ==========================================
if st.button("🚀 توليد التقرير الأسبوعي المدمج", type="primary", use_container_width=True):
    if not api_key:
        st.error("⚠️ يرجى إدخال مفتاح API الخاص بك في الشريط الجانبي أولاً.")
    elif not (file1 and file2 and file3):
        st.warning("⚠️ يرجى رفع ملفات المحادثات للجروبات الثلاثة قبل بدء التحليل.")
    else:
        try:
            with st.spinner("⏳ جاري قراءة الملفات وتحليل كافة المحادثات..."):
                msgs1 = parse_whatsapp_chat(file1.getvalue())
                msgs2 = parse_whatsapp_chat(file2.getvalue())
                msgs3 = parse_whatsapp_chat(file3.getvalue())
                
                st.success(f"✅ تم القراءة بنجاح! (الجروب الأول: {len(msgs1)} رسالة | الجروب الثاني: {len(msgs2)} رسالة | الجروب الثالث: {len(msgs3)} رسالة)")
                
                report = generate_combined_report(msgs1, msgs2, msgs3, api_key)
                
                # إنشاء ملف Word
                docx_file = create_docx_report(report)
                
                st.markdown("---")
                st.header("📊 التقرير الأسبوعي المدمج والتحليل الشامل")
                st.markdown(report)
                
                st.download_button(
                    label="📄 تنزيل التقرير بملف ورد (Weekly_Report.docx)",
                    data=docx_file,
                    file_name="Weekly_Report.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
        except Exception as e:
            st.error(f"❌ حدث خطأ أثناء تنفيذ الطلب: {e}")
