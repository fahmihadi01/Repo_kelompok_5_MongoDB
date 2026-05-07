import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# =========================
# KONEKSI DATABASE
# =========================

MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    # Build URI dari komponen yang ada di .env
    MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
    MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
    MONGO_USER = os.getenv("MONGO_USER")
    MONGO_PASS = os.getenv("MONGO_PASS")
    
    if MONGO_USER and MONGO_PASS:
        MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/"
    else:
        MONGO_URI = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/"

DB_NAME = os.getenv("MONGO_DB")
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db["sensor_tomat"]

# =========================
# AMBIL DATA 24 JAM TERAKHIR
# =========================
waktu_sekarang = datetime.now()
waktu_24_jam = waktu_sekarang - timedelta(hours=24)

pipeline = [
    {
        "$addFields": {
            "timestamp_dt": {
                "$dateFromString": {
                    "dateString": "$timestamp",
                    "format": "%Y-%m-%d %H:%M:%S"
                }
            }
        }
    },
    {
        "$match": {
            "timestamp_dt": {"$gte": waktu_24_jam}
        }
    },
    {
        "$group": {
            "_id": {
                "lokasi": "$lokasi",
                "jam": {
                    "$dateToString": {
                        "format": "%Y-%m-%d %H:00",
                        "date": "$timestamp_dt"
                    }
                }
            },
            "avg_pm25": {"$avg": "$pm25"}
        }
    },
    {
        "$sort": {"_id.jam": 1}
    }
]

# =========================
# EKSEKUSI AGGREGATE
# =========================
data = list(collection.aggregate(pipeline))

if not data:
    print("Tidak ada data dalam 24 jam terakhir.")
    exit()

# =========================
# UBAH KE DATAFRAME
# =========================
df = pd.DataFrame(data)

# Pecah kolom _id
df["lokasi"] = df["_id"].apply(lambda x: x["lokasi"])
df["jam"] = df["_id"].apply(lambda x: x["jam"])

df = df.drop(columns=["_id"])

# =========================
# SIMPAN CSV
# =========================
df.to_csv("data_24jam.csv", index=False, sep=";")
print("Data berhasil disimpan ke data_24jam.csv")

# =========================
# PLOT GRAFIK
# =========================
plt.figure()

for lokasi in df["lokasi"].unique():
    subset = df[df["lokasi"] == lokasi]
    plt.plot(subset["jam"], subset["avg_pm25"], label=lokasi)

plt.xticks(rotation=45)
plt.xlabel("Waktu (per jam)")
plt.ylabel("Rata-rata PM2.5")
plt.title("Rata-rata PM2.5 per Jam (24 Jam Terakhir)")
plt.legend()

plt.tight_layout()
plt.savefig("dashboard_PM2.5.png")

print("Grafik berhasil disimpan sebagai dashboard_PM2.5.png")