#include <WiFi.h>
#include <PubSubClient.h>
#include <TinyGPS++.h>
#include <HardwareSerial.h>

//  WiFi & MQTT Config 
const char* WIFI_SSID = "Portuetxe24";
const char* WIFI_PASS = "ErEkIk27Ct";
const char* MQTT_BROKER = "192.168.1.142"; // e.g., "192.168.1.100"
const char* MQTT_TOPIC = "topic/location";
const char* CLIENT_ID = "ESP32-TESTBED";

//  GPS Config (UART) 
HardwareSerial gpsSerial(2); // UART2: RX=GPIO16, TX=GPIO17
TinyGPSPlus gps;
const uint32_t GPS_BAUD = 9600; // Default for NEO-6M

//  MQTT Client 
WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);

void setup() {
  Serial.begin(115200);
  gpsSerial.begin(GPS_BAUD, SERIAL_8N1, 16, 17); // RX, TX pins

  // Connect to WiFi
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  Serial.print("Connecting to WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected!");

  // Set MQTT server and callback
  mqttClient.setServer(MQTT_BROKER, 1883);
  mqttClient.setCallback([](char* topic, byte* payload, unsigned int length) {
    Serial.print("MQTT Message: ");
    Serial.write(payload, length);
    Serial.println();
  });

  // Connect to MQTT
  reconnectMQTT();
}

void loop() {
  // Feed GPS data to TinyGPS++
  while (gpsSerial.available() > 0) {
    gps.encode(gpsSerial.read());
  }

  // Publish if new GPS data is available
  if (gps.location.isValid() && gps.altitude.isValid()) {
    if (!mqttClient.connected()) reconnectMQTT();
    mqttClient.loop();

    // Format CSV: latitude,longitude,altitude
    char csv[100];
    snprintf(csv, sizeof(csv), "%.6f,%.6f,%.2f",
             gps.location.lat(), gps.location.lng(), gps.altitude.meters());

    Serial.print("Publishing: ");
    Serial.println(csv);

    mqttClient.publish(MQTT_TOPIC, csv);
  }

  delay(1000); // Publish every second (adjust as needed)
}

void reconnectMQTT() {
  while (!mqttClient.connected()) {
    Serial.print("Connecting to MQTT...");
    if (mqttClient.connect(CLIENT_ID)) {
      Serial.println("Connected!");
      mqttClient.subscribe("gps/debug"); // Optional: for testing
    } else {
      Serial.print("Failed (rc=");
      Serial.print(mqttClient.state());
      Serial.println("). Retrying in 5s...");
      delay(5000);
    }
  }
}