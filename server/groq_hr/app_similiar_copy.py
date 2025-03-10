# Yang ini SELECT nya DIPISAH
from flask import Flask, request, jsonify
import json
from datetime import datetime
import re
import os
import pymysql
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_core.documents import Document
from langchain.chains import LLMChain
from flask_cors import CORS
# Tidak menggunakan text splitter karena tidak ingin chunking

app = Flask(__name__)
CORS(app,
     origins=["http://localhost:5173"],
     methods=["GET", "POST", "OPTIONS"],
     allow_headers=["Content-Type", "X-Requested-With", "Authorization"])

# 1. Konfigurasi MySQL Database (PyMySQL)
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'markovkaryawandb',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

# 2. Ambil Data dari MySQL & Buat Document tanpa chunking
def get_data_from_mysql():
    connection = None
    documents = []  # List untuk menyimpan setiap dokumen
    try:
        connection = pymysql.connect(**db_config)
        with connection.cursor() as cursor:
            # Query Departemen
            cursor.execute("SELECT department FROM department")
            departments = cursor.fetchall()
            text_departments = "Departemen:\n" + "\n".join([row["department"] for row in departments])
            documents.append(Document(page_content=text_departments))

            # Query Sertifikat
            cursor.execute("SELECT certificate_name FROM certificate")
            certificates = cursor.fetchall()
            text_certificates = "Sertifikat:\n" + "\n".join([row["certificate_name"] for row in certificates])
            documents.append(Document(page_content=text_certificates))

            # Query Jurusan
            cursor.execute("SELECT major_name FROM major")
            majors = cursor.fetchall()
            text_majors = "Jurusan:\n" + "\n".join([row["major_name"] for row in majors])
            documents.append(Document(page_content=text_majors))

            # Query Posisi
            cursor.execute("SELECT position FROM position")
            positions = cursor.fetchall()
            text_positions = "Posisi:\n" + "\n".join([row["position"] for row in positions])
            documents.append(Document(page_content=text_positions))

            # Query Sekolah
            cursor.execute("SELECT school_name FROM school")
            schools = cursor.fetchall()
            text_schools = "Sekolah:\n" + "\n".join([row["school_name"] for row in schools])
            documents.append(Document(page_content=text_schools))

            # Query Strata
            cursor.execute("SELECT strata FROM strata")
            stratas = cursor.fetchall()
            text_stratas = "Strata:\n" + "\n".join([row["strata"] for row in stratas])
            documents.append(Document(page_content=text_stratas))

        return documents

    except Exception as e:
        print(f"Error retrieving data: {e}")
        return []
    finally:
        if connection is not None:
            connection.close()

# 3. Setup Embedding dan Vector Database
embedding_function = HuggingFaceEmbeddings(model_name="intfloat/e5-large-v2")
db_name = "vector_db"

if os.path.exists(db_name):
    try:
        Chroma(persist_directory=db_name, embedding_function=embedding_function).delete_collection()
        print(f"Database lama di {db_name} dihapus")
    except Exception as e:
        print(f"Gagal menghapus database: {e}")

try:
    documents = get_data_from_mysql()
    if not documents:
        raise ValueError("Tidak ada dokumen yang diambil dari MySQL.")
    db = Chroma.from_documents(
        documents=documents,
        embedding=embedding_function,
        persist_directory=db_name
    )
    print(f"Database vektor dibuat dengan {db._collection.count()} dokumen")
except Exception as e:
    print(f"Error building vector database: {e}")
    raise

# 4. Setup Model LLM
llm = ChatGroq(
    model_name='deepseek-r1-distill-llama-70b',
    api_key="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",
    temperature=0,
)
llm2 = ChatGroq(
    model='llama-3.3-70b-versatile',
    api_key="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",
    temperature=0
)
sql_query = """
SELECT 
    e.id, 
    e.full_name,
    e.status,
    e.birth_date,
    d.department,
    e.location,
    e.division,
    p.position,
    e.company_history,
    e.position_history,
    IFNULL(GROUP_CONCAT(DISTINCT c.certificate_name ORDER BY c.certificate_name SEPARATOR ', '), 'Tidak Ada') AS certificates,
    IFNULL(GROUP_CONCAT(DISTINCT CONCAT(str.strata, ' di ', s.school_name, ' Jurusan ', m.major_name) ORDER BY str.strata SEPARATOR ' | '), 'Tidak Ada') AS education_details
FROM employee e 
LEFT JOIN department d ON e.department = d.id 
LEFT JOIN position p ON p.id = e.position
LEFT JOIN employee_education ep ON ep.employee_id = e.id
LEFT JOIN major m ON ep.major_id = m.id
LEFT JOIN school s ON ep.school_id = s.id
LEFT JOIN strata str ON ep.strata = str.id
LEFT JOIN employee_certificate ec ON e.id = ec.employee_id
LEFT JOIN certificate c ON ec.certificate_id = c.id
"""

# 5. Template Prompt
sql_query_template = """
Instruksi: 
Anda adalah SQL Query Expert. Tugas Anda adalah membuat bagian **WHERE, GROUP BY, dan LIMIT** berdasarkan pertanyaan user. Berikut adalah data yang dapat Anda gunakan (PENTING: Gunakan data tersebut untuk menentukan apakah WHERE menggunakan = atau LIKE DAN untuk membedakan mana yang department, division, position, certificate, school, strata, dan major):
{context}

**Catatan Penting:**
1. Jika user **tidak menyebut jumlah** kandidat, gunakan `LIMIT 25` secara default.
2. Tugas Anda hanya **Generate WHERE, GROUP BY, dan LIMIT** sesuai contoh di bawah (GROUP BY selalu GROUP BY e.id).
3. **Perhatikan konteks data sebelum menentukan WHERE**:
   - `CMD, OPS, HCCA, FAD, FLEET` adalah **division** (gunakan `e.division`).
   - `aktif, non-aktif` adalah **status** (gunakan `e.status`).
   - **JANGAN SALAH** antara department, division, position, certificate, school, strata, dan major. 
   - **Gunakan alias yang benar** untuk tabel:
     - `e.employee` untuk employee, list kolom: `full_name`, `birth_date`, `position_history`, `division`, `status`
     - `d.department` untuk department, list kolom: `department`
     - `p.position` untuk position, list kolom: `position`
     - `m.major` untuk major, list kolom: `major_name` 
     - `s.school` untuk school, list kolom: `school_name`
     - `str.strata` untuk strata, list kolom: `strata`
     - `c.certificate` untuk certificate, list kolom: `certificate_name`
4. e.status adalah "aktif" secara default

**Contoh:**
- **Input:** "berikan 10 Manajer IT di divisi OPS pendidikan Informatika S3 dengan sertifikat Six Sigma black Belt"
- **Output SQL (hanya ganti WHERE, GROUP BY, LIMIT, tanpa SELECT dan JOIN, JANGAN TAMBAHKAN FORMAT TAMBAHAN DILUAR QUERY SQL):**
WHERE p.position LIKE "%Manager%" 
AND d.department LIKE "%IT%" 
AND e.division = "OPS"
AND str.strata = "S3"
AND m.major_name LIKE "%Informatika%"
AND c.certificate = "Six Sigma black Belt" 
AND e.status = "aktif"
GROUP BY e.id
LIMIT 10;

BUATKAN OUTPUT UNTUK: {question}
"""
template_suggestion = """
**Instruksi:**
Anda adalah sistem rekomendasi kalimat perintah yang bertugas membuat 3 perintah serupa berdasarkan perintah berikut:

**Perintah:**
{question}

**Kriteria untuk Perintah baru berdasarkan data berikut:**
{context}
- Harus tetap dalam konteks pencarian kandidat.
- Jangan memasukkan informasi tanggal dalam perintah baru.
- Format dalam kalimat perintah

**Format Jawaban (Gunakan format JSON array, tidak perlu tambahan lain):**
["perintah1", "perintah2", "perintah3"]
"""

template_filter = """
**Instruksi:**
Anda adalah Human Resource Expert. Tugas Anda mengecek bagian DEPARTMENT:
1. Filter array kandidat BERDASARKAN input user: {{ user_query }}.
2. Hapus kandidat yang TIDAK MEMENUHI kriteria **department HANYA JIKA** department disebut dalam input user.
3. Jika input user **tidak menyebutkan department**, **jangan hapus kandidat** berdasarkan department.
4. Update field 'alasan' dengan penjelasan singkat berdasarkan kecocokan kandidat dengan kriteria (contoh: "Sesuai kriteria Manager dan OPS").
5. Output HANYA berupa JSON array yang valid, tanpa komentar atau markdown.

**Contoh Output:**
[
    {
        "id": 123,
        ...,
        "alasan": "Sesuai kriteria Manager dan OPS"
    }
]

**Array Kandidat:**
{{ executed_result }}

Jawaban (HANYA JSON array):
"""

prompt = PromptTemplate(
    template=sql_query_template,
    input_variables=["context", "question"]
)
prompt2 = PromptTemplate(
    template=template_suggestion,
    input_variables=["context", "question"]
)
promptFilter = PromptTemplate(
    template=template_filter,
    input_variables=["user_query", "executed_result"],
    template_format="jinja2"
)
def regex_think_and_sql(result_text):
    """
    Menerima output LLM dengan format:
    
    <think>Your calculated thought here...</think>
    Your SQL query here...
    
    Mengembalikan tuple (think_text, sql_query)
    """
    think_match = re.search(r"<think>(.*?)</think>", result_text, flags=re.DOTALL)
    think_text = think_match.group(1).strip() if think_match else ""
    if think_match:
        end_index = think_match.end()
        sql_query = result_text[end_index:].strip()
    else:
        sql_query = result_text.strip()
    return think_text, sql_query

def regex_sugestion(data):
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            return []
    if not isinstance(data, list):
        return []
    return [s.strip() for s in data if isinstance(s, str)]

def execute_sql_query(query):
    """
    Mengeksekusi query SQL terhadap MySQL dan mengembalikan hasilnya (list of dictionaries).
    """
    connection = None
    try:
        connection = pymysql.connect(**db_config)
        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
            return result
    except Exception as e:
        print(f"Error executing SQL query: {e}")
        return None
    finally:
        if connection is not None:
            connection.close()

def extract_conditions(query):
    where_clause_match = re.search(r'WHERE(.*?)GROUP BY', query, re.DOTALL | re.IGNORECASE)
    if not where_clause_match:
        return []
    
    where_clause = where_clause_match.group(1)
    conditions = re.findall(r'([a-zA-Z_\.]+)\s*(LIKE|=)\s*"(.*?)"', where_clause)
    
    result = {}
    for column, operator, value in conditions:
        key = column.split('.')[-1]  # Ambil hanya nama kolom
        if operator.upper() == 'LIKE':
            value = value.replace('%', '')  # Hilangkan % jika ada
        result[key] = value
    
    return [result]

@app.route('/search', methods=['POST'])
def search_candidates():
    try:
        data = request.get_json()
        user_query = data.get('query', '')
        if not user_query:
            return jsonify({"error": "Query tidak boleh kosong"}), 400
        
        print("User Query:", user_query)
        retriever = db.as_retriever(search_kwargs={"k": 50})
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=True
        )
        qa_chain2 = RetrievalQA.from_chain_type(
            llm=llm2,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": prompt2},
            return_source_documents=True
        )
        
        current_date = datetime.now().strftime("%d %B %Y")
        case_information = f"{user_query} (Untuk sekedar informasi, tanggal saat ini adalah {current_date})"
                
        response2 = qa_chain2.invoke({"query": case_information})
        print("LLM 2 Response:", response2["result"])
        
        result = qa_chain.invoke({"query": case_information})
        think_text, candidates = regex_think_and_sql(result["result"])
        print("Think:", think_text)
        print("Candidates sql:", candidates)
        
        final_query = f"{sql_query}{candidates}"
        print(final_query)
        executed_result = None
        if candidates:
            executed_result = execute_sql_query(final_query)
        
        # Tambahkan field 'alasan' pada setiap record (menggunakan think_text sebagai contoh)
        if executed_result and isinstance(executed_result, list):
            for row in executed_result:
                row['alasan'] = "Field alasan"
        print(executed_result)
        # Buat prompt kustom dengan menyematkan informasi yang sudah ada
        qa_chain3 = LLMChain(
            llm=llm2,
            prompt=promptFilter
        )
        executed_result_str = json.dumps(executed_result, default=str)
        try:
            response3 = qa_chain3.invoke({
                "user_query": user_query,
                "executed_result": executed_result_str
            })
            print("Response3 Raw:", response3)  # Debug log
            print("response3['text']:", response3['text'])
        except Exception as e:
            print(f"Error in qa_chain3: {str(e)}")
            return jsonify({"error": "Gagal memproses filter kandidat"}), 500
        try:
            # Bersihkan teks tambahan di luar JSON
            json_str = re.search(r'\[.*\]', response3['text'], flags=re.DOTALL).group()
            filtered_data = json.loads(json_str)
        except (json.JSONDecodeError, AttributeError) as e:
            print(f"Error parsing JSON: {e}")
            filtered_data = []  # Atau return error ke client
        response_payload = {
            "suggestion": regex_sugestion(response2["result"]),
            "keyword" : extract_conditions(candidates),
            "think": think_text,
            "answer": filtered_data,
            "sources": [
                {"content": doc.page_content, "metadata": doc.metadata}
                for doc in result["source_documents"]
            ]
        }
        print("Cleaned Query Array:", response_payload['answer'])
        print("keyword: ", response_payload['keyword'])
        print("IS LIST: ", isinstance(response_payload['keyword'],list))
        # print(isinstance(json.loads(response_payload['keyword']), list))
        
        return jsonify(response_payload)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5025, debug=True)
    
    