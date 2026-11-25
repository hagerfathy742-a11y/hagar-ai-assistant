import os
import time
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pypdf import PdfReader

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

st.set_page_config(page_title="Hagar Company - المساعد الذكي", page_icon="🌟", layout="wide", initial_sidebar_state="collapsed")

    "🌸 وردي بنفسجي عصري": "linear-gradient(135deg, #EC4899 0%, #8B5CF6 100%)",
}

with st.sidebar:
    st.header("🎨 تخصيص الشكل والألوان")
    selected_theme = st.selectbox("اختاري ألوان الواجهة:", list(themes.keys()))
    st.divider()
    st.header("⚙️ لوحة تحكم الشركة")
    company_name = st.text_input("اسم الشركة / البراند", value="Hagar Company")
    whatsapp_number = st.text_input("رقم الواتساب للتواصل السريع", value="01000000000")
    assistant_role = st.selectbox(
        "شخصية المساعد الذكي",
        ["مندوب مبيعات وخدمة عملاء محترف", "مساعد حجز مواعيد واستفسارات", "مستشار دعم فني وحل مشكلات"]
    )
    st.divider()
    uploaded_file = st.file_uploader("📄 ارفع كتالوج أو ملف أسعار الشركة (PDF / TXT)", type=["pdf", "txt"])
    
    company_data = ""
    if uploaded_file is not None:
        if uploaded_file.name.endswith(".pdf"):
            reader = PdfReader(uploaded_file)
            for page in reader.pages:
                company_data += page.extract_text() + "\n"
        else:
            company_data = uploaded_file.read().decode("utf-8")
        st.success("✅ تم ربط ملف الشركة بنجاح!")
    else:
        company_data = st.text_area(
            "📝 أو اكتب تفاصيل المنتجات والأسعار هنا:",
            value="نحن شركة متخصصة في بيع الأجهزة الإلكترونية الحديثة بضمان عامين. مواعيد العمل يومياً من 10 صباحاً حتى 10 مساءً. التوصيل متاح لجميع المحافظات خلال 48 ساعة بتكلفة 50 جنيه.",
            height=150
        )

    st.divider()
    if st.button("🗑️ بدء محادثة جديدة", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

banner_gradient = themes[selected_theme]

st.markdown(f"""
<style>
    @import url('https://googleapis.com');
    html, body, [class*="css"] {{
        font-family: 'Cairo', sans-serif;
        direction: rtl;
        text-align: right;
    }}
    .main-card {{
        background: {banner_gradient};
        padding: 28px;
        border-radius: 18px;
        color: white;
        text-align: center;
        margin-bottom: 22px;
        box-shadow: 0 8px 20px rgba(255, 81, 47, 0.25);
    }}
    .main-title {{font-size: 2.1rem; font-weight: 700; margin-bottom: 6px;}}
    .sub-title {{font-size: 1.05rem; opacity: 0.95;}}
    div.stButton > button {{
        border-radius: 12px;
        border: 1px solid #FF512F;
        font-weight: 600;
        transition: all 0.3s ease;
    }}
    div.stButton > button:hover {{
        background: {banner_gradient};
        color: white;
        border: none;
    }}
    .stChatMessage {{direction: rtl; text-align: right;}}
    .stTextInput > div > div > input {{direction: rtl; text-align: right;}}
    .stTextArea > div > div > textarea {{direction: rtl; text-align: right;}}
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="main-card">
    <div class="main-title">🌟 المساعد الذكي لـ {company_name}</div>
    <div class="sub-title">خدمة عملاء فورية على مدار 24 ساعة — اسألني عن الأسعار، المنتجات، أو الحجز</div>
</div>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []


st.write("💡 *أسئلة سريعة (اضغط للإجابة الفورية):*")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🕒 مواعيد العمل والفروع", use_container_width=True):
        st.session_state.pending_prompt = "ما هي مواعيد العمل لديكم؟"
with col2:
    if st.button("🚚 تفاصيل وتكلفة التوصيل", use_container_width=True):
        st.session_state.pending_prompt = "ما هي تفاصيل وتكلفة التوصيل للمحافظات؟"
with col3:
    if st.button("📞 التواصل مع المبيعات", use_container_width=True):
        st.session_state.pending_prompt = "كيف يمكنني التواصل مع فريق المبيعات أو الحجز؟"

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("اكتب سؤالك أو استفسارك هنا...")
prompt = st.session_state.pop("pending_prompt", None) or user_input


if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if not api_key:
            st.error("⚠️ تأكد من وضع مفتاح GEMINI_API_KEY في ملف .env")
        else:
            client = genai.Client(api_key=api_key)
            system_instruction = f"""
            أنت {assistant_role} تعمل لصالح '{company_name}'.
            أجب على أسئلة العملاء بلباقة واحترافية وباللهجة المصرية المهذبة.
            اعتمد في إجاباتك على بيانات الشركة التالية:
            ---
            التزم بالإملاء العربي الصحيح دائماً واكتب الكلمات كاملة مثل (يا فندم) بدون اختصار أو حذف حروف.
            {company_data}
            ---
            رقم الواتساب الرسمي للشركة هو: {whatsapp_number}.
            إذا طلب العميل الحجز أو الشراء أو سأل عن شيء غير موجود في البيانات، اعرض عليه التواصل مباشرة عبر واتساب على الرقم {whatsapp_number}.
            اجعل إجاباتك قصيرة ومباشرة ومقنعة.
            """

            def stream_response():
                response = client.models.generate_content_stream(
                    model="gemini-3.8-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.3,
                    ),
                )
                for chunk in response:
                    if chunk.text:
                        yield chunk.text

            for attempt in range(3):
             try:
                 reply = st.write_stream(stream_response)
                 st.session_state.messages.append({"role": "assistant", "content": reply})
                 break
             except Exception:
                 if attempt < 2:
                     time.sleep(3)
                 else:
                     st.warning("الضغط مرتفع حالياً، جرب إرسال الرسالة مرة أخرى.")
