from cryptography.fernet import Fernet

KEY = b"tA8f6ZdBrrn6Nj_6Oa1e8xaIycxeFCPTjD2AdTsucw4="

fernet = Fernet(KEY)

def encrypt_data(data: dict) -> str:
    """Enkripsi dict menjadi string ciphertext"""
    import json
    json_bytes = json.dumps(data).encode("utf-8")
    return fernet.encrypt(json_bytes).decode("utf-8")

def decrypt_data(ciphertext: str) -> dict:
    """Dekripsi string ciphertext kembali ke dict"""
    import json
    json_bytes = fernet.decrypt(ciphertext.encode("utf-8"))
    return json.loads(json_bytes.decode("utf-8"))