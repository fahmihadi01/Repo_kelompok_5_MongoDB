# Aplikasi Produksi MongoDB

Aplikasi ini digunakan untuk mengelola data produksi menggunakan Python dan MongoDB. Program berjalan dalam bentuk CLI (Command Line Interface).

## Fitur

1. Input data produksi
2. Menampilkan data berdasarkan mesin
3. Menghitung reject rate (>5%)
4. Export laporan bulanan ke CSV
5. Logging aktivitas ke file app.log

## Struktur Data

Setiap data produksi memiliki field:
- batch (string)
- mesin (string)
- jumlah (int)
- reject (int)
- tanggal (datetime)

## Cara Menjalankan

1. Aktifkan virtual environment:
.venv\Scripts\activate

2. Install dependency:
pip install pymongo pandas python-dotenv

3. Pastikan file `.env` ada:
MONGO_URI=your_connection_string
DB_NAME=nama_database

4. Jalankan program:
python app_produksi.py


## Contoh Input
Batch: B001
Mesin: CNC-01
Jumlah: 200
Reject: 10
Tanggal: 2026-05-01


## Output
- Data ditampilkan dalam bentuk tabel
- File laporan akan tersimpan dalam format CSV
- Log aktivitas tersimpan di app.log

## Catatan
- Format tanggal wajib: YYYY-MM-DD
- Reject rate dihitung: (reject / jumlah) * 100