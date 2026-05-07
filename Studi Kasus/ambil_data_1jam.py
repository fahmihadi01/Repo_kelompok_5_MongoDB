from datetime import datetime, timedelta
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["studi_kasus_kel5"]
col = db["suhu_mesin"]

one_hour_ago = datetime.now() - timedelta(hours=1)

data_1_jam = list(col.find({
    "timestamp": { "$gte": one_hour_ago }
}))

for d in data_1_jam:
    print("\n", d)