from faker import Faker
import random
from datetime import datetime, timedelta
import pymysql

faker = Faker()

# List custom untuk department
departments = ['Account Receivable Core Department', 'Account Receivable Department', 'Accounting Department', 'Administrasi Depo', 'Administration Department', 'BOD', 'Branch Class B East', 'Branch Class C East', 'Branches Management Department', 'Bulk Management Department', 'Bunker And Overseas Purchasing Department', 'Business Development Department', 'Car Carrier', 'Chinese Desk', 'Commercial Department', 'Commercial Jakarta Department', 'Continuous Improvement Department', 'Core Department', 'Corporate Account Department', 'Corporate Communication', 'Customer Service Department', 'DFF', 'DPA Department', 'DPL', 'Facility Electrical Department', 'Feeder, SOC & International Trade Sales Department', 'Finance & Administration Department', 'Finance Department', 'Finance and Accounting Department', 'Fleet Department', 'Fleet Jakarta Department', 'General Accounting Department', 'General Affairs Department', 'Global Freight & Logistics', 'HR System and Information Department', 'HRBP Department', 'Health Safety Environment Department', 'Heavy Equipment Department', 'Human Capital', 'Human Capital & Corporate Affairs', 'Human Capital & Corporate Affairs Jakarta Department', 'Human Capital Department', 'Human Resources Change Agent', 'Human Resources Change Agent Department', 'Human Resources Development Department', 'Human Resources Development NPTI', 'Human Resources Information System', 'Human Resources Information System Department', 'Human Resources Service Excellence Department', 'Human Resources System Department', 'Human Resources and General Affair Department', 'IT Application Development Department', 'IT DevOps Department', 'IT Development Department', 'IT Network & Infrastructure Department', 'IT Planning & Business Process Department', 'IT Software Development & Business Process Analyst Department', 'Industrial Relation Department', 'Information Technology & Technical Support Dept', 'Information Technology System Department', 'Inland Service Department', 'Insurance & Claim Department', 'Internal Audit Department', 'Learning And Development Department', 'Legal & Claim Department', 'Legal Department', 'Logistic Department', 'Machinery Department', 'Management Accounting Department', 'Management Trainee', 'Management Trainee Department', 'Marketing & Communication Department', 'Marketing Department', 'Marketing Department (Domestic Trade)', 'Marketing Department (International Trade)', 'Marketing Inbound & SOC Department', 'Medical Department', 'National Sales Department', 'Nautical Department', 'Office of Corporate Communication', 'Office of Strategy Management Department', 'Operation', 'Operation Jakarta Department', 'Operations & Administration Core Department', 'Operations Department', 'Operations Jakarta Department', 'Operations NPTI', 'Organization Development Department', 'Organizational & Talent Management', 'Outports Department', 'Overseas Purchasing Department', 'Performance Excellence Department', 'Personnel And Industrial Relation Department', 'Personnel Branches Department', 'Personnel Surabaya Department', 'Process Excellence Department', 'Procurement Department', 'Production Department', 'Project and Building Maintenance Department', 'Public Affair, Industrial & Employee Relation Department', 'Public Affairs & Relation Department', 'Public Affairs And Security Department', 'Public Affairs Department', 'Purchasing Departement', 'Quality Assurance & Continuous Improvement', 'Quality Assurance Department', 'Quality Control Departement', 'Quality Health Safety And Enviroment Department', 'R', 'Recruitment Department', 'Regional East Department', 'Regional West Department', 'Rendal Department', 'Sales Department', 'Sales Inbound & SOC Department', 'Salvage Department', 'Sekretariat', 'Services Department', 'Services Department (Domestic Trade)', 'Services Department (International Trade)', 'Ship Operation Department (N)', 'Ship Operations Department', 'Ship Personnel Management Department', 'Special Project', 'Special Project & Corporate Representative', 'Strategy Development And Implementation Department', 'Surabaya Branch Office Department', 'TPIL', 'Talent Management & OD Department', 'Talent Management Department', 'Technical Department', 'Terminal Operator Surabaya', 'Trade Department', 'Treasury Department', 'Vendor Management', 'Workshop Department', 'Yard Development Department', 'Yard Operations Department', 'Yield Excellent Service Department']
position = ['President Director', 'Director', 'Expatriat', 'General Manager', 'Senior Manager', 'Middle Manager', 'Junior Manager', 'Team Leader', 'Senior Staff', 'Staff', 'Worker', 'Trainee', 'Non Grade']
universitas = [
    "Universitas Indonesia",
    "Institut Teknologi Bandung",
    "Universitas Gadjah Mada",
    "Institut Pertanian Bogor",
    "Universitas Airlangga",
    "Universitas Brawijaya",
    "Universitas Diponegoro",
    "Universitas Padjadjaran",
    "Universitas Sebelas Maret",
    "Universitas Hasanuddin",
    "Universitas Sumatera Utara",
    "Institut Teknologi Sepuluh Nopember",
    "Universitas Negeri Yogyakarta",
    "Universitas Negeri Malang",
    "Universitas Negeri Jakarta",
    "Universitas Andalas",
    "Universitas Pendidikan Indonesia",
    "Universitas Islam Indonesia",
    "Universitas Muhammadiyah Yogyakarta",
    "Universitas Syiah Kuala",
    "Universitas Udayana",
    "Universitas Jember",
    "Universitas Riau",
    "Universitas Lampung",
    "Universitas Negeri Surabaya",
    "Universitas Negeri Semarang",
    "Universitas Negeri Medan",
    "Universitas Negeri Makassar",
    "Universitas Jenderal Soedirman",
    "Universitas Trisakti"
]
jurusan = [
    "Teknik Informatika",
    "Sistem Informasi",
    "Ilmu Komputer",
    "Teknik Elektro",
    "Teknik Mesin",
    "Teknik Industri",
    "Teknik Sipil",
    "Teknik Kimia",
    "Kedokteran",
    "Farmasi",
    "Keperawatan",
    "Ilmu Hukum",
    "Manajemen",
    "Akuntansi",
    "Ekonomi Pembangunan",
    "Hubungan Internasional",
    "Administrasi Bisnis",
    "Psikologi",
    "Sastra Inggris",
    "Sastra Jepang",
    "Pendidikan Matematika",
    "Pendidikan Biologi",
    "Pendidikan Fisika",
    "Pendidikan Kimia",
    "Arsitektur",
    "Desain Komunikasi Visual",
    "Desain Interior",
    "Ilmu Komunikasi",
    "Antropologi",
    "Sosiologi"
]
count = [1,2,3,4,5]
data = []
for i in departments:
    for _ in range(random.choice(count)):
        data.append({
            'nik': faker.uuid4(),
            'email': faker.email(),
            'password': 'hashed_password',  # Untuk testing, gunakan string hash sederhana
            'full_name': faker.name(),
            'birth_date': faker.date_of_birth(minimum_age=20, maximum_age=60),
            'department': random.choice(departments),  # Pilih acak dari list
            'location': faker.city(),
            'division': random.choice(["HCCA","FAD","OPS","FLEET","CMD"]),
            'position': random.choice(position),
            'education_major': random.choice(jurusan),
            'education_institute': random.choice(universitas),
            'company_history': faker.company(),
            'position_history': random.choice(position),
            'session': faker.uuid4(),
            'otp_code': faker.random_number(digits=6),
            'otp_expiration': (datetime.now() + timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S'),
            'last_activity': faker.date_time_this_month(),
            'session_exp': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')
        })
        
def save_dummy(cur, conn, data):
    try:
        insert_query = """
            INSERT INTO employee (nik, email, password, full_name, birth_date, department, location, position, education_major, education_institute, company_history, position_history, session, otp_code, otp_expiration, last_activity, session_exp)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        # Siapkan data untuk di-insert
        data_to_insert = [
            (row['nik'], row['email'],row['password'],row['full_name'],row['birth_date'],row['department'],row['location'],row['position'],row['education_major'],row['education_institute'],row['company_history'],row['position_history'],row['session'],row['otp_code'],row['otp_expiration'],row['last_activity'],row['session_exp'])  # Hubungkan dengan id di tabel posts
            for row in data
        ]

        # Eksekusi query untuk batch insert
        cur.executemany(insert_query, data_to_insert)
        conn.commit()

        print(f"{len(data)} semua history postingan berhasil disimpan.")

    except Exception as e:
        print(f"Terjadi kesalahan saat menyimpan history postingan: {e}")
              
def mysqlconnect():
    try:
        with pymysql.connect(
            host='localhost',
            user='root',
            password="",
            db='markovkaryawandb',
        ) as conn:
            with conn.cursor() as cur:
                save_dummy(cur=cur, conn=conn, data=data)
    except Exception as e:
        print(f"Database connection error: {e}")

if __name__ == "__main__":
    mysqlconnect()



