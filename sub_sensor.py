import json
import os
import paho.mqtt.client as mqtt
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC = os.getenv("MQTT_TOPIC")
MQTT_USER = os.getenv("MQTT_USER")
MQTT_PASS = os.getenv("MQTT_PASS")

MONGO_HOST = os.getenv("MONGO_HOST")
MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASS = os.getenv("MONGO_PASS")
MONGO_DB = os.getenv("MONGO_DB")

COLLECTION_DATA = os.getenv("COLLECTION_DATA", "sensor_tomat")
COLLECTION_ALERT = os.getenv("COLLECTION_ALERT", "alert")

# --- BUILD MongoDB URI ---
if MONGO_USER and MONGO_PASS:
    MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/"
else:
    MONGO_URI = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/"

# --- KONEKSI KE MONGODB ---
try:
    mongo_client = MongoClient(MONGO_URI)
    # Test koneksi
    mongo_client.admin.command('ping')
    print(f"[INFO] Koneksi MongoDB berhasil ke {MONGO_HOST}:{MONGO_PORT}")
except Exception as e:
    print(f"[ERROR] Gagal koneksi MongoDB: {e}")
    exit(1)

db = mongo_client[MONGO_DB]
col_data = db[COLLECTION_DATA]
col_alert = db[COLLECTION_ALERT]

def on_connect(client, rc):
    if rc == 0:
        print(f"[INFO] MQTT Connected ke {MQTT_BROKER}:{MQTT_PORT}")
        client.subscribe(MQTT_TOPIC)
        print(f"[INFO] Subscribed ke topik: {MQTT_TOPIC}")
    else:
        print(f"[ERROR] Connect gagal, code: {rc}")

# MESSAGE CALLBACK
def on_message(msg):
    try:
        payload = msg.payload.decode()
        data = json.loads(payload)
        
        # Tambahkan timestamp jika tidak ada
        if "timestamp" not in data:
            data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 1. Simpan semua data ke MongoDB
        col_data.insert_one(data)
        print(f"[DB] Data tersimpan dari {data.get('lokasi')}")

        # --- LOGIKA ALERT SESUAI PARAMETER ZAIDAN ---
        alerts = []
        
        # A. Kelembapan Tanah (Buruk: <40% atau >80%)
        t_moisture = data.get("kelembapan_tanah", 0)
        if t_moisture < 40:
            alerts.append(f"Tanah terlalu kering! ({t_moisture}%)")
        elif t_moisture > 80:
            alerts.append(f"Tanah terlalu basah! ({t_moisture}%)")

        # B. Udara PM2.5 (Buruk: > 150)
        pm25 = data.get("pm25", 0)
        if pm25 > 150:
            alerts.append(f"Polusi udara berbahaya! (PM2.5: {pm25})")

        # C. Cahaya fc (Buruk: < 500 atau > 8000)
        cahaya = data.get("cahaya", 0)
        if cahaya < 500:
            alerts.append(f"Cahaya terlalu redup! ({cahaya} fc)")
        elif cahaya > 8000:
            alerts.append(f"Cahaya terlalu terik! ({cahaya} fc)")

        # D. Suhu (Buruk: < 15 atau > 32)
        suhu = data.get("suhu", 0)
        if suhu < 15:
            alerts.append(f"Suhu terlalu dingin! ({suhu} C)")
        elif suhu > 32:
            alerts.append(f"Suhu terlalu panas! ({suhu} C)")

        # 2. Jika ada alert, simpan ke koleksi 'alert'
        if alerts:
            alert_doc = {
                "lokasi": data.get("lokasi"),
                "timestamp": data.get("timestamp"),
                "nilai_sensor": {
                    "suhu": suhu,
                    "cahaya": cahaya,
                    "tanah": t_moisture,
                    "pm25": pm25
                },
                "pesan_alert": alerts
            }
            col_alert.insert_one(alert_doc)
            print(f"\n!!! ALERT TERDETEKSI !!!")
            for a in alerts:
                print(f" -> {a}")
            print("========================\n")

    except Exception as e:
        print("[ERROR] Gagal proses data:", e)

# MQTT SETUP
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.username_pw_set(MQTT_USER, MQTT_PASS)
client.on_connect = on_connect
client.on_message = on_message

# RUN
try:
    print(f"[INFO] Connecting Subscriber to Broker {MQTT_BROKER}:{MQTT_PORT}...")
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    
    import threading
    def wait_for_enter():
        input("Tekan ENTER untuk menghentikan subscriber...\n")
        client.disconnect()
        print("[INFO] Subscriber dihentikan")
    
    threading.Thread(target=wait_for_enter, daemon=True).start()
    
    client.loop_forever()
except KeyboardInterrupt:
    print("\n[INFO] Subscriber dihentikan oleh user")
except Exception as e:
    print("[ERROR] Sub mati:", e)
finally:
    mongo_client.close()
    print("[INFO] Koneksi MongoDB ditutup")