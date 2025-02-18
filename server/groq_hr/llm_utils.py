from langchain_groq import ChatGroq
from config import CHAT_GROQ_API_KEY, LLM_MODEL_1, LLM_MODEL_2, LLM_MODEL_3, TEMPERATURE_DEFAULT, TEMPERATURE_FILTER

# Inisialisasi LLM utama
llm = ChatGroq(
    model_name=LLM_MODEL_1,
    api_key=CHAT_GROQ_API_KEY,
    temperature=TEMPERATURE_DEFAULT
)

llm2 = ChatGroq(
    model=LLM_MODEL_2,
    api_key=CHAT_GROQ_API_KEY,
    temperature=TEMPERATURE_DEFAULT
)

llm_filter = ChatGroq(
    model=LLM_MODEL_2,
    api_key=CHAT_GROQ_API_KEY,
    temperature=TEMPERATURE_FILTER
)

def get_llm3():
    """
    Inisialisasi LLM ketiga (dipakai untuk parafrase).
    """
    return ChatGroq(
        model=LLM_MODEL_3,
        api_key=CHAT_GROQ_API_KEY,
        temperature=TEMPERATURE_DEFAULT
    )
