import os
import sqlite3
import paho.mqtt.client as mqtt

from dotenv import load_dotenv

load_dotenv()

USERNAME = os.getenv("MQTT_USERNAME")
PASSWORD = os.getenv("MQTT_PASSWORD")
BROKER_URL = "app.galerna.eus"
BROKER_PORT = 8883

class subscriber:

    def __init__(self):

        self.client = mqtt.Client()
        self.client.tls_set()
        self.conn = sqlite3.connect(
            "data/iot.db",
            check_same_thread=False
        )

        self._init_db()

    def _init_db(self):

        cursor = self.conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS telemetry (
            topic TEXT PRIMARY KEY,
            value TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        self.conn.commit()

    def on_connect(self, client, userdata, flags, rc):

        print(f"[MQTT] Connected with result code {rc}")

        client.subscribe("urpekari/telem/#")

        print("[MQTT] Subscribed to urpekari/telem/#")

        cursor = self.conn.cursor()

        cursor.execute("""
        INSERT INTO telemetry(topic, value, timestamp)
        VALUES(
            'urpekari/telem/MQT-BROKER',
            ?,
            CURRENT_TIMESTAMP
        )
        ON CONFLICT(topic)
        DO UPDATE SET
            value=?,
            timestamp=CURRENT_TIMESTAMP
        """, (
            f"{BROKER_URL}:{BROKER_PORT}",
            f"{BROKER_URL}:{BROKER_PORT}"
        ))

        self.conn.commit()

    def on_disconnect(self, client, userdata, rc):

        print(f"[MQTT] Disconnected ({rc})")

        cursor = self.conn.cursor()

        cursor.execute("""
        INSERT INTO telemetry(topic, value, timestamp)
        VALUES(
            'urpekari/telem/MQT-BROKER',
            ?,
            CURRENT_TIMESTAMP
        )
        ON CONFLICT(topic)
        DO UPDATE SET
            value=?,
            timestamp=CURRENT_TIMESTAMP
        """, (
            f"{BROKER_URL}:{BROKER_PORT} (OFFLINE)",
            f"{BROKER_URL}:{BROKER_PORT} (OFFLINE)"
        ))

        self.conn.commit()

    def on_message(self, client, userdata, msg):

        topic = msg.topic
        value = msg.payload.decode().strip()

        print(f"[MQTT] {topic} -> {value}")

        cursor = self.conn.cursor()

        cursor.execute("""
        INSERT INTO telemetry(topic, value, timestamp)
        VALUES(?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(topic)
        DO UPDATE SET
            value=excluded.value,
            timestamp=CURRENT_TIMESTAMP
        """, (topic, value))

        self.conn.commit()

        cursor.execute("""
        INSERT INTO telemetry(topic, value, timestamp)
        VALUES(
            'urpekari/telem/MQT-LATEST',
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        )
        ON CONFLICT(topic)
        DO UPDATE SET
            value=CURRENT_TIMESTAMP,
            timestamp=CURRENT_TIMESTAMP
        """)

        self.conn.commit()

    def start_listening(self):

        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message

        if USERNAME and PASSWORD:
            self.client.username_pw_set(
                USERNAME,
                PASSWORD
            )

        # Local broker
        self.client.connect(
            BROKER_URL,
            BROKER_PORT,
            60
        )

        print("[MQTT] Starting loop")

        self.client.loop_forever()


if __name__ == "__main__":

    sub = subscriber()
    sub.start_listening()