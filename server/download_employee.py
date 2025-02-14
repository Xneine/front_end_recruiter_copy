from sqlalchemy import create_engine
import pandas as pd

# Buat koneksi menggunakan SQLAlchemy
engine = create_engine("mysql+pymysql://root:@localhost/markovkaryawandb")

# Query SQL
query = """                
                SELECT 
                    id, 
                    nik,
                    full_name,
                    status,
                    birth_date,
                    department,
                    location,
                    division,
                    position,
                    education_major,
                    education_institute,
                    company_history,
                    position_history
                FROM employee3"""
# query = """                
#                 SELECT 
#                     e.id, 
#                     e.nik,
#                     e.full_name,
#                     e.status,
#                     e.birth_date,
#                     d.department,
#                     e.location,
#                     e.division,
#                     p.position,
#                     e.education_major,
#                     e.education_institute,
#                     e.company_history,
#                     e.position_history
#                 FROM employee3 e JOIN department d ON d.id = e.department JOIN position p ON p.id = e.position"""

# Baca data ke dalam DataFrame
df = pd.read_sql(query, engine)

# Simpan DataFrame ke file Excel
df.to_excel("data_output2.xlsx", index=False, engine="openpyxl")

print("Data berhasil diekspor ke data_output.xlsx")
