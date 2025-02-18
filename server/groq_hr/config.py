import pymysql

# Konfigurasi Database MySQL
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'markovkaryawandb',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

# Direktori untuk menyimpan database vektor
VECTOR_DB_DIR = "vector_db"

# Konfigurasi API dan model untuk ChatGroq
CHAT_GROQ_API_KEY = "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"
LLM_MODEL_1 = "deepseek-r1-distill-llama-70b"
LLM_MODEL_2 = "llama-3.3-70b-versatile"
LLM_MODEL_3 = "llama-3.1-8b-instant"

TEMPERATURE_DEFAULT = 0.3
TEMPERATURE_FILTER = 0.2