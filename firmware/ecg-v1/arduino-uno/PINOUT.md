# ECG v1 pinout: Arduino Uno

ECG board: `hardware/ecg-schematic-v1` (AD8232, Rev A), header **J2 "TO_MCU"**.
Sketch: `ecg_v1_uno/ecg_v1_uno.ino`

| J2 pin | Signal | Arduino Uno pin | Notes |
|---|---|---|---|
| 1 | GND | GND | |
| 2 | VDD_3V3 | **3.3V** | Do not use 5V. The AD8232 is a 3.3 V part. |
| 3 | ECG_OUT | **A0** | Analog ECG signal |
| 4 | LO− | **D10** | Leads-off detect (HIGH = electrode off) |
| 5 | LO+ | **D11** | Leads-off detect (HIGH = electrode off) |
| 6 | SDN | **3.3V** | Shutdown, active LOW. Tie HIGH so the chip stays on. Don't leave it floating. |

Electrodes plug into J1 or the 3.5 mm jack J3: RA = right arm, LA = left arm, RL = right leg.

## Notes

- The Uno's ADC runs on 5 V, but ECG_OUT only swings 0 to 3.3 V, so readings top out around 675 of 1023. That's expected (our 2026-11-06 data peaks around 660).
- LO+ and LO− are 3.3 V logic. The Uno reads them as HIGH, but only just.
- Serial: 115200 baud, one value per line, `!` when an electrode is off.
