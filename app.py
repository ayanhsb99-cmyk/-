import streamlit as st
import google.generativeai as genai

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
        "أدخل مفتاح Gemini API:", 
        value="AQ.Ab8RN6Lc3K0vcmrUlkgCnsPqtJ67EiHJOvqmhdGLvPzmBHqTAg", 
        type="password"
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

# ==========================================
# 3. دالة التحليل المدمج عبر Gemini
# ==========================================
def generate_combined_report(chat1_msgs, chat2_msgs, chat3_msgs, user_api_key):
    genai.configure(api_key=user_api_key)
    
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

    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    return response.text

# ==========================================
# 4. أيقونات واجهة رفع الملفات الثلاثة
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
# 5. زر المعالجة واستخراج النتائج
# ==========================================
if st.button("🚀 توليد التقرير الأسبوعي المدمج", type="primary", use_container_width=True):
    if not api_key:
        st.error("⚠️ يرجى إدخال مفتاح API في الشريط الجانبي أولاً.")
    elif not (file1 and file2 and file3):
        st.warning("⚠️ يرجى رفع ملفات المحادثات للجروبات الثلاثة قبل بدء التحليل.")
    else:
        try:
            with st.spinner("⏳ جاري قراءة الملفات وتحليل كافة محادثات الجروبات..."):
                msgs1 = parse_whatsapp_chat(file1.getvalue())
                msgs2 = parse_whatsapp_chat(file2.getvalue())
                msgs3 = parse_whatsapp_chat(file3.getvalue())
                
                st.success(f"✅ تم القراءة بنجاح! (الجروب الأول: {len(msgs1)} رسالة | الجروب الثاني: {len(msgs2)} رسالة | الجروب الثالث: {len(msgs3)} رسالة)")
                
                report = generate_combined_report(msgs1, msgs2, msgs3, api_key)
                
                st.markdown("---")
                st.header("📊 التقرير الأسبوعي المدمج والتحليل الشامل")
                st.markdown(report)
                
                st.download_button(
                    label="📥 تنزيل التقرير بملف (Weekly_Report.txt)",
                    data=report,
                    file_name="Weekly_Report.txt",
                    mime="text/plain",
                    use_container_width=True
                )
        except Exception as e:
            st.error(f"❌ حدث خطأ أثناء تنفيذ الطلب: {e}")
