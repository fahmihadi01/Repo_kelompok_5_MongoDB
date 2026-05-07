import os
from dotenv import load_dotenv
import paho.mqtt.client as mqtt

load_dotenv()

def get_mqtt_client():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.username_pw_set(
        os.getenv("MQTT_USER"),
        os.getenv("MQTT_PASS")
    )

    client.connect(
        os.getenv("MQTT_BROKER"),
        int(os.getenv("MQTT_PORT")),
        60
    )

    return client