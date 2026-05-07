from dotenv import load_dotenv
import random
from datetime import datetime, timedelta
from pymongo import MongoClient
import random, os

load_dotenv()

client = MongoClient("mongodb://localhost:27017/")
db = client[os.getenv("DB_NAME")]
col = db["suhu_mesin"]  

machines = ["M01", "M02", "M03", "M04"]

def generate_data():
    return {
        "machine_id": random.choice(machines),
        "timestamp": datetime.now() - timedelta(minutes=random.randint(0,120)),
        "temperature": round(random.uniform(60, 100), 2),
        "distance": round(random.uniform(0, 200), 2),
        "light_intensity": random.randint(0, 1000),
        "vibration": round(random.uniform(0, 5), 2),
        "infrared_detected": random.choice([True, False]),
        "ultrasonic_distance": round(random.uniform(2, 400), 2)
    }

for _ in range(100):
    data = generate_data()
    col.insert_one(data)