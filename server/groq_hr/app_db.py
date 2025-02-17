from flask import Flask, request, jsonify
import json
from datetime import datetime
import re
import os
import pymysql  # Ganti mysql.connector dengan pymysql
from langchain_community.document_loaders import DataFrameLoader
from langchain_community.vectorstores.utils import filter_complex_metadata
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
# from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import RetrievalQA
import pandas as pd
from langchain_core.documents import Document
from flask_cors import CORS
from langchain.text_splitter import RecursiveCharacterTextSplitter

app = Flask(__name__)
CORS(app,
     origins=["http://localhost:5173"],
     methods=["GET","POST","OPTIONS"],
     allow_headers=["Content-Type", "X-Requested-With", "Authorization"])

# 1. Konfigurasi MySQL Database (PyMySQL)
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'markovkaryawandb',
    'charset': 'utf8mb4',  # Tambahkan konfigurasi charset
    'cursorclass': pymysql.cursors.DictCursor
}

# 2. Ambil Data dari MySQL & Buat Chunk dengan Metadata
def get_data_from_mysql():
    try:
        connection = pymysql.connect(**db_config)
        with connection.cursor() as cursor:
            query = """
                SELECT 
                    e.id, 
                    e.nik,
                    e.full_name,
                    e.status,
                    e.birth_date,
                    d.department,
                    e.location,
                    e.division,
                    p.position,
                    e.education_major,
                    e.education_institute,
                    e.company_history,
                    e.position_history
                FROM employee e 
                JOIN department d ON e.department = d.id 
                JOIN position p ON p.id = e.position
            """
            cursor.execute(query)
            results = cursor.fetchall()

            # Buat instance text splitter untuk memecah teks panjang menjadi chunk
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
            documents = []
            for row in results:
                # Gabungkan data tiap baris menjadi teks
                text = f"""
                id: {row['id']}
                Nama: {row['full_name']}
                NIK: {row['nik']}
                Status: {row['status']}
                Tanggal Lahir: {row['birth_date']}
                Departemen: {row['department']}
                Lokasi: {row['location']}
                Divisi: {row['division']}
                Posisi: {row['position']}
                Pendidikan: {row['education_major']} di {row['education_institute']}
                Riwayat Pekerjaan: {row['position_history']}
                Riwayat Perusahaan: {row['company_history']}
                """
                # Pecah teks menjadi beberapa chunk
                chunks = text_splitter.split_text(text)
                # Siapkan metadata berdasarkan data row
                metadata = {
                    "id": row['id'],
                    "full_name": row['full_name'],
                    "nik": row['nik'],
                    "status": row['status'],
                    "birth_date": str(row['birth_date']),
                    "department": row['department'],
                    "location": row['location'],
                    "division": row['division'],
                    "position": row['position'],
                    "education_major": row['education_major'],
                    "education_institute": row['education_institute'],
                    "company_history": row['company_history'],
                    "position_history": row['position_history']
                }
                # Buat Document untuk setiap chunk dengan metadata yang sesuai
                for chunk in chunks:
                    documents.append(Document(page_content=chunk, metadata=metadata))
            return documents

    except Exception as e:
        print(f"Error retrieving data: {e}")
        return []
    finally:
        if connection:
            connection.close()
              
# 3. Setup Embedding dan Vector Database
embedding_function = HuggingFaceEmbeddings(model_name="sentence-transformers/multi-qa-mpnet-base-dot-v1")
db_name = "vector_db"

# Hapus database lama jika ada
if os.path.exists(db_name):
    try:
        Chroma(persist_directory=db_name, embedding_function=embedding_function).delete_collection()
        print(f"Database lama di {db_name} dihapus")
    except Exception as e:
        print(f"Gagal menghapus database: {e}")

# Bangun database baru dari MySQL
try:
    documents = get_data_from_mysql()
    db = Chroma.from_documents(
        documents=documents,
        embedding=embedding_function,
        persist_directory=db_name
    )
    print(f"Database vektor dibuat dengan {db._collection.count()} dokumen")
except Exception as e:
    print(f"Error building vector database: {e}")
    raise

# 4. Setup Model LLM (tetap sama)
llm = ChatGroq(
    model_name='deepseek-r1-distill-llama-70b',
    api_key="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",
    temperature=0.5,
)
llm2 = ChatGroq(
    model='llama-3.3-70b-versatile',
    api_key="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",
    temperature=0.3
)
llm_filter = ChatGroq(
    model='llama-3.3-70b-versatile',
    api_key="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",
    temperature=0.2
)
# 5. Template Prompt (tetap sama)
template = """
Instruksi:
Anda adalah asisten pencari kandidat. Pilih kandidat terbaik berdasarkan data berikut:
{context}

Perintah:
{question}

Catatan:
- Pilih hanya kandidat yang 100 persen memenuhi setiap kriteria (Perhatikan department, divisi, posisi dan semua perintah user. Pastikan outputnya 100 persen memenuhi kriteria).
- Jangan menambahkan informasi di luar data yang diberikan.
- Setiap ID harus unik dalam satu output.
- Cek ulang agar hasil sesuai dengan permintaan.

Format Jawaban (Buat sesuai persis sesuai formatnya. Perhatikan huruf kapitalnya juga -> ID, Alasan):
1. ID: [id]
   Alasan: [Alasan pemilihan kandidat]

Jika tidak ada yang cocok, Jika ada meskipun satu, tampilkan yang ada, jawab:
"Tidak ditemukan kandidat yang sesuai."
"""
template2 = """
**Instruksi:**
Anda adalah sistem rekomendasi kalimat perintah yang bertugas membuat 3 perintah serupa berdasarkan perintah berikut:

**Perintah:**
{question}

**Kriteria untuk Perintah baru berdasarkan data berikut**:
{context}
- Harus tetap dalam konteks pencarian kandidat.
- Variasi dapat berupa perubahan pada jabatan, departemen, tingkat pengalaman, atau pendidikan.
- Jangan hanya mengubah kata-kata secara acak, tetapi buat perintah yang tetap masuk akal.
- Jangan memasukkan informasi tanggal dalam perintah baru.
- Format dalam kalimat perintah

**Contoh sebelum dan sesudah:**
- Input: "Cari kandidat dengan pengalaman 5 tahun di bidang IT."
- Output: ["Cari kandidat dengan pengalaman di bidang keamanan siber.", "Cari kandidat dengan latar belakang software engineering.", "Cari kandidat yang memiliki keahlian cloud computing."]

**Format Jawaban (Gunakan format JSON array, tidak perlu tambahan lain):**
["perintah1", "perintah2", "perintah3"]
"""
filter_prompt_template = """
Instruksi: 
Anda adalah sistem ekstraksi filter divisi. Ambil divisi dari perintah pengguna.
Jika tidak disebutkan, kosongkan saja. Hanya tampilkan dalam format JSON.
Divisi yang ada = ["FAD", "FLEET", "HCCA", "OPS", "CMD"]
Contoh:
- Input: "Cari MANAGER IT di divisi FAD"
  Output: {"division": "FAD"}

- Input: "Tampilkan kandidat MANAGER IT di HCCA atau OPS"
  Output: {"division": ["HCCA", "OPS"]}

- Input: "Cari kandidat posisi ANALYST"
  Output: {}

Jawaban (Hanya JSON):

Perintah:
"""
prompt = PromptTemplate(
    template=template,
    input_variables=["context", "question"]
)
prompt2 = PromptTemplate(
    template=template2,
    input_variables=["context", "question"]
)
prompt3 = PromptTemplate(
    template=filter_prompt_template,
    input_variables=["question"]
)
@app.route('/update', methods=['GET'])
def update_vector_db():
    # Mengambil data terbaru dari MySQL
    documents = get_data_from_mysql()
    
    if not documents:
        print("Tidak ada data baru untuk memperbarui ChromaDB.")
        return jsonify({"message": "Tidak ada data baru"}), 200
    
    # Persiapkan embedding function untuk update
    embedding_function = HuggingFaceEmbeddings(model_name="sentence-transformers/multi-qa-mpnet-base-dot-v1")
    db_name = "vector_db"
    
    # Jika collection lama ada, hapus dulu
    if os.path.exists(db_name):
        try:
            chroma_db = Chroma(persist_directory=db_name, embedding_function=embedding_function)
            chroma_db.delete_collection()  # Menghapus koleksi lama
            print(f"Database lama di {db_name} dihapus.")
        except Exception as e:
            print(f"Gagal menghapus database lama: {e}")
    
    # Bangun database baru dari dokumen terbaru
    try:
        db = Chroma.from_documents(
            documents=documents,
            embedding=embedding_function,
            persist_directory=db_name
        )
        
        # Memperbarui retriever dan qa_chain dengan database yang baru
        global retriever
        retriever = db.as_retriever(search_kwargs={"k": 10})  # Pastikan retriever menggunakan database yang baru
        
        global qa_chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=True
        )
        
        print(f"ChromaDB diperbarui dengan {len(documents)} dokumen.")
        return jsonify({
            "message": "ChromaDB diperbarui dan retriever diperbarui."
        }), 200
    except Exception as e:
        print(f"Error membangun ChromaDB: {e}")
        raise   
    
# 7. Fungsi Bantuan untuk Mengambil Data Employee Berdasarkan Hasil LLM
def get_array_employee(data):
    connection = None
    try:
        connection = pymysql.connect(**db_config)
        with connection.cursor() as cursor:
            if isinstance(data, list):
                data_array = data
            else:
                data_array = json.loads(data)
                
            employees = []
            for employee in data_array:
                employee_id = employee[0]
                alasan = employee[1]
                
                query = """
                    SELECT 
                        e.id, 
                        e.nik,
                        e.full_name,
                        e.status,
                        DATE(e.birth_date) AS birth_date,
                        d.department,
                        e.location,
                        e.division,
                        p.position,
                        e.education_major,
                        e.education_institute,
                        e.company_history,
                        e.position_history
                    FROM employee e 
                    JOIN department d ON e.department = d.id 
                    JOIN position p ON p.id = e.position
                    WHERE e.id = %s
                """
                cursor.execute(query, (employee_id,))
                employee_details = cursor.fetchone()
                
                if employee_details:
                    employee_details['alasan'] = alasan
                    employees.append([employee_details])
            print("TESTINGGG", employees)
            return employees
    except Exception as e:
        print(f"Error retrieving data: {e}")
        return []
    finally:
        if connection:
            connection.close()
            
def regex_think_and_candidates(result_text):
    """
    Fungsi ini menerima string result_text (output LLM) dengan format:
    
    <think>Your calculated thought here...</think>
    1. ID: 519
       Alasan: Samuel Becker memiliki latar belakang ...
    2. ID: 12
       Alasan: Mikayla Smith berada di Departemen Finance ...
       
    Fungsi ini mengembalikan tuple (think_text, candidate_list) dimana:
    - think_text adalah teks lengkap termasuk tag <think>...</think> (atau string kosong jika tidak ada)
    - candidate_list adalah list of lists dengan format:
      [[519, "Samuel Becker memiliki latar belakang ..."],
       [12, "Mikayla Smith berada di Departemen Finance ..."],
       ...]
    """
    # Ekstrak think_text beserta tag <think>...</think>
    think_match = re.search(r"(<think>[\s\S]*?<\/think>)", result_text, flags=re.DOTALL)
    think_text = think_match.group(1).strip() if think_match else ""
    
    # Ekstrak kandidat menggunakan regex dengan mode multiline,
    # hanya mencocokkan baris yang dimulai dengan angka (sehingga tag <think> tidak ikut)
    pattern = r"(?m)^\d+\.\s*ID:\s*(\d+)\s*\n\s*Alasan:\s*(.*?)(?=\n\d+\.|$)"
    matches = re.findall(pattern, result_text, flags=re.DOTALL)
    candidate_list = [[int(id_str), alasan.strip()] for id_str, alasan in matches]
    
    return think_text, candidate_list

def regex_sugestion(data):
    # Jika data adalah string, coba parse sebagai JSON
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            return []  # Jika parsing gagal, kembalikan list kosong
    # Pastikan data sekarang adalah list
    if not isinstance(data, list):
        return []
    # Lakukan trim pada setiap elemen yang merupakan string
    return [s.strip() for s in data if isinstance(s, str)]

# Endpoint API untuk Pencarian Kandidat
@app.route('/search', methods=['POST'])
def search_candidates():
    try:
        data = request.get_json()
        user_query = data.get('query', '')
        
        if not user_query:
            return jsonify({"error": "Query tidak boleh kosong"}), 400
        print(user_query)
        # retriever = db.as_retriever(search_kwargs={"k": 50})
        filters = llm_filter.invoke(
            f"{filter_prompt_template} {user_query})"
        )
        print(filters.content)
        try:
            filters_dict = json.loads(filters.content)
        except Exception as e:
            print(f"Error parsing filter JSON: {e}")
            filters_dict = {}
        # filters = get_filter_from_prompt(user_query)
        # print("Filter yang diterapkan:", filters)

        search_kwargs = {"k": 50}
        
        if filters_dict:
            search_kwargs["filter"] = filters_dict

        retriever = db.as_retriever(search_kwargs=search_kwargs)

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
        case_information = f"{user_query} (Untuk Sekedar Informasi, Tanggal saat ini adalah {current_date})"
        
        # START OF SECOND LLM
        llm3 = ChatGroq(
            model='llama-3.1-8b-instant',
            api_key="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",
            temperature=0.3
        )
        topic = '''
            Anda adalah ahli prompting, Tugas Anda Adalah Menparafrase suatu prompt menjadi prompt yang lebih Baik dan jelas, Ubah menjadi kalimat perintah cari. Disini tugasmu hanya memperbaiki kalimatnya Bukan membuat kalimat baru dengan makna yang berbeda jangan menanyakan jumlah/hitung.

            format hanya jawaban saja
        '''
        prompt_template = f'''
        {topic} Prompt yang perlu diperbaiki: {case_information}
        '''
        
        prompt_obj = PromptTemplate.from_template(
            template=prompt_template
        )
            
        # Create and run the chain
        chain = prompt_obj | llm3
            
        # Get the response
        response2 = chain.invoke({"text": topic})
        
        print("INI LLM2", response2.content)
        # END OF SECOND LLM
        # START OF THIRD LLM
        response3 = qa_chain2.invoke({"query": response2.content})
        print("INI LLM 3: ", response3["result"])
        # END OF THIRD LLM
        result = qa_chain.invoke({"query": response2.content})
        think_text, candidates = regex_think_and_candidates(result["result"])
        print(think_text)
        candidates_array = get_array_employee(candidates)
        print(candidates_array)
        # Flatten array of arrays
        flattened_candidates = []
        for sublist in candidates_array:
            flattened_candidates.extend(sublist)
        
        print(flattened_candidates)
        response = {
            "suggestion": regex_sugestion(response3["result"]),
            "think": think_text,  # Digunakan pada chat untuk animasi
            "answer": flattened_candidates,  # Digunakan pada card
            "sources": [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata
                } for doc in result["source_documents"]
            ]
        }
        print(response['answer'])
        print(jsonify(response))
        if isinstance(regex_sugestion(response3["result"]), list):
           print("benar array", regex_sugestion(response3["result"]))
        else:
            print("bukan array")
        print("Ini response raw: ", result["result"])
        return jsonify(response)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5025, debug=True)
