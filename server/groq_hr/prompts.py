from langchain.prompts import PromptTemplate

template = """
Instruksi:
Anda adalah asisten pencari kandidat perusahaan. Pilih kandidat terbaik berdasarkan data berikut:
{context}

Perintah:
{question}

Catatan:
- Pilih hanya kandidat yang 100 persen memenuhi setiap kriteria (Perhatikan department, divisi, posisi dan semua perintah user. Pastikan outputnya 100 persen memenuhi kriteria).
- Jangan menambahkan informasi di luar data yang diberikan.
- Setiap ID harus unik dalam satu output.
- Cek ulang agar hasil sesuai dengan permintaan.
- Tidak apa-apa apabila jumlah yang relevan tidak sesuai dengan jumlah yang diminta. Berikan output seadanya

Format Jawaban (Buat sesuai persis sesuai formatnya(nomer, ID, Alasan). Perhatikan huruf kapitalnya juga -> ID, Alasan):
1. ID: [id karyawan pada database]
   Alasan: [Alasan pemilihan kandidat]

Jika tidak ada yang cocok atau perintah diluar cangkupan pencarian kandidat perusahaan, jawab:
"Tidak ditemukan kandidat yang sesuai."
"""

template2 = """
**Instruksi:**
Anda adalah sistem rekomendasi kalimat perintah yang bertugas membuat 3 perintah serupa berdasarkan perintah berikut:

**Perintah:**
{question}

**Kriteria untuk Perintah baru berdasarkan data berikut**:
{context}
- Harus tetap dalam konteks pencarian kandidat.
- Jangan memasukkan informasi tanggal dalam perintah baru.
- Format dalam kalimat perintah

**Format Jawaban (Gunakan format JSON array, tidak perlu tambahan lain):**
["perintah1", "perintah2", "perintah3"]
"""

filter_prompt_template = """
Instruksi: 
Anda adalah sistem ekstraksi filter divisi dan posisi. Ambil divisi dan posisi dari perintah pengguna.
Jika tidak disebutkan, kosongkan saja. Khusus untuk posisi, analisis dan buat filternya sesuai list position dibawah, Apabila memang tidak ada yang sesuai, jangan outputkan position. divisi atau posisi yang lebih dari 1 gunakan $in. Hanya tampilkan dalam format JSON.
Division = ["FAD", "FLEET", "HCCA", "OPS", "CMD"]
position = ['President Director', 'Director', 'Expatriat', 'General Manager', 'Senior Manager', 'Middle Manager', 'Junior Manager', 'Team Leader', 'Senior Staff', 'Staff', 'Worker', 'Trainee', 'Non Grade']
Contoh:
- Input: "Cari MANAGER IT di divisi FAD"
  Output: {"$and": [{"division": {"$eq": "FAD"}}, {"position": {"$in": ["General Manager", "Senior Manager", "Middle Manager", "Junior Manager"]}}]}

- Input: "Tampilkan kandidat staff IT di HCCA atau OPS"
  Output: {"$and": [{"division": {"$in": ["HCCA","OPS"]}}, {"position": {"$in": ["Senior Staff", "Staff"]}}]}

- Input: "Cari kandidat department ANALYST"
  Output: {}
    
Jawaban (Hanya JSON):
Perintah:
"""

prompt = PromptTemplate(
    template=template,
    input_variables=["context", "question"]
)

prompt2 = PromptTemplate(
    template=template2,
    input_variables=["context", "question"]
)

prompt3 = PromptTemplate(
    template=filter_prompt_template,
    input_variables=["question"]
)
