# SpO₂ firmware v1

Reads a MAX30102 SpO₂ sensor and streams the raw red and IR signals over USB serial as CSV. It doesn't calculate SpO₂ or heart rate yet: that's the processing step, which will use exactly this data format.

- **Sensor:** MAX30102 breakout module, in the team's finger clip (`mech/`)
- **Status:** written 2026-11-08, not yet tested on hardware

## What's in here

| Path | What it is |
|---|---|
| `esp32-devkit/spo2_v1_esp32/spo2_v1_esp32.ino` | Sketch for the ESP32 Dev Module |
| `esp32-devkit/PINOUT.md` | Which sensor pin goes to which ESP32 pin |

Each sketch is in a folder with the same name because the Arduino IDE needs that to open it.

## How to run it

1. Wire the sensor using `esp32-devkit/PINOUT.md`.
2. In the Arduino IDE, install the **ESP32 board package** (Boards Manager → "esp32" by Espressif) and the library **"SparkFun MAX3010x Pulse and Proximity Sensor Library"** (Library Manager).
3. Open the `.ino` file, pick **ESP32 Dev Module** and the port, and upload.
4. Open the Serial Monitor at **115200 baud**. Use the Serial Plotter to see the pulse.

When the sensor is on a person, power the ESP32 from a battery or power bank, or from a laptop running on battery.

## Sensor settings

All settings are constants at the top of the sketch.

| Setting | Value | Why |
|---|---|---|
| LED mode | Red + IR | Both are needed for SpO₂ |
| Internal sample rate | 400 Hz | |
| Sample averaging | 4 | Less noise; gives **100 Hz output** |
| Pulse width | 411 µs | 18-bit resolution |
| ADC range | 16384 | Headroom so the signal doesn't max out |
| LED brightness | 60 / 255 | Lower it if values hit the ceiling, raise it if the pulse is barely visible |

## Output format

CSV at 100 samples per second. Lines starting with `#` are status messages, so skip them when loading the data.

```
# MAX30102 ready. Output rate (Hz): 100.00
sample_idx,t_ms,red,ir,finger
0,0,98123,104550,1
1,10,98140,104571,1
```

| Column | Meaning |
|---|---|
| `sample_idx` | Sample counter |
| `t_ms` | Time in ms, from the sensor's own clock (`sample_idx × 10 ms`) |
| `red` | Raw red reading |
| `ir` | Raw IR reading |
| `finger` | `1` if a finger seems to be on the sensor, `0` if not |

**Why `t_ms` is calculated, not measured:** the sensor stores samples in a buffer and the ESP32 reads them in batches, so the time the ESP32 reads a sample isn't when it was taken. Counting samples gives evenly spaced times. The sensor's clock isn't perfect, so long recordings drift slightly against other devices.

## Saving a recording

For quick tests, copy from the Serial Monitor. For proper recordings, use a short Python script (`pip install pyserial`):

```python
import serial

PORT = "COM5"          # Windows example; Mac/Linux: "/dev/ttyUSB0"
with serial.Serial(PORT, 115200) as ser, open("spo2_recording.csv", "w") as f:
    while True:
        line = ser.readline().decode(errors="ignore").strip()
        if line and not line.startswith("#"):
            f.write(line + "\n")
```

Put recordings in a `data/` folder here, named like the ECG ones: `YYYY-MM-DD_spo2-v1_esp32_<what>.csv`.

## Troubleshooting

| Problem | Fix |
|---|---|
| `# ERROR: MAX30102 not found` | Check SDA/SCL aren't swapped, the sensor is on 3V3, and grounds are connected |
| Values stuck near the maximum (~262143) | Signal is maxing out: lower `LED_BRIGHTNESS` |
| No pulse visible in the IR trace | Raise `LED_BRIGHTNESS`, check finger contact and clip pressure, block outside light |
| `finger` always 0 or always 1 | Change `FINGER_IR_THRESHOLD`, using the IR values you see with and without a finger |
| I²C keeps dropping out | See the pull-up note in `esp32-devkit/PINOUT.md` |

## Versions

Don't edit a version once it's been used to record data. Copy it to `spo2-v2/` instead.

| Version | Date | Who | What changed |
|---|---|---|---|
| v1 | 2026-11-08 | Arta | First version: raw red/IR at 100 Hz over serial, calculated timestamps, finger detection |

Next: the combined ECG + SpO₂ firmware on one ESP32, with one shared time base.
