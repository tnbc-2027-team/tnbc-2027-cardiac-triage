# SpO₂ v1 pinout: ESP32 Dev Module

Sensor: MAX30102 breakout module (I²C).
Microcontroller: ESP32 Dev Module (ESP32-WROOM-32 DevKitC, 38-pin).
Sketch: `spo2_v1_esp32/spo2_v1_esp32.ino`

| MAX30102 pin | ESP32 pin | Notes |
|---|---|---|
| VIN | **3V3** | Use 3.3 V so the I²C lines stay at ESP32-safe levels |
| GND | GND | Common ground with the rest of the system |
| SDA | **GPIO21** | Default ESP32 I²C data |
| SCL | **GPIO22** | Default ESP32 I²C clock |
| INT | not connected | Unused in v1. GPIO19 is reserved for it later. |

```
 MAX30102            ESP32 DevKit
 ┌────────┐          ┌──────────┐
 │ VIN ───┼──────────┼─ 3V3     │
 │ GND ───┼──────────┼─ GND     │
 │ SDA ───┼──────────┼─ GPIO21  │
 │ SCL ───┼──────────┼─ GPIO22  │
 │ INT    │ (n/c)    │          │
 └────────┘          └──────────┘
```

## Notes

- No pin clashes with `ecg-v1` on the ESP32 (ECG uses GPIO32, 33 and 36), so both sensors can go on the same board for the combined version.
- Some purple "MAX30102" boards pull SDA/SCL up to 1.8 V. If I²C is unreliable, add 4.7 kΩ pull-ups from SDA and SCL to 3V3.
- If you change a pin, change it in both this table and the sketch.
