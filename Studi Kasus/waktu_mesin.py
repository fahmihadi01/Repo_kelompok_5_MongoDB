from datetime import datetime, timedelta
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["studi_kasus_kel5"]
col = db["suhu_mesin"]

one_hour_ago = datetime.now() - timedelta(hours=1)

pipeline = [
    {
        "$match": {
            "timestamp": { "$gte": one_hour_ago }
        }
    },
    {
        "$group": {
            "_id": "$machine_id",
            "max_temperature": { "$max": "$temperature" }
        }
    },
    {
        "$match": {
            "max_temperature": { "$gt": 90 }
        }
    }
]

result = list(col.aggregate(pipeline))

for r in result:
    print(f"Mesin: {r['_id']} | Suhu maksimum: {r['max_temperature']} °C")