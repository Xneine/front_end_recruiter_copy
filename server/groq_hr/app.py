from flask import Flask, request, jsonify
import os
import pandas as pd
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

app = Flask(__name__)

# 1. Konversi Excel ke CSV
excel_path = 'dummy candidate selection.xlsx'
csv_path = 'dummy candidate selection_pd.csv'

if not os.path.exists(excel_path):
    raise FileNotFoundError(f"File Excel tidak ditemukan: {excel_path}")

data = pd.read_excel(excel_path)
data.to_csv(csv_path, index=False, sep=';')

# 2. Setup Embedding dan Vector Database
embedding_function = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
db_name = "vector_db"

# Hapus database lama jika ada
if os.path.exists(db_name):
    try:
        Chroma(persist_directory=db_name, embedding_function=embedding_function).delete_collection()
        print(f"Database lama di {db_name} dihapus")
    except Exception as e:
        print(f"Gagal menghapus database: {e}")
        
# Bangun database baru
loader = CSVLoader(csv_path, encoding="windows-1252")
documents = loader.load()
db = Chroma.from_documents(
    documents=documents,
    embedding=embedding_function,
    persist_directory=db_name
)
print(f"Database vektor dibuat dengan {db._collection.count()} dokumen")

# 3. Setup Model LLM
llm = ChatGroq(
    model_name='llama-3.3-70b-specdec',
    api_key="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",  # Ambil dari environment variable
    temperature=0.7
)

# 4. Konfigurasi Template Prompt
template = """
**Instruksi:**
Anda adalah asisten pencari kandidat. Gunakan data berikut untuk menjawab:
{context}

**Pertanyaan:**
{question}

Format jawaban:
1. ID: [ID]
   Tanggal Lahir: [BIRTH_DATE]
   Universitas: [EDUCATION_INSTITUTE]
   Jurusan: [EDUCATION_MAJOR]
   IPK: [EDUCATION_GPA]
   Pengalaman: [EXPERIENCE_POSITION]
"""

prompt = PromptTemplate(
    template=template,
    input_variables=["context", "question"]
)

# 5. Setup RAG Chain
retriever = db.as_retriever(search_kwargs={"k": 50})
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    chain_type_kwargs={"prompt": prompt},
    return_source_documents=True
)

# Endpoint API
# ============
@app.route('/search', methods=['POST'])
def search_candidates():
    try:
        # Ambil query dari request
        data = request.get_json()
        user_query = data.get('query', '')
        
        if not user_query:
            return jsonify({"error": "Query tidak boleh kosong"}), 400
        
        # Eksekusi pencarian
        result = qa_chain.invoke({"query": user_query})
        
        # Format respons
        response = {
            "answer": result["result"],
            "sources": [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata
                } for doc in result["source_documents"]
            ]
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
