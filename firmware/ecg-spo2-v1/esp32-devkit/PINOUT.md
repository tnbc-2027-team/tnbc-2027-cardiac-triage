# ECG + SpO₂ v1 pinout: ESP32 Dev Module

One breadboard, one ESP32, both sensors.
Microcontroller: ESP32 Dev Module (ESP32-WROOM-32 DevKitC, 38-pin).
Sketch: `ecg_spo2_v1_esp32/ecg_spo2_v1_esp32.ino`

The pins are the same as `ecg-v1` and `spo2-v1`, so nothing clashes.

## ECG board (`hardware/ecg-schematic-v1`, header J2 "TO_MCU")

| J2 pin | Signal | ESP32 pin | Notes |
|---|---|---|---|
| 1 | GND | GND rail | |
| 2 | VDD_3V3 | 3V3 rail | |
| 3 | ECG_OUT | **GPIO36 (VP)** | ADC1, input only |
| 4 | LO− | **GPIO33** | HIGH = electrode off |
| 5 | LO+ | **GPIO32** | HIGH = electrode off |
| 6 | SDN | 3V3 rail | Keeps the AD8232 on. Don't leave it floating. |

Electrodes: RA = right arm, LA = left arm, RL = right leg (J1 or the 3.5 mm jack J3).

## SpO₂ module (MAX30102, I²C)

| Module pin | ESP32 pin | Notes |
|---|---|---|
| VIN | 3V3 rail | |
| GND | GND rail | |
| SDA | **GPIO21** | |
| SCL | **GPIO22** | |
| INT | not connected | Unused in v1 |

If your module's pins are labelled differently, match them by function: power, ground, SDA, SCL.

## Breadboard layout

```
                       ESP32 DevKit
                     ┌──────────────┐
   3V3 rail (+) ─────┤ 3V3          │
   GND rail (−) ─────┤ GND          │
                     │              │
 AD8232 ECG_OUT ─────┤ GPIO36 (VP)  │
 AD8232 LO−     ─────┤ GPIO33       │
 AD8232 LO+     ─────┤ GPIO32       │
                     │              │
 MAX30102 SDA   ─────┤ GPIO21       │
 MAX30102 SCL   ─────┤ GPIO22       │
                     └──────────────┘

 3V3 rail (+) ──► AD8232 VDD_3V3, AD8232 SDN, MAX30102 VIN
 GND rail (−) ──► AD8232 GND, MAX30102 GND
```

## Notes

- **Use the breadboard power rails.** Run the ESP32's 3V3 and GND to the rails once, and power both sensors from there. Both sensors must share the ESP32's ground.
- **The 38-pin DevKit is wide.** On a normal breadboard it covers almost every hole on both sides. Put it across two breadboards side by side, or let one row of pins hang off the edge if you only need pins from the other side. On the DevKit, GPIO32/33/36 and GPIO21/22 are on opposite sides.
- Keep ECG_OUT on an **ADC1** pin (GPIO32 to 39). ADC2 stops working when Wi-Fi or Bluetooth is on.
- Keep the ECG leads short and away from the USB cable. Run from a battery or a laptop on battery when the electrodes are on a person.
- If I²C is unreliable on a purple MAX30102 board, add 4.7 kΩ pull-ups from SDA and SCL to 3V3 (see `spo2-v1/esp32-devkit/PINOUT.md`).
- If you change a pin, change it in both this table and the sketch.
