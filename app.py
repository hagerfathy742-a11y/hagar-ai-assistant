import os
import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from pypdf import PdfReader

load_dotenv()
api_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")

st.set_page_config(page_title="Hagar Company - المساعد الذكي", page_icon="🌟", layout="wide", initial_sidebar_state="collapsed")

banner_gradient = "linear-gradient(135deg, #EC4899 0%, #8B5CF6 100%)"

st.markdown(f"""
<style>
    @import url('https://googleapis.com');
    html, body, [class*="css"] {{
        font-family: 'Cairo', sans-serif;
    }}
    @media (max-width: 768px) {{
        section[data-testid="stSidebar"] {{
            display: none !important;
        }}
    }}
    .main-card {{
        background: {banner_gradient};
        padding: 24px;
        border-radius: 18px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 8px 20px rgba(236, 72, 153, 0.25);
        direction: rtl;
    }}
    .main-title {{font-size: 1.9rem; font-weight: 700; margin-bottom: 6px;}}
    .sub-title {{font-size: 1rem; opacity: 0.95;}}
    div.stButton > button {{
        border-radius: 12px;
        border: 1px solid #EC4899;
        font-weight: 600;
        direction: rtl;
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

with st.sidebar:
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

st.markdown(f"""
<div class="main-card">
    <div class="main-title">🌟 المساعد الذكي لـ {company_name}</div>
    <div class="sub-title">خدمة عملاء فورية على مدار 24 ساعة — اسألني عن الأسعار، المنتجات، أو الحجز</div>
</div>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

st.markdown('<p style="direction: rtl; text-align: right; font-weight: bold;">💡 أسئلة سريعة (اضغط للإجابة الفورية):</p>', unsafe_allow_html=True)
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
            st.error("⚠️ تأكد من وضع مفتاح GROQ_API_KEY في إعدادات Secrets")
        else:
            client = Groq(api_key=api_key)
            system_instruction = f"""
            أنت {assistant_role} تعمل لصالح '{company_name}'.
            أجب على أسئلة العملاء بلباقة واحترافية وباللهجة المصرية المهذبة.
            التزم بالإملاء العربي الصحيح دائماً واكتب الكلمات كاملة مثل (يا فندم) بدون اختصار أو حذف حروف.
            اعتمد في إجاباتك على بيانات الشركة التالية:
            ---
            {company_data}
            ---
            رقم الواتساب الرسمي للشركة هو: {whatsapp_number}.
            إذا طلب العميل الحجز أو الشراء أو سأل عن شيء غير موجود في البيانات، اعرض عليه التواصل مباشرة عبر واتساب على الرقم {whatsapp_number}.
            اجعل إجاباتك منظمة ومقنعة للبيع.
            """

            try:
                active_model = "llama-3.1-8b-instant"
                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": prompt},
                    ],
                    model=active_model,
                    temperature=0.3,
                )
                reply = chat_completion.choices[0].message.content
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                st.error(f"حدث خطأ: {e}")
