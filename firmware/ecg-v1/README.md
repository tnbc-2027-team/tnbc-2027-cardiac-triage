# ECG firmware v1

First working ECG code. Reads the AD8232 front end and streams the raw signal over USB serial so you can see it in the Arduino Serial Plotter.

- **Works with board:** `hardware/ecg-schematic-v1` (Rev A), header J2 "TO_MCU"
- **Status:** working on Arduino Uno (bench test 2026-11-06). ESP32 version is a port of the same code and hasn't been tested on hardware yet.

## What's in here

| Path | What it is |
|---|---|
| `arduino-uno/ecg_v1_uno/ecg_v1_uno.ino` | Rushil's original sketch, unchanged apart from a header comment |
| `arduino-uno/PINOUT.md` | Which J2 pin goes to which Uno pin |
| `esp32-devkit/ecg_v1_esp32/ecg_v1_esp32.ino` | Same code for the ESP32 Dev Module |
| `esp32-devkit/PINOUT.md` | Which J2 pin goes to which ESP32 pin |
| `data/` | ECG recordings captured with the Uno sketch |

Each sketch is in a folder with the same name because the Arduino IDE needs that to open it.

## How to run it

1. Wire the ECG board to your microcontroller using the `PINOUT.md` next to the sketch.
2. Open the `.ino` file in the Arduino IDE, pick the board (Arduino Uno or ESP32 Dev Module) and the port, and upload.
3. Open **Tools → Serial Plotter** at **115200 baud**. You'll see the ECG trace, or `!` when an electrode is off.

## Recorded data (`data/`)

Captured 2026-11-06 with the Uno sketch. Each trial lasted about 10 seconds.

| File | What it is |
|---|---|
| `2026-11-06_ecg-v1_uno_trials.xlsx` | Original workbook, all three trials side by side |
| `2026-11-06_ecg-v1_uno_normal.csv` | Normal resting ECG (30,065 samples) |
| `2026-11-06_ecg-v1_uno_60hz-noise.csv` | Recorded with 60 Hz mains interference (28,377 samples) |
| `2026-11-06_ecg-v1_uno_motion.csv` | Recorded with motion artifact (25,727 samples) |

The CSVs are the same data as the workbook, one file per trial. Columns are `sample` and `ECG`, where `ECG` is the raw Uno reading (0 to 1023). They load straight into the triage console in `software/triage-console/`.

**Sample rate:** v1 has no fixed sample rate. It sends readings as fast as the 115200 baud serial link allows, and there are no timestamps. Roughly 10 s per trial works out to about 2,500 to 3,000 samples per second, but treat that as an estimate.

## Versions

We keep one folder per firmware version, matching the board it runs on (`ecg-v1` goes with `ecg-schematic-v1`). For a new version, copy this folder to `ecg-v2/`, make your changes there, and add a line below. Don't edit a version once it's been used to record data, so the data always matches the code that made it.

| Version | Date | Who | What changed |
|---|---|---|---|
| v1 | 2026-11-06 | Rushil | First working version: raw ECG over serial and leads-off detection. Uno and ESP32 sketches with pinouts. |

Ideas for v2: a fixed sample rate (for example 250 or 500 Hz using `micros()`), a timestamp on each line, and driving SDN from a pin to save battery.
