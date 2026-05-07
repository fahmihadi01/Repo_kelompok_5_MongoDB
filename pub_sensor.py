import time
import random
import json
from datetime import datetime
import paho.mqtt.client as mqtt
from pymongo import MongoClient
from koneksi import get_mqtt_client
from enkripsi import encrypt_data 

TOPIC = "sensor5"

client = get_mqtt_client()

lokasi = ["Lokasi A", "Lokasi B", "Lokasi C", "Lokasi D", "Lokasi E"]

#generate data
def generate_data( lokasi):

    if random.random() < 0.10:
        suhu = round(random.choice([
            random.uniform(0, 21),
            random.uniform(29, 40)
        ]), 2)
    else:
        suhu = round(random.uniform(22, 29),2)

    if random.random() < 0.05:
        pm25 = random.randint(50, 100)
    else:
        pm25 = random.randint(5, 50)
        
    return{
        "lokasi":random.choice(lokasi),
        "suhu": suhu,
        "cahaya": random.randint(900, 10000),
        "kelembapan_udara": random.randint(0, 100),
        "kelembapan_tanah": random.randint(0, 100),
        "pm25":pm25
    }

while True:
    data = generate_data(lokasi)
    payload = encrypt_data(data)

    client.publish(TOPIC,payload)
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Data terkirim ke topic '{TOPIC}':")
    print(f"  Lokasi          : {data['lokasi']}")
    print(f"  Suhu            : {data['suhu']} °C")
    print(f"  Cahaya          : {data['cahaya']} lux")
    print(f"  Kelembapan Udara: {data['kelembapan_udara']} %")
    print(f"  Kelembapan Tanah: {data['kelembapan_tanah']} %")
    print(f"  PM2.5           : {data['pm25']} µg/m³")
    print("-" * 40)
    time.sleep(5)
