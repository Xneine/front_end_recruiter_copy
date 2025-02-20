from faker import Faker
import random
import pymysql

faker = Faker()

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

        id_employee_query = """
            SELECT id FROM `employee` WHERE department >= 69 AND department <=76
        """
        cur.execute(id_employee_query)
        array_employee_id = cur.fetchall()
        for i in array_employee_id:
            print(i[0])
        # print(array_employee_id)
        # Buat batch update untuk meningkatkan efisiensi
        update_query = """
            INSERT INTO employee_certificate VALUES(null, %s, %s)
        """

        data_to_update = []
        for i in array_employee_id:
            # for j in range(1, random.randint(2, 3)):
            if (random.randint(1,3) == 1):
                continue
            else:
                data_to_update.append((i[0], 4))
            
        # Eksekusi batch update jika ada data
        if data_to_update:
            cur.executemany(update_query, data_to_update)
            conn.commit()

        print(f"Berhasil mengupdate {len(data_to_update)} data.")

        # Tutup koneksi setelah selesai
        cur.close()
        conn.close()

    except Exception as e:
        print(f"Database connection error: {e}")

if __name__ == "__main__":
    mysqlconnect()
