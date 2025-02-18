import re
import json

def regex_think_and_candidates(result_text):
    """
    Menerima string result_text dengan format:
    
    <think>Your calculated thought here...</think>
    1. ID: 519
       Alasan: Samuel Becker memiliki latar belakang ...
    2. ID: 12
       Alasan: Mikayla Smith berada di Departemen Finance ...
       
    Mengembalikan tuple (think_text, candidate_list) di mana:
    - think_text adalah teks dengan tag <think> (atau string kosong jika tidak ada)
    - candidate_list adalah list list dengan format: [[519, "alasan"], ...]
    """
    think_match = re.search(r"(<think>[\s\S]*?<\/think>)", result_text, flags=re.DOTALL)
    think_text = think_match.group(1).strip() if think_match else ""
    pattern = r"(?m)^\d+\.\s*ID:\s*(\d+)\s*\n\s*Alasan:\s*(.*?)(?=\n\d+\.|$)"
    matches = re.findall(pattern, result_text, flags=re.DOTALL)
    candidate_list = [[int(id_str), alasan.strip()] for id_str, alasan in matches]
    return think_text, candidate_list

def regex_sugestion(data):
    """
    Mengubah string JSON menjadi list perintah.
    """
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            return []
    if not isinstance(data, list):
        return []
    return [s.strip() for s in data if isinstance(s, str)]
