from flask import Blueprint, request, jsonify
from datetime import datetime
from prompts import prompt, prompt2, prompt3
from llm_utils import llm, llm2, llm_filter, get_llm3
from vector_store import update_vector_store, build_vector_store
from langchain.chains import RetrievalQA
from langchain_huggingface import HuggingFaceEmbeddings
from utils import regex_think_and_candidates, regex_sugestion
from database import get_employee_by_ids

import json

routes = Blueprint('routes', __name__)

# Bangun vector store saat inisialisasi
db = build_vector_store()
embedding_function = HuggingFaceEmbeddings(model_name="sentence-transformers/multi-qa-mpnet-base-dot-v1")
retriever = db.as_retriever(search_kwargs={"k": 10})
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    chain_type_kwargs={"prompt": prompt},
    return_source_documents=True
)

@routes.route('/update', methods=['GET'])
def update_vector_db():
    updated_db = update_vector_store()
    if updated_db is None:
        return jsonify({"message": "Tidak ada data baru"}), 200
    
    # Memperbarui retriever dan qa_chain global
    global retriever, qa_chain, db
    db = updated_db
    retriever = db.as_retriever(search_kwargs={"k": 10})
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=True
    )
    return jsonify({"message": "ChromaDB diperbarui dan retriever diperbarui."}), 200

@routes.route('/search', methods=['POST'])
def search_candidates():
    try:
        data = request.get_json()
        user_query = data.get('query', '')
        if not user_query:
            return jsonify({"error": "Query tidak boleh kosong"}), 400

        # Generate filter menggunakan llm_filter dengan prompt filter
        filters = llm_filter.invoke(f"{prompt3.template} {user_query}")
        try:
            filters_dict = json.loads(filters.content)
        except Exception as e:
            print(f"Error parsing filter JSON: {e}")
            filters_dict = {}

        search_kwargs = {"k": 50}
        if filters_dict:
            search_kwargs["filter"] = filters_dict

        local_retriever = db.as_retriever(search_kwargs=search_kwargs)
        qa_chain_local = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=local_retriever,
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=True
        )
        qa_chain2 = RetrievalQA.from_chain_type(
            llm=llm2,
            chain_type="stuff",
            retriever=local_retriever,
            chain_type_kwargs={"prompt": prompt2},
            return_source_documents=True
        )
        current_date = datetime.now().strftime("%d %B %Y")
        case_information = f"{user_query} (Untuk Sekedar Informasi, Tanggal saat ini adalah {current_date})"
        
        # LLM ketiga untuk memperbaiki prompt (parafrase)
        llm3 = get_llm3()
        topic = '''
            Anda adalah ahli prompting, Tugas Anda Adalah Menparafrase suatu prompt menjadi prompt yang lebih Baik dan jelas, Ubah menjadi kalimat perintah cari. Disini tugasmu hanya memperbaiki kalimatnya Bukan membuat kalimat baru dengan makna yang berbeda jangan menanyakan jumlah/hitung.

            format hanya jawaban saja
        '''
        prompt_template = f'''
        {topic} Prompt yang perlu diperbaiki: {case_information}
        '''
        from langchain.prompts import PromptTemplate
        prompt_obj = PromptTemplate.from_template(template=prompt_template)
        chain = prompt_obj | llm3
        response2 = chain.invoke({"text": topic})
        
        response3 = qa_chain2.invoke({"query": response2.content})
        result = qa_chain_local.invoke({"query": response2.content})
        think_text, candidates = regex_think_and_candidates(result["result"])
        candidates_array = get_employee_by_ids(candidates)
        
        response = {
            "suggestion": regex_sugestion(response3["result"]),
            "think": think_text,
            "answer": candidates_array,
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
