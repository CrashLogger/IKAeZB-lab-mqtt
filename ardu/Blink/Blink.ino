#include <WiFi.h>
#include <PubSubClient.h>
#include <TinyGPS++.h>
#include <HardwareSerial.h>
#include <WiFiClientSecure.h>

// --- WiFi ---
const char* WIFI_SSID = "Portuetxe24";
const char* WIFI_PASS = "ErEkIk27Ct";

// --- MQTT Broker information ---
const char* MQTT_BROKER = "galerna.eus"; // e.g., "mqtt.example.com"
const int MQTT_PORT = 8883;
const char* MQTT_USER = "telekes";
const char* MQTT_PASS = "t3l3k35";

// --- Topics where we are the publisher ---
const char* GPS_TOPIC = "topic/location";

// --- Topics where we are subscribers
const char* RUNNING_LIGHTS_TOPIC = "car/lights";
const char* INDICATOR_L_TOPIC = "car/indicatorL";
const char* INDICATOR_R_TOPIC = "car/indicatorR";
const char* MOTORS_L_TOPIC = "car/motorL";
const char* MOTORS_R_TOPIC = "car/motorR";

uint8_t running_lights_val = 0;
uint8_t indicator_l_val = 0;
uint8_t indicator_r_val = 0;
uint8_t motor_l_val = 0;
uint8_t motor_r_val = 0;

const char* CLIENT_ID = "iot-slave";

// --- GPS Config (UART2) ---
static const int RXPin = 13, TXPin = 12;
static const uint32_t GPSBaud = 9600;
HardwareSerial ss(2);
TinyGPSPlus gps;

// --- MQTT Client with TLS ---
WiFiClientSecure wifiClient;
PubSubClient mqttClient(wifiClient);

// --- SCHEDULERS ---
uint32_t last_mqtt_tx = 0;
uint32_t last_rx = 0;
uint32_t last_indicator = 0;
// · · ·
uint32_t period_mqtt_tx = 1000;
uint32_t period_rx = 10;
uint32_t period_indicator = 425;

uint32_t uptime_millis = 0;

// --- PINS ---
#define INDICATOR_R_PIN 18
#define INDICATOR_L_PIN 15
#define HEADLIGHTS_PIN 17
#define TAILLIGHTS_PIN 16

// --- Indicator state ---
bool indicator_state = false;

void reconnectMQTT() {
  Serial.print("Connecting to MQTT...");
  if (mqttClient.connect(CLIENT_ID, MQTT_USER, MQTT_PASS)) {
    Serial.println("Connected!");
    mqttClient.subscribe(RUNNING_LIGHTS_TOPIC);
    mqttClient.subscribe(INDICATOR_L_TOPIC);
    mqttClient.subscribe(INDICATOR_R_TOPIC);
    mqttClient.subscribe(MOTORS_L_TOPIC);
    mqttClient.subscribe(MOTORS_R_TOPIC);
  } else {
    Serial.print("Failed (rc=");
    Serial.print(mqttClient.state());
    Serial.println(")");
  }
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
  char msg[100];
  memcpy(msg, payload, length);
  msg[length] = '\0';

  uint8_t value = atoi(msg);

  if(strcmp(topic, RUNNING_LIGHTS_TOPIC) == 0){
    running_lights_val = value;
  }
  else if((strcmp(topic, MOTORS_L_TOPIC) == 0)){
    motor_l_val = value;
  }
  else if((strcmp(topic, MOTORS_R_TOPIC) == 0)){
    motor_r_val = value;
  }
  else if((strcmp(topic, INDICATOR_L_TOPIC) == 0)){
    indicator_l_val = value;
  }
  else if((strcmp(topic, INDICATOR_R_TOPIC) == 0)){
    indicator_r_val = value;
  }
}

void setup() {
  Serial.begin(115200);
  ss.begin(GPSBaud, SERIAL_8N1, RXPin, TXPin);

  //Setting up the lighting arrangement
  pinMode(TAILLIGHTS_PIN, OUTPUT);
  pinMode(HEADLIGHTS_PIN, OUTPUT);
  pinMode(INDICATOR_L_PIN, OUTPUT);
  pinMode(INDICATOR_R_PIN, OUTPUT);

  // Connect to the given WiFi SSID
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  Serial.print("Connecting to WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected!");

  // Configure TLS - I'm not using setCACert because that's a pain in the ass
  // Trust me bro™ technology right here
  wifiClient.setInsecure();

  // Set MQTT broker
  mqttClient.setServer(MQTT_BROKER, MQTT_PORT);

  mqttClient.setCallback(mqttCallback);
  reconnectMQTT();
}

void loop() {
  uptime_millis = millis();
  while (ss.available() > 0) {
    gps.encode(ss.read());
  }

  analogWrite(HEADLIGHTS_PIN,running_lights_val);
  analogWrite(TAILLIGHTS_PIN,running_lights_val);
  digitalWrite(INDICATOR_L_PIN, (bool)indicator_l_val & indicator_state);
  digitalWrite(INDICATOR_R_PIN, (bool)indicator_r_val & indicator_state);

  if (uptime_millis >= period_indicator + last_indicator) {
    last_indicator = millis();
    indicator_state = !indicator_state;
  }  

  if (millis() > 5000 && gps.charsProcessed() < 10) {
    Serial.println(F("No GPS detected: check wiring."));
    while(true);
  }

  if (uptime_millis >= period_rx + last_rx) {
    last_rx = millis();
    mqttClient.loop();
  }

  if(uptime_millis >= (last_mqtt_tx + period_mqtt_tx)){
    last_mqtt_tx = millis();
    if (gps.location.isValid() && gps.altitude.isValid()) {
        char csv[100];
        //Not interested in doxxing myself 24/7 thank you!!
        //snprintf(csv, sizeof(csv), "%.6f,%.6f,%.6f", gps.location.lat(), gps.location.lng(), gps.altitude.meters());
        snprintf(csv, sizeof(csv), "%.2f,%.2f,%.2f", gps.location.lat(), gps.location.lng(), gps.altitude.meters());
        Serial.print("Publishing: ");
        Serial.println(csv);
        mqttClient.publish(GPS_TOPIC, csv);
    }
    else{
    Serial.println(F("Still waiting for GPS lock!"));
    }
  }

}
