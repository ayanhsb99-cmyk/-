import streamlit as st
from google import genai

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
    st.info("💡 أدخل مفتاح API الصادر من Google AI Studio لتشغيل عمليات التحليل.")

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

# ==========================================
# 3. دالة التحليل المدمج عبر Gemini 3.8
# ==========================================
def generate_combined_report(chat1_msgs, chat2_msgs, chat3_msgs, user_api_key):
    client = genai.Client(api_key=user_api_key.strip())
    
    combined_text = "### محتوى الجروب الأول:\n" + "\n".join([f"- {m}" for m in chat1_msgs[:150]]) + "\n\n"
    combined_text += "### محتوى الجروب الثاني:\n" + "\n".join([f"- {m}" for m in chat2_msgs[:150]]) + "\n\n"
    combined_text += "### محتوى الجروب الثالث:\n" + "\n".join([f"- {m}" for m in chat3_msgs[:150]])

    prompt = f"""
أنت خبير في تحليل المنشورات ورصد الرأي العام والوسائط الاجتماعية.
لديك المحتوى المستخرج من (3) جروبات واتساب مختلفة خلال الأسبوع الماضي:

---
{combined_text}
---

المطلوب منك تحليل كافة المحادثات ودمج الأفكار لتوليد تقرير أسبوعي شامل باللغة العربية يغطي المواضيع من كافة الجروبات:

1. **جدول التصنيف العام الشامل**:
قم باستخراج كافة المواضيع والمنشورات المذكورة، وصنفها في جدول Markdown يحتوي على الحقول التالية:
| الموضوع الرئيسي | نوع التصنيف (شائعة / رأي عام / رصد) | التقييم (إيجابي / سلبي / محايد) | المنصة (فيسبوك / انستغرام / تليكرام / واتساب / تيك توك / مواقع اخبارية / X / غير محدد) | مستوى التفاعل (ضعيف / متوسط / عالي) | المصدر (جروب 1 / 2 / 3 أو مشترك) |

2. **التقرير الأسبوعي الشامل لأهم المواضيع**:
حدد أهم المواضيع المطروحة عبر الجروبات الثلاثة، وقدم تحليلاً لكل موضوع بالهيكلية التالية:
- **عنوان الموضوع**:
- **شرح وتفاصيل الموضوع**:
- **الحلول المقترحة**:
- **الاستنتاجات**:
- **التوصيات**:
"""

    response = client.models.generate_content(
        model='gemini-3.8-flash',
        contents=prompt
    )
    return response.text

# ==========================================
# 4. أيقونات واجهة رفع الملفات الثلاثة
# ==========================================
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 💬 الجروب الأول")
    file1 = st.file_uploader("يرجى رفع ملف
