import paho.mqtt.client as mqtt
import ssl
import sqlite3

from dotenv import load_dotenv
import os
load_dotenv()

USERNAME = os.getenv('MQTT_USERNAME')
PASSWORD = os.getenv('MQTT_PASSWORD')

class subscriber:
    def __init__(self, topics, location_queue, air_queue, rad_queue):
        self.topics = topics
        self.location_queue = location_queue
        self.air_queue = air_queue
        self.rad_queue = rad_queue
        self.client = mqtt.Client()
        self.conn = sqlite3.connect('data/iot.db', check_same_thread=False)
        self._init_db()

    def _init_db(self):
        cursor = self.conn.cursor()
        cursor.executescript('''
            CREATE TABLE IF NOT EXISTS location_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                lat REAL, lon REAL, altitude REAL, roll REAL, pitch REAL
            );
            CREATE TABLE IF NOT EXISTS radiation_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                rad REAL, cps REAL
            );
            CREATE TABLE IF NOT EXISTS meteo_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                temp REAL, pres REAL, humid REAL
            );
        ''')
        self.conn.commit()

    def on_connect(self, client, userdata, flags, rc):
        for topic in self.topics:
            client.subscribe(topic)

    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode()
        cursor = self.conn.cursor()

        if msg.topic == "topic/location":
            lat, lon, alt = map(float, payload.split(','))
            cursor.execute('''
                INSERT INTO location_log (lat, lon, altitude, roll, pitch)
                VALUES (?, ?, ?, 0, 0)
            ''', (lat, lon, alt))
        elif msg.topic == "topic/radiacode":
            dose, count = map(float, payload.split(','))
            cursor.execute('''
                INSERT INTO radiation_log (rad, cps) VALUES (?, ?)
            ''', (dose, count))
        elif msg.topic == "topic/meteo":
            temp, pres, humid = map(float, payload.split(','))
            cursor.execute('''
                INSERT INTO meteo_log (temp, pres, humid) VALUES (?, ?, ?)
            ''', (temp, pres, humid))
        self.conn.commit()

    def start_listening(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.tls_set(ca_certs=None,cert_reqs=ssl.CERT_REQUIRED,tls_version=ssl.PROTOCOL_TLSv1_2)
        self.client.username_pw_set("USERNAME", "PASSWORD")
        self.client.connect("galerna.eus", 8883, 60)
        #self.client.connect("127.0.0.1", 1883, 60)
        self.client.loop_forever()