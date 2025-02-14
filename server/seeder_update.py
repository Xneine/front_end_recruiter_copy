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

        # Buat batch update untuk meningkatkan efisiensi
        update_query = """
            UPDATE employee 
            SET department = %s, position = %s
            WHERE id = %s;
        """

        data_to_update = []
        for i in range(11, 896):
            data_to_update.append((random.randint(1, 140), random.randint(4, 13), i))

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
