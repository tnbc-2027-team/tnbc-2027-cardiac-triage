/*
 * spo2_v1_esp32.ino
 * TMU BioDesign Team — Portable Cardiac Triage System
 *
 * Standalone SpO2 sensor firmware (MAX30102 + ESP32).
 * Streams RAW red/IR PPG samples over USB serial as CSV.
 * No SpO2/HR calculation here on purpose — this is the acquisition layer.
 * Processing comes later and will consume exactly this data format.
 *
 * Board:   ESP32 DevKit (ESP32-WROOM-32)
 * Sensor:  MAX30102 breakout module
 * Library: "SparkFun MAX3010x Pulse and Proximity Sensor Library"
 *          (Arduino Library Manager)
 *
 * Wiring (see ../PINOUT.md):
 *   MAX30102 VIN -> ESP32 3V3
 *   MAX30102 GND -> ESP32 GND
 *   MAX30102 SDA -> ESP32 GPIO21
 *   MAX30102 SCL -> ESP32 GPIO22
 *   MAX30102 INT -> not connected (unused in this version)
 *
 * Output CSV columns:
 *   sample_idx, t_ms, red, ir, finger
 *   - sample_idx : running sample counter (0, 1, 2, ...)
 *   - t_ms       : sample time = sample_idx * 1000 / OUTPUT_RATE_HZ
 *                  (derived from the sensor's own sample clock, not from
 *                  when the ESP32 happened to read the FIFO)
 *   - red, ir    : raw 18-bit ADC counts
 *   - finger     : 1 if IR level suggests a finger is on the sensor, else 0
 */

#include <Wire.h>
#include "MAX30105.h"   // SparkFun library; works for MAX30102 too

// ---------------- Configuration ----------------

// Serial
static const uint32_t SERIAL_BAUD = 115200;

// I2C pins (ESP32 DevKit defaults)
static const int PIN_SDA = 21;
static const int PIN_SCL = 22;

// Sensor settings
//   Internal sample rate 400 Hz, averaged 4 samples -> 100 Hz output.
static const byte LED_BRIGHTNESS = 60;     // 0-255 (0 = off, 255 ≈ 50 mA). Lower if signal saturates.
static const byte SAMPLE_AVERAGE = 4;      // 1, 2, 4, 8, 16, 32
static const byte LED_MODE       = 2;      // 2 = Red + IR (SpO2 mode)
static const int  SAMPLE_RATE    = 400;    // 50, 100, 200, 400, 800, 1000, 1600, 3200
static const int  PULSE_WIDTH    = 411;    // 69, 118, 215, 411 us (411 = 18-bit resolution)
static const int  ADC_RANGE      = 16384;  // 2048, 4096, 8192, 16384

static const float OUTPUT_RATE_HZ = (float)SAMPLE_RATE / SAMPLE_AVERAGE;  // 100 Hz

// Finger detection: IR counts below this mean no finger / poor contact.
// Tune for your module + clip (check the raw IR values with and without a finger).
static const uint32_t FINGER_IR_THRESHOLD = 50000;

// ---------------- Globals ----------------

MAX30105 sensor;
uint32_t sampleIdx = 0;

// ---------------- Setup ----------------

void setup() {
  Serial.begin(SERIAL_BAUD);
  delay(200);

  Wire.begin(PIN_SDA, PIN_SCL);

  if (!sensor.begin(Wire, I2C_SPEED_FAST)) {   // 400 kHz I2C
    Serial.println("# ERROR: MAX30102 not found. Check wiring and power.");
    while (true) {
      delay(1000);
    }
  }

  sensor.setup(LED_BRIGHTNESS, SAMPLE_AVERAGE, LED_MODE,
               SAMPLE_RATE, PULSE_WIDTH, ADC_RANGE);

  // Lines starting with '#' are comments/metadata; parsers should skip them.
  Serial.print("# MAX30102 ready. Output rate (Hz): ");
  Serial.println(OUTPUT_RATE_HZ);
  Serial.println("sample_idx,t_ms,red,ir,finger");
}

// ---------------- Loop ----------------
// The sensor samples on its own clock and stores samples in its FIFO.
// check() pulls any new samples into the library's buffer without blocking
// for long; we then print every sample it collected. This pattern keeps the
// main loop free for other sensors (e.g. ECG) in the combined firmware.

void loop() {
  sensor.check();

  while (sensor.available()) {
    uint32_t red = sensor.getFIFORed();
    uint32_t ir  = sensor.getFIFOIR();
    sensor.nextSample();

    uint32_t t_ms  = (uint32_t)(sampleIdx * 1000.0f / OUTPUT_RATE_HZ);
    uint8_t finger = (ir >= FINGER_IR_THRESHOLD) ? 1 : 0;

    Serial.print(sampleIdx);  Serial.print(',');
    Serial.print(t_ms);       Serial.print(',');
    Serial.print(red);        Serial.print(',');
    Serial.print(ir);         Serial.print(',');
    Serial.println(finger);

    sampleIdx++;
  }
}
