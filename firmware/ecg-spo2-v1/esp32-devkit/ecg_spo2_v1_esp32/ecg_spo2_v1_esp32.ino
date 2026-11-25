/*
 * ecg_spo2_v1_esp32.ino
 * TMU BioDesign Team - Portable Cardiac Triage System
 *
 * Combined ECG + SpO2 bench test: both sensors on one breadboard, one ESP32.
 *   ECG:  AD8232 board (hardware/ecg-schematic-v1, Rev A), same pins as ecg-v1
 *   SpO2: MAX30102 module (I2C), same pins and settings as spo2-v1
 * Wiring: see ../PINOUT.md
 *
 * Board:   Tools > Board > esp32 > "ESP32 Dev Module"
 * Library: "SparkFun MAX3010x Pulse and Proximity Sensor Library" (Library Manager)
 *
 * Output: Serial Monitor or Serial Plotter at 230400 baud.
 * One line per ECG sample (250 lines per second):
 *
 *   ecg:2051,ppg:812,spo2:98,hr:72
 *
 *   ecg   raw ECG reading (0-4095). 0 when an electrode is off.
 *   ppg   IR pulse wave with the slow (DC) level removed, flipped so beats point up,
 *         and shifted to sit below the ECG on the plotter. Flat at PPG_PLOT_OFFSET with no finger.
 *   spo2  SpO2 in %, recalculated every second from the last 4 s. 0 = no finger / not valid yet.
 *   hr    heart rate in bpm from the PPG, same timing. 0 = no finger / not valid yet.
 *
 * After placing a finger, SpO2 and HR take about 5 s to appear.
 *
 * Timing: the ECG is sampled at a fixed 250 Hz by its own FreeRTOS task on core 0,
 * so printing and I2C reads in loop() (core 1) can't delay ECG samples.
 * The MAX30102 samples on its own clock and buffers in its FIFO.
 */

#include <Wire.h>
#include "MAX30105.h"        // SparkFun library, works for the MAX30102
#include "spo2_algorithm.h"  // SparkFun/Maxim SpO2 + HR algorithm, same library

// ---------------- Configuration ----------------

static const uint32_t SERIAL_BAUD = 230400;  // 250 lines/s needs more than 115200

// ECG (AD8232) - same as ecg-v1
static const int ECG_OUT_PIN  = 36;  // GPIO36 (VP), ADC1
static const int LO_PLUS_PIN  = 32;  // leads-off LO+
static const int LO_MINUS_PIN = 33;  // leads-off LO-
static const uint32_t ECG_PERIOD_MS = 4;  // 250 Hz

// SpO2 (MAX30102) - same as spo2-v1
static const int PIN_SDA = 21;
static const int PIN_SCL = 22;
static const byte LED_BRIGHTNESS = 60;     // 0-255. Lower if IR saturates, raise if the pulse is tiny.
static const byte SAMPLE_AVERAGE = 4;
static const byte LED_MODE       = 2;      // Red + IR
static const int  SAMPLE_RATE    = 400;    // 400 Hz / 4 averaged = 100 Hz output
static const int  PULSE_WIDTH    = 411;    // 18-bit
static const int  ADC_RANGE      = 16384;
static const uint32_t FINGER_IR_THRESHOLD = 50000;  // IR below this = no finger

// PPG trace on the plotter
static const float PPG_PLOT_GAIN   = 1.0f;    // raise if the pulse wave looks flat
static const float PPG_PLOT_OFFSET = 800.0f;  // where the PPG sits on the plot
static const float PPG_DC_ALPHA    = 0.01f;   // DC tracking speed (~1 s at 100 Hz)

// SpO2/HR algorithm input: 25 Hz (every 4 PPG samples averaged), 4 s window, update every 1 s
static const int ALGO_DECIMATION = 4;
static const int ALGO_WINDOW     = 100;
static const int ALGO_STEP       = 25;

// ---------------- Globals ----------------

MAX30105 sensor;
QueueHandle_t ecgQueue;

uint32_t irWin[ALGO_WINDOW];
uint32_t redWin[ALGO_WINDOW];
int winCount = 0;
int newSinceCalc = 0;

uint32_t irSum = 0, redSum = 0;
int sumCount = 0;

float ppgDc = 0;
bool ppgDcReady = false;
int32_t ppgPlot = (int32_t)PPG_PLOT_OFFSET;

int32_t spo2Out = 0;
int32_t hrOut = 0;

// ---------------- ECG task (core 0, fixed 250 Hz) ----------------

void ecgTask(void *) {
  TickType_t lastWake = xTaskGetTickCount();
  for (;;) {
    vTaskDelayUntil(&lastWake, pdMS_TO_TICKS(ECG_PERIOD_MS));

    uint16_t value = 0;
    if (digitalRead(LO_PLUS_PIN) == LOW && digitalRead(LO_MINUS_PIN) == LOW) {
      value = analogRead(ECG_OUT_PIN);
    }
    xQueueSend(ecgQueue, &value, 0);
  }
}

// ---------------- SpO2 processing ----------------

void resetSpo2() {
  winCount = 0;
  newSinceCalc = 0;
  irSum = redSum = 0;
  sumCount = 0;
  ppgDcReady = false;
  ppgPlot = (int32_t)PPG_PLOT_OFFSET;
  spo2Out = 0;
  hrOut = 0;
}

void runAlgorithm() {
  int32_t spo2, hr;
  int8_t spo2Valid, hrValid;
  maxim_heart_rate_and_oxygen_saturation(irWin, ALGO_WINDOW, redWin,
                                         &spo2, &spo2Valid, &hr, &hrValid);

  spo2Out = (spo2Valid && spo2 >= 50 && spo2 <= 100) ? spo2 : 0;
  hrOut   = (hrValid && hr >= 30 && hr <= 220) ? hr : 0;
}

void handlePpgSample(uint32_t red, uint32_t ir) {
  if (ir < FINGER_IR_THRESHOLD) {
    resetSpo2();
    return;
  }

  // Pulse wave for the plotter
  if (!ppgDcReady) {
    ppgDc = (float)ir;
    ppgDcReady = true;
  }
  ppgDc += PPG_DC_ALPHA * ((float)ir - ppgDc);
  ppgPlot = (int32_t)(PPG_PLOT_OFFSET - PPG_PLOT_GAIN * ((float)ir - ppgDc));

  // Average down to 25 Hz for the algorithm
  irSum += ir;
  redSum += red;
  if (++sumCount < ALGO_DECIMATION) return;

  uint32_t irAvg = irSum / ALGO_DECIMATION;
  uint32_t redAvg = redSum / ALGO_DECIMATION;
  irSum = redSum = 0;
  sumCount = 0;

  if (winCount < ALGO_WINDOW) {
    irWin[winCount] = irAvg;
    redWin[winCount] = redAvg;
    winCount++;
  } else {
    memmove(irWin, irWin + 1, (ALGO_WINDOW - 1) * sizeof(uint32_t));
    memmove(redWin, redWin + 1, (ALGO_WINDOW - 1) * sizeof(uint32_t));
    irWin[ALGO_WINDOW - 1] = irAvg;
    redWin[ALGO_WINDOW - 1] = redAvg;
  }

  if (winCount == ALGO_WINDOW && ++newSinceCalc >= ALGO_STEP) {
    newSinceCalc = 0;
    runAlgorithm();
  }
}

// ---------------- Setup ----------------

void setup() {
  Serial.begin(SERIAL_BAUD);
  delay(200);

  pinMode(LO_PLUS_PIN, INPUT);
  pinMode(LO_MINUS_PIN, INPUT);
  analogReadResolution(12);
  analogSetPinAttenuation(ECG_OUT_PIN, ADC_11db);

  Wire.begin(PIN_SDA, PIN_SCL);
  if (!sensor.begin(Wire, I2C_SPEED_FAST)) {
    while (true) {
      Serial.println("ERROR: MAX30102 not found. Check SDA/SCL, 3V3 and GND.");
      delay(1000);
    }
  }
  sensor.setup(LED_BRIGHTNESS, SAMPLE_AVERAGE, LED_MODE,
               SAMPLE_RATE, PULSE_WIDTH, ADC_RANGE);

  ecgQueue = xQueueCreate(128, sizeof(uint16_t));
  xTaskCreatePinnedToCore(ecgTask, "ecg", 2048, nullptr, 2, nullptr, 0);
}

// ---------------- Loop (core 1) ----------------

void loop() {
  sensor.check();
  while (sensor.available()) {
    uint32_t red = sensor.getFIFORed();
    uint32_t ir  = sensor.getFIFOIR();
    sensor.nextSample();
    handlePpgSample(red, ir);
  }

  uint16_t ecg;
  while (xQueueReceive(ecgQueue, &ecg, 0) == pdTRUE) {
    Serial.printf("ecg:%u,ppg:%ld,spo2:%ld,hr:%ld\n",
                  ecg, (long)ppgPlot, (long)spo2Out, (long)hrOut);
  }

  delay(1);
}
