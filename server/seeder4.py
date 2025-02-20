from faker import Faker
import random
import pymysql

faker = Faker()
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

def mysqlconnect():
    try:
        # Buat koneksi tanpa `with` agar tetap terbuka selama proses
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password="",
            db='markovkaryawandb',
        )
        cur = conn.cursor()
        query = """ 
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
                        WHERE e.id = 134
                        GROUP BY e.id;
        """
        cur.execute(query)
        employee_id = cur.fetchall()
        # data_education = []
        # for i in employee_id:
        #     if(random.randint(1,10) == 1):
        #         data_education.append((i[0], random.randint(1,30), random.randint(1,30), 3))
        #     else:
        #         continue
        #     # print(i, random.randint(1,3))

        # update_query = """
        #     INSERT INTO employee_education VALUES(null, %s, %s, %s, %s)
        # """
        # cur.executemany(update_query, data_education)
        # conn.commit()
        print(employee_id)
        cur.close()
        conn.close()

    except Exception as e:
        print(f"Database connection error: {e}")

if __name__ == "__main__":
    mysqlconnect()
