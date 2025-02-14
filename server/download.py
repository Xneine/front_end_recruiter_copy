import pandas as pd
# from IPython.display import FileLink  # Hanya jika ingin menampilkan link download (misal di Jupyter Notebook)

# Fungsi untuk mengekstrak department dari label dengan format "level_department_job"
def extract_department(label):
    parts = label.split('_', 2)  # Bagi string dengan maksimal 2 pemisah
    if len(parts) == 3:
        return parts[1].strip()
    else:
        return label.strip()

# Baca file Excel input (asumsi file memiliki header pada baris pertama dan index di kolom pertama)
input_file = 'input.xlsx'
df = pd.read_excel(input_file, index_col=0)

# Tampilkan DataFrame asli (optional)
print("DataFrame Asli:")
print(df)

# Ubah label index dan kolom dengan mengekstrak department
df.index = df.index.map(extract_department)
df.columns = df.columns.map(extract_department)

# Kelompokkan baris berdasarkan department dan jumlahkan nilainya
df_grouped_rows = df.groupby(df.index).sum()

# Kelompokkan kolom berdasarkan department dan jumlahkan nilainya (grouping pada axis=1)
df_grouped = df_grouped_rows.groupby(df_grouped_rows.columns, axis=1).sum()

# Tampilkan DataFrame hasil grouping (optional)
print("\nDataFrame setelah grouping berdasarkan department:")
print(df_grouped)

# Simpan hasilnya ke file Excel baru
output_file = 'aggregated_by_department.xlsx'
df_grouped.to_excel(output_file)

print("\nFile output telah disimpan sebagai:", output_file)

# # Jika dijalankan di Jupyter Notebook, berikut cara membuat link download:
# try:
#     display(FileLink(output_file))
# except Exception:
#     pass
