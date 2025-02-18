import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from database import get_data_from_mysql
from config import VECTOR_DB_DIR

def build_vector_store():
    """
    Membuat database vektor baru dari data MySQL.
    """
    embedding_function = HuggingFaceEmbeddings(model_name="sentence-transformers/multi-qa-mpnet-base-dot-v1")
    
    # Hapus database lama jika ada
    if os.path.exists(VECTOR_DB_DIR):
        try:
            Chroma(persist_directory=VECTOR_DB_DIR, embedding_function=embedding_function).delete_collection()
            print(f"Database lama di {VECTOR_DB_DIR} dihapus.")
        except Exception as e:
            print(f"Gagal menghapus database lama: {e}")
    
    documents = get_data_from_mysql()
    try:
        db = Chroma.from_documents(
            documents=documents,
            embedding=embedding_function,
            persist_directory=VECTOR_DB_DIR
        )
        print(f"Database vektor dibuat dengan {db._collection.count()} dokumen.")
        return db
    except Exception as e:
        print(f"Error building vector database: {e}")
        raise

def update_vector_store():
    """
    Memperbarui database vektor dengan data terbaru.
    """
    embedding_function = HuggingFaceEmbeddings(model_name="sentence-transformers/multi-qa-mpnet-base-dot-v1")
    documents = get_data_from_mysql()
    
    if not documents:
        print("Tidak ada data baru untuk memperbarui vector store.")
        return None
    
    if os.path.exists(VECTOR_DB_DIR):
        try:
            chroma_db = Chroma(persist_directory=VECTOR_DB_DIR, embedding_function=embedding_function)
            chroma_db.delete_collection()
            print(f"Database lama di {VECTOR_DB_DIR} dihapus.")
        except Exception as e:
            print(f"Gagal menghapus database lama: {e}")
    
    try:
        db = Chroma.from_documents(
            documents=documents,
            embedding=embedding_function,
            persist_directory=VECTOR_DB_DIR
        )
        print(f"Database vektor diperbarui dengan {len(documents)} dokumen.")
        return db
    except Exception as e:
        print(f"Error updating vector database: {e}")
        raise
