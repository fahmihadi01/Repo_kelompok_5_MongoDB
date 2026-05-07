import os
import logging
import pandas as pd
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# Koneksi ke MongoDB
client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("DB_NAME")]

# Set up logging
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Input Data
def input_data():
    try:
        batch = input("Batch: ")
        mesin = input("Mesin: ")
        jumlah = int(input("Jumlah: "))
        reject = int(input("Reject: "))
        tanggal = input ("Tanggal (YYYY-MM-DD): ")

        data = {
            "batch": batch,
            "mesin": mesin,
            "jumlah": jumlah,
            "reject": reject,
            "tanggal": datetime.strptime(tanggal, "%Y-%m-%d")
        }

        db.produksi.insert_one(data)
        logging.info(f"Inserted data: {data}")
        print("Data berhasil disimpan.\n")
    
    except Exception as e:
        logging.error(f"Error input data: {e}")
        print("Terjadi error!\n")

# Tampilan Data per mesin
def tampilkan_data_mesin():
    try:
        mesin = input("Masukkan nama mesin:")
        cursor = db.produksi.find({"mesin": mesin}, {"_id": 0})
        df = pd.DataFrame(list(cursor))

        if df.empty:
            print("Tidak ada data.\n")
        else:
            print(df, "\n")

        logging.info(f"Query data mesin: {mesin}")

    except Exception as e:
        logging.error(f"Error tampil mesin: {e}")


# Menghitung Reject Rate
def hitung_reject_rate():
    try:
        df = pd.DataFrame(list(db.produksi.aggregate([
            {
                "$project": {
                    "batch": 1,
                    "mesin": 1,
                    "reject_rate": {
                        "$multiply": [{"$divide":
                             ["$reject", "$jumlah"]}, 100]
                    }
                }
            },
            {"$match": {
                "reject_rate": {"$gt": 5}
            }}
        ])))

        print(df if not df.empty else "Tidak ada data\n")
        logging.info("Hitung reject rate")

    except Exception as e:
        logging.error(f"Error hitung reject rate: {e}")


# export data ke CSV bulanan
def export_laporan():
    try:
        bulan_tahun = input("Masukkan bulan dan tahun (MM-YYYY): ")
        bulan, tahun = bulan_tahun.split("-")
        df = pd.DataFrame(list(db.produksi.aggregate([
            {"$match": {
                "$expr": {
                    "$and": [
                        {"$eq": [{"$month": "$tanggal"}, int(bulan)]},
                        {"$eq": [{"$year": "$tanggal"}, int(tahun)]}
                        ]
                    }
                }
            },
            {
                "$group": {
                    "_id": "$mesin",
                    "total_jumlah": {"$sum": "$jumlah"},
                    "total_reject": {"$sum": "$reject"}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "mesin": "$_id",
                    "total_jumlah": 1,
                    "total_reject": 1
                }
            }
        ])))

        filename = f"Laporan_{bulan_tahun}.csv"
        df.to_csv(filename, index=False)

        print(f"Laporan berhasil diekspor ke {filename}\n")
        logging.info(f"Export laporan: {filename}")

    except Exception as e:
        logging.error(f"Error export laporan: {e}")

# Menu utama
def menu ():
    while True:
        print("===== Menu =====")
        print("1. Input Data")
        print("2. Tampilkan Per Mesin")
        print("3. Hitung Reject Rate")
        print("4. Export Laporan Bulanan")
        print("5. Keluar")

        pilihan = input("Pilih menu: ")
        if pilihan == "1":
            input_data()
        elif pilihan == "2":
            tampilkan_data_mesin()
        elif pilihan == "3":
            hitung_reject_rate()
        elif pilihan == "4":
            export_laporan()
        elif pilihan == "5":
            print("Keluar dari program.")
            break
        else:
            print("Pilihan tidak valid. Silakan coba lagi.\n")

# Jalankan program
if __name__ == "__main__":
    menu()