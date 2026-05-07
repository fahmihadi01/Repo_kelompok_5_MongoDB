from datetime import datetime, timedelta
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["studi_kasus_kel5"]
col = db["suhu_mesin"]

one_hour_ago = datetime.utcnow() - timedelta(hours=1)

pipeline = [
    {
        "$match": {
            "timestamp": { "$gte": one_hour_ago }
        }
    },
    {
        "$group": {
            "_id": "$machine_id",
            "avg_temperature": { "$avg": "$temperature" }
        }
    },
    {
        "$sort": { "_id": 1 }
    }
]

result = list(col.aggregate(pipeline))

for r in result:
    print(f"Mesin: {r['_id']}, Rata-rata suhu: {r['avg_temperature']:.2f} °C")