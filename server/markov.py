import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# Memuat file Excel
def load_matrix(file_path):
    df = pd.read_excel(file_path, index_col=0)
    df.columns = df.columns.astype(str).str.strip()
    df.index = df.index.astype(str).str.strip()
    return df

# Load DataFrame (asumsi menggunakan fungsi `load_matrix()`)
file_path = "matrix.xlsx"
markov_matrix = load_matrix(file_path)

# Pastikan tipe data DataFrame adalah float
markov_matrix = markov_matrix.astype(float)

epsilon = 1e-6  # Nilai kecil untuk normalisasi

# Perbaiki state yang tidak memiliki transisi
for index, row in markov_matrix.iterrows():
    if np.isclose(np.sum(row), 1.0):  # State absorbing tetap dipertahankan
        continue
    elif np.isclose(np.sum(row), 0.0):  # Jika tidak ada transisi, tambahkan probabilitas kecil
        markov_matrix.loc[index] = np.ones(len(row), dtype=np.float64) * epsilon
        markov_matrix.loc[index, index] = 1 - (epsilon * (len(row) - 1))  # Menjaga normalisasi

# Pastikan matriks transisi tetap valid (jumlah setiap baris harus 1)
markov_matrix = markov_matrix.div(markov_matrix.sum(axis=1), axis=0)

# Konversi DataFrame ke NumPy sebelum matrix power
markov_numpy = markov_matrix.to_numpy()

print("Baris:", len(markov_matrix), "Kolom:", len(markov_matrix.columns))
# print(markov_matrix.iloc[:, 0])

# Nama baris yang dicari
kurangi_depart = "Worker_Yard Operations Department_Gate Operator"
tambah_depart= "Worker_Yard Operations Department_Tallyman Loading Discharge"

tambah = ["Worker_Yard Operations Department_Tallyman Loading Discharge", "Worker_Yard Operations Department_Gate Operator"]

# nanti input dan output berupa 2 array dictionary yang berisi value nama seperti Worker_Yard Operations Department_Gate Operator dan quantity (integer lebih dari 1)

# Pastikan nama baris ada dalam DataFrame
if kurangi_depart in markov_matrix.index:
    # Ambil baris sebagai array
    search_array = markov_matrix.loc[kurangi_depart].to_numpy()
    print(search_array)
    # Menerapkan matrix power (misalnya 1 langkah)
    mc_p2 = np.linalg.matrix_power(markov_numpy, 1)

    # Menghitung hasil dengan np.dot()
    hasil = np.dot(search_array, mc_p2)

    # Pastikan state 'tambah_depart' ada di kolom DataFrame (diasumsikan urutan kolom sama dengan urutan di matrix)
    if tambah_depart in markov_matrix.columns:
        # Dapatkan posisi index dari 'tambah_depart' dalam kolom DataFrame
        new_posisi = []
        new_probabilty = []
        for i in tambah:
            new_posisi.append((markov_matrix.columns.get_loc(i)))
            temp = hasil[(markov_matrix.columns.get_loc(i))]
            new_probabilty.append((temp))
            print(f"Probabilitas menuju state '{i}': {temp}")
        # posisi = markov_matrix.columns.get_loc(tambah_depart)
        # Ambil nilai probability dari vektor hasil menggunakan posisi tersebut
        # probability_value = hasil[posisi]
        
        # print(f"Probabilitas menuju state '{tambah_depart}': {probability_value}")
    else:
        print(f"State '{tambah_depart}' tidak ditemukan dalam kolom DataFrame.")


    # # Tampilkan hasil
    # print(f"Hasil untuk state '{hasil}':")
    # print(hasil)
else:
    print(f"State '{kurangi_depart}' tidak ditemukan dalam DataFrame.")
