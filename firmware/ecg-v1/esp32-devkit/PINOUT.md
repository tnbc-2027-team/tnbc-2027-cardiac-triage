# ECG v1 pinout: ESP32 Dev Module

ECG board: `hardware/ecg-schematic-v1` (AD8232, Rev A), header **J2 "TO_MCU"**.
Microcontroller: ESP32 Dev Module (ESP32-WROOM-32 DevKitC, 38-pin).
Sketch: `ecg_v1_esp32/ecg_v1_esp32.ino`

| J2 pin | Signal | ESP32 pin | Notes |
|---|---|---|---|
| 1 | GND | GND | |
| 2 | VDD_3V3 | **3V3** | |
| 3 | ECG_OUT | **GPIO36 (VP)** | ADC1, input only |
| 4 | LO− | **GPIO33** | Leads-off detect (HIGH = electrode off) |
| 5 | LO+ | **GPIO32** | Leads-off detect (HIGH = electrode off) |
| 6 | SDN | **3V3** | Shutdown, active LOW. Tie HIGH so the chip stays on. Don't leave it floating. |

Electrodes plug into J1 or the 3.5 mm jack J3: RA = right arm, LA = left arm, RL = right leg.

## Notes

- Keep ECG_OUT on an **ADC1** pin (GPIO32 to 39). ADC2 pins stop working whenever Wi-Fi or Bluetooth is on.
- Everything is 3.3 V, so no level shifting is needed.
- Readings are 0 to 4095 (12-bit), so numbers won't match the Uno's 0 to 1023 data.
- If you change a pin, change it in both this table and the sketch.
