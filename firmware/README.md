# Firmware

Code that runs on the microcontroller: SpO₂ / heart rate, blood pressure, and the High / Medium / Low triage logic. It has to run fully offline on battery.

Write down here which board version the code works with, and update it when pins or addresses change.

## Current firmware

| Folder | What it does | Works with board | Microcontroller |
|---|---|---|---|
| `ecg-v1/` | Raw ECG over serial, leads-off detection | `hardware/ecg-schematic-v1` (Rev A) | Arduino Uno (tested), ESP32 Dev Module (not yet tested) |
| `spo2-v1/` | Raw red/IR PPG at 100 Hz over serial, finger detection | MAX30102 breakout module | ESP32 Dev Module (not yet tested) |

New version of something? Copy its folder to the next number (for example `ecg-v2/`) and note the change in that folder's README. See `ecg-v1/README.md`.
