from datetime import datetime, timedelta, UTC
from pymongo import MongoClient, errors

try:
    client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=3000)

    client.admin.command("ping")

    db = client["studi_kasus_kel5"]
    col = db["suhu_mesin"]

    one_hour_ago = datetime.now(UTC) - timedelta(hours=1)

    latest_pipeline = [
        {"$sort": {"machine_id": 1, "timestamp": -1}},
        {
            "$group": {
                "_id": "$machine_id",
                "latest_temp": {"$first": "$temperature"},
                "latest_time": {"$first": "$timestamp"}
            }
        },
        {"$sort": {"_id": 1}}
    ]
    latest_data = list(col.aggregate(latest_pipeline))

    alarm_pipeline = [
        {"$match": {"timestamp": {"$gte": one_hour_ago}}},
        {
            "$group": {
                "_id": "$machine_id",
                "max_temp": {"$max": "$temperature"}
            }
        },
        {"$match": {"max_temp": {"$gt": 90}}}
    ]
    alarm_data = list(col.aggregate(alarm_pipeline))

    avg_pipeline = [
        {"$match": {"timestamp": {"$gte": one_hour_ago}}},
        {
            "$group": {
                "_id": "$machine_id",
                "avg_temp": {"$avg": "$temperature"}
            }
        },
        {"$sort": {"_id": 1}}
    ]
    avg_data = list(col.aggregate(avg_pipeline))

    print("\n=== SUHU TERKINI PER MESIN ===")
    for d in latest_data:
        print(f"Mesin {d['_id']} | Suhu: {d['latest_temp']:.2f}°C | Waktu: {d['latest_time']}")

    print("\n=== MESIN DENGAN ALARM (>90°C) ===")
    if not alarm_data:
        print("Tidak ada mesin yang memicu alarm")
    else:
        for d in alarm_data:
            print(f"Mesin {d['_id']} | Suhu maksimum: {d['max_temp']:.2f}°C")

    print("\n=== RATA-RATA SUHU PER MESIN ===")
    for d in avg_data:
        print(f"Mesin {d['_id']} | Rata-rata suhu: {d['avg_temp']:.2f}°C")

    if alarm_data:
        with open("alarm.log", "a") as f:
            for d in alarm_data:
                log_line = (
                    f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                    f"Mesin={d['_id']} | MaxTemp={d['max_temp']:.2f}°C\n"
                )
                f.write(log_line)


except errors.ServerSelectionTimeoutError:
    print("Sistem monitoring OFFLINE: MongoDB tidak dapat dihubungi.")
except Exception:
    print("Terjadi gangguan pada sistem monitoring.")
