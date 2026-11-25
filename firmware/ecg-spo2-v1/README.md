# ECG + SpO₂ firmware v1 (combined bench test)

First combined version: the AD8232 ECG board and a MAX30102 SpO₂ sensor on one breadboard with one ESP32. It's for testing the combined circuit. It shows both waves plus SpO₂ and heart rate in the Arduino Serial Plotter or Serial Monitor.

- **Works with:** `hardware/ecg-schematic-v1` (Rev A) and a MAX30102 module
- **Based on:** `ecg-v1` (same ECG pins) and `spo2-v1` (same SpO₂ pins and sensor settings)
- **Status:** written 2026-11-24. Compiles for ESP32 Dev Module (Arduino ESP32 core 3.3.10, SparkFun MAX3010x 1.1.2). Not yet tested on hardware.

## What's in here

| Path | What it is |
|---|---|
| `esp32-devkit/ecg_spo2_v1_esp32/ecg_spo2_v1_esp32.ino` | Sketch for the ESP32 Dev Module |
| `esp32-devkit/PINOUT.md` | Wiring for both sensors and the breadboard layout |
| `tools/live_plot.py` | Live plot of the last 5 s of ECG and PPG, with SpO₂ and HR, and a Record button that saves CSVs for the triage console |

## How to run it

1. Wire both sensors using `esp32-devkit/PINOUT.md`.
2. In the Arduino IDE, install the **ESP32 board package** (Boards Manager → "esp32" by Espressif) and the library **"SparkFun MAX3010x Pulse and Proximity Sensor Library"** (Library Manager).
3. Open the `.ino`, pick **ESP32 Dev Module** and the port, and upload.
4. Open **Tools → Serial Plotter** (or Serial Monitor) and set it to **115200 baud**.
5. Put on the electrodes (RA, LA, RL) and place a finger on the SpO₂ sensor. SpO₂ and heart rate show up about 5 seconds later.

When electrodes are on a person, run the ESP32 from a battery or power bank, or from a laptop running on battery.

## What you'll see

One line per ECG sample, 250 lines per second:

```
ecg:2051,ppg:812,spo2:98,hr:72
```

| Value | Meaning | When it's 0 or flat |
|---|---|---|
| `ecg` | Raw ECG reading, 0 to 4095 | `0` = an electrode is off |
| `ppg` | Pulse wave from the IR LED, with the slow level removed so beats show up | Flat at 800 = no finger |
| `spo2` | SpO₂ in %, updated every second from the last 4 seconds | `0` = no finger, or not a clean enough reading yet |
| `hr` | Heart rate in bpm from the pulse wave, same timing | `0` = same as above |

## Seeing the waves properly

The Arduino Serial Plotter only shows the last 50 points, which is 0.2 s at 250 lines per second: too short to see a heartbeat. Use the live plot instead (close the Serial Monitor/Plotter first, since only one program can use the port):

```
pip install pyserial matplotlib
python tools/live_plot.py
```

It finds the ESP32's port by itself (or pass one, e.g. `COM4`), waits if the board is unplugged, and shows the last 5 seconds of ECG and PPG with SpO₂ and HR in the title.

In the Serial Plotter, `ecg` and `ppg` draw as waves, and `spo2` and `hr` draw as near-flat lines near the bottom. Their current numbers are shown in the legend.

## Recording data for the triage console

The sketch has two output modes, set by `CSV_OUTPUT` at the top:

| `CSV_OUTPUT` | Output | Use it for |
|---|---|---|
| `false` (default) | `ecg:…,ppg:…,spo2:…,hr:…` | Watching the live plot with SpO₂ and HR |
| `true` | `ms,ECG,RED,IR` (raw, 250 rows per second) | Recording CSVs for the triage console |

To record:

1. Set `CSV_OUTPUT = true` and upload.
2. Run `tools/live_plot.py`, put on the electrodes and a finger, then press **Record** and later **Stop**. The file goes in `tools/recordings/`, named by date and time.
3. In `software/triage-console/index.html`, use **Upload your own CSV** on the ECG or PPG tab. The console reads `ms` as the time column (250 Hz), `ECG` as the ECG and `IR` as the pulse signal, and flips the raw IR itself. On the PPG tab it also checks every pulse against the ECG and measures pulse arrival time.

`RED` and `IR` update at 100 Hz, so each value repeats 2–3 times in the 250 Hz rows. `ECG` is 0 while an electrode is off, so start recording once the trace looks right.

Put recordings worth keeping in a `data/` folder here, named like `YYYY-MM-DD_ecg-spo2-v1_<who>_<what>.csv`.

## How it works

- **ECG:** sampled at a fixed **250 Hz** by its own task on the ESP32's second core, so printing and reading the SpO₂ sensor can't throw off its timing.
- **SpO₂ sensor:** same settings as `spo2-v1` (Red + IR, 100 samples per second). The sensor stores samples in its own buffer and the main loop reads them in batches.
- **SpO₂ and heart rate:** calculated with the SparkFun/Maxim algorithm that comes with the SparkFun library. It works on the last 4 seconds of data and recalculates every second. This is a known, simple algorithm that's fine for checking the circuit works. Our own processing will replace it later.
- When the finger comes off, the SpO₂ window resets, so the 4 seconds start again when the finger is back.

## Settings you might change

All are constants at the top of the sketch.

| Setting | Default | Change it when |
|---|---|---|
| `LED_BRIGHTNESS` | 60 | The pulse wave is tiny (raise it) or `ppg` clips/flat-lines with a finger on (lower it) |
| `FINGER_IR_THRESHOLD` | 50000 | `spo2`/`hr` stay 0 with a finger on, or the PPG jumps around with no finger |
| `PPG_PLOT_GAIN` | 1.0 | The PPG wave looks too small or too big next to the ECG |
| `PPG_PLOT_OFFSET` | 800 | The PPG wave overlaps the ECG on the plot |

## Troubleshooting

| Problem | Fix |
|---|---|
| `ERROR: MAX30102 not found` repeating | Check SDA/SCL aren't swapped, the sensor is on 3V3, and grounds are connected |
| Garbage characters in the Serial Monitor | Set the baud rate to 115200 |
| `ecg` is always 0 | An electrode is off or LO+/LO− is miswired. Check that SDN is tied to 3V3. |
| ECG is very noisy | Unplug the laptop charger, keep leads short and still, check the electrodes are stuck down |
| `spo2`/`hr` stay 0 | Keep the finger still for at least 5 s with light, steady pressure. Then tune `LED_BRIGHTNESS` and `FINGER_IR_THRESHOLD`. |
| Heart rate from `hr` doesn't match the ECG | Normal for this simple algorithm when there's movement. Stay still and compare again. |

## Versions

Don't edit a version once it's been used to record data. Copy it to `ecg-spo2-v2/` instead.

| Version | Date | Who | What changed |
|---|---|---|---|
| v1 | 2026-11-24 | Arta | First combined version: ECG at a fixed 250 Hz and MAX30102 on one ESP32. Serial Plotter output with SpO₂ and HR. |

Ideas for v2: on-device R-peak and pulse detection, so heart rate comes from the waveform instead of the SparkFun estimate.
