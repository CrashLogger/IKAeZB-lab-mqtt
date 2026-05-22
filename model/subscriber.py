import paho.mqtt.client as mqtt
import ssl

class subscriber:
    def __init__(self, topics, location_queue, air_queue, rad_queue):
        self.topics = topics
        self.location_queue = location_queue
        self.air_queue = air_queue
        self.rad_queue = rad_queue
        self.client = mqtt.Client()

    def on_connect(self, client, userdata, flags, rc):
        for topic in self.topics:
            client.subscribe(topic)

    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode()

        #CSV formatuak oso errazak dira zatitzeko zorionez
        if msg.topic == "topic/location":
            lat, lon, alt = map(float, payload.split(','))
            self.location_queue.put({
                "lat": lat,
                "lon": lon,
                "altitude": alt,
                "roll": 0,
                "pitch": 0
            })
        elif msg.topic == "topic/radiacode":
            dose, count = map(float, payload.split(','))
            self.rad_queue.put({"rad": dose, "cps": count})
        elif msg.topic == "topic/meteo":
            temperature, pressure, humidity = map(float, payload.split(','))
            self.air_queue.put({"temp": temperature, "pres": pressure, "humid": humidity})

    def start_listening(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

#        self.client.tls_set(ca_certs=None,cert_reqs=ssl.CERT_REQUIRED,tls_version=ssl.PROTOCOL_TLSv1_2)
#        self.client.connect("127.0.0.1", 8883, 60)
        self.client.connect("127.0.0.1", 1883, 60)
        self.client.loop_forever()