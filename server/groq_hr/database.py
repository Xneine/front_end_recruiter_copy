from config import DB_CONFIG
import pymysql
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def get_data_from_mysql():
    """
    Mengambil data dari MySQL dan mengembalikan list objek Document.
    """
    connection = None
    try:
        connection = pymysql.connect(**DB_CONFIG)
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

            # Pecah teks panjang menjadi chunk
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
            documents = []
            for row in results:
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
                chunks = text_splitter.split_text(text)
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
                for chunk in chunks:
                    documents.append(Document(page_content=chunk, metadata=metadata))
            return documents
    except Exception as e:
        print(f"Error retrieving data: {e}")
        return []
    finally:
        if connection:
            connection.close()

def get_employee_by_ids(employees):
    """
    Mengambil detail karyawan berdasarkan daftar kandidat.
    Setiap kandidat adalah tuple [id, alasan].
    """
    connection = None
    results = []
    try:
        connection = pymysql.connect(**DB_CONFIG)
        with connection.cursor() as cursor:
            for employee in employees:
                employee_id, alasan = employee
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
                    results.append(employee_details)
        return results
    except Exception as e:
        print(f"Error retrieving employee data: {e}")
        return []
    finally:
        if connection:
            connection.close()
