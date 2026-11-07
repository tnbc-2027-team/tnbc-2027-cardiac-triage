// ECG v1 - ESP32 Dev Module (ESP32-WROOM-32 DevKitC)
// Board:   hardware/ecg-schematic-v1 (AD8232 front end, Rev A), header J2 "TO_MCU"
// Wiring:  see ../PINOUT.md
// Port of the Arduino Uno v1 sketch (Rushil, 2026-11-06). Same behaviour,
// ESP32 pins only.
//
// Streams the raw ECG reading over Serial at 115200 baud, one value per line
// (0-4095, the ESP32 ADC is 12-bit). Prints '!' instead when an electrode is
// off (LO+ or LO- high). View it with Tools > Serial Plotter in the Arduino IDE.
//
// Arduino IDE: Tools > Board > esp32 > "ESP32 Dev Module"

const int ECG_OUT_PIN = 36; // GPIO36 (VP), ADC1. Use ADC1 pins only: ADC2 stops working when Wi-Fi is on
const int LO_PLUS_PIN = 32; // leads-off detection LO+
const int LO_MINUS_PIN = 33; // leads-off detection LO-

void setup() {
  Serial.begin(115200);

  pinMode(LO_PLUS_PIN, INPUT);
  pinMode(LO_MINUS_PIN, INPUT);

  analogReadResolution(12);                       // 0-4095
  analogSetPinAttenuation(ECG_OUT_PIN, ADC_11db); // full 0-3.3 V range
}

void loop() {
  if ((digitalRead(LO_MINUS_PIN) == HIGH) || (digitalRead(LO_PLUS_PIN) == HIGH)) {
    Serial.println('!');
  } else {
    Serial.println(analogRead(ECG_OUT_PIN));
  }
}
