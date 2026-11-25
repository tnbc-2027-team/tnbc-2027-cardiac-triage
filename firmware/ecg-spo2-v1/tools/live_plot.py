"""
Live plot and recorder for ecg-spo2-v1: last 5 seconds of ECG and PPG.

Works with both sketch output modes:
  - live view  (CSV_OUTPUT = false): ecg:...,ppg:...,spo2:...,hr:...  -> SpO2 and HR in the title
  - recording  (CSV_OUTPUT = true):  ms,ECG,RED,IR                    -> Record button saves a CSV
    for the triage console's "Upload your own CSV" (ECG and PPG tabs)

The Arduino Serial Plotter only shows the last 50 points (0.2 s at 250 lines/s),
which is too short to see a heartbeat.

Close the Arduino Serial Monitor / Plotter first: only one program can use the port.

  pip install pyserial matplotlib
  python live_plot.py          (finds the ESP32's port by itself)
  python live_plot.py COM4     (or name the port)

Recordings go in a "recordings" folder next to this script.
"""
import collections
import os
import sys
import threading
import time
from datetime import datetime

import matplotlib.pyplot as plt
import serial
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button
from serial.tools import list_ports

PORT_ARG = sys.argv[1] if len(sys.argv) > 1 else None
BAUD = 115200
RATE_HZ = 250      # lines per second from the sketch
WINDOW_S = 5       # seconds shown
N = RATE_HZ * WINDOW_S
RECORD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "recordings")
CSV_HEADER = "ms,ECG,RED,IR"

ecg = collections.deque([0] * N, maxlen=N)
ppg = collections.deque([0] * N, maxlen=N)   # live mode: sketch's PPG; CSV mode: raw IR
latest = {"spo2": 0, "hr": 0}
status = {"text": "Looking for the ESP32...", "mode": None, "port": None, "last_raw": ""}
rec = {"file": None, "path": None, "rows": 0}
USB_SERIAL_HINTS = ("cp210", "silicon labs", "ch340", "ch910", "wch", "usb-serial", "usb serial", "uart", "ftdi")
lock = threading.Lock()


def parse_live(line):
    """'ecg:2051,ppg:812,spo2:98,hr:72' -> (2051, 812, 98, 72), or None."""
    try:
        fields = dict(part.split(":") for part in line.split(","))
        return int(fields["ecg"]), int(fields["ppg"]), int(fields["spo2"]), int(fields["hr"])
    except (ValueError, KeyError):
        return None


def parse_csv(line):
    """'1234,2051,98123,104550' -> (1234, 2051, 98123, 104550), or None."""
    parts = line.split(",")
    if len(parts) != 4:
        return None
    try:
        return tuple(int(x) for x in parts)
    except ValueError:
        return None


def find_port():
    if PORT_ARG:
        return PORT_ARG
    for p in list_ports.comports():
        text = f"{p.description} {p.manufacturer or ''} {p.hwid}".lower()
        if any(h in text for h in USB_SERIAL_HINTS):
            return p.device
    return None


def handle_line(raw):
    live = parse_live(raw)
    if live:
        e, p, s, h = live
        with lock:
            status["mode"] = "live"
            ecg.append(e)
            ppg.append(p)
            latest["spo2"], latest["hr"] = s, h
        return
    row = parse_csv(raw)
    if row:
        ms, e, red, ir = row
        with lock:
            status["mode"] = "csv"
            ecg.append(e)
            ppg.append(ir)
            if rec["file"]:
                rec["file"].write(f"{ms},{e},{red},{ir}\n")
                rec["rows"] += 1
        return
    if raw and raw != CSV_HEADER:
        status["last_raw"] = raw


def reader():
    while True:
        port = find_port()
        if port is None:
            status["text"] = "ESP32 not found: plug it in with a USB data cable"
            time.sleep(1)
            continue
        try:
            with serial.Serial(port, BAUD, timeout=1) as ser:
                status["text"] = f"Connected on {port}, waiting for data..."
                status["port"] = port
                while True:
                    handle_line(ser.readline().decode(errors="ignore").strip())
        except serial.SerialException:
            status["mode"] = None
            status["text"] = f"Can't open {port}: unplugged, or the Arduino Serial Monitor/Plotter is using it"
            time.sleep(1)


def start_recording():
    os.makedirs(RECORD_DIR, exist_ok=True)
    name = datetime.now().strftime("%Y-%m-%d_%H%M%S") + "_ecg-spo2-v1.csv"
    path = os.path.join(RECORD_DIR, name)
    with lock:
        rec["file"] = open(path, "w", newline="")
        rec["file"].write(CSV_HEADER + "\n")
        rec["path"], rec["rows"] = path, 0


def stop_recording():
    with lock:
        if rec["file"]:
            rec["file"].close()
        rec["file"] = None


def autoscale(ax, data, min_span=20):
    lo, hi = min(data), max(data)
    span = max(hi - lo, min_span)
    mid = (hi + lo) / 2
    ax.set_ylim(mid - span * 0.6, mid + span * 0.6)


def main():
    threading.Thread(target=reader, daemon=True).start()

    t = [i / RATE_HZ - WINDOW_S for i in range(N)]
    fig, (ax_e, ax_p) = plt.subplots(2, 1, sharex=True, figsize=(11, 6.5))
    fig.subplots_adjust(bottom=0.16, top=0.9)
    line_e, = ax_e.plot(t, list(ecg), lw=1)
    line_p, = ax_p.plot(t, list(ppg), lw=1, color="tab:red")
    ax_e.set_ylabel("ECG (raw, 0 = electrode off)")
    ax_p.set_ylabel("PPG")
    ax_p.set_xlabel("seconds")
    title = fig.suptitle("Waiting for data...")
    note = fig.text(0.24, 0.035, "", fontsize=9)

    btn_ax = fig.add_axes([0.08, 0.02, 0.13, 0.055])
    btn = Button(btn_ax, "Record")

    def on_click(_):
        if rec["file"]:
            stop_recording()
            btn.label.set_text("Record")
            note.set_text(f"Saved {rec['rows'] / RATE_HZ:.0f} s to {rec['path']}")
        elif status["mode"] == "csv":
            start_recording()
            btn.label.set_text("Stop")
        else:
            note.set_text("To record, set CSV_OUTPUT = true at the top of the sketch and upload it again.")

    btn.on_clicked(on_click)

    def update(_):
        with lock:
            e, p = list(ecg), list(ppg)
            s, h = latest["spo2"], latest["hr"]
            mode = status["mode"]
        if mode == "csv":
            mean = sum(p) / len(p)
            p = [mean - v for v in p]        # flip raw IR so beats point up, centre on 0
            ax_p.set_ylabel("PPG (raw IR, flipped)")
        else:
            ax_p.set_ylabel("PPG (IR, DC removed)")
        line_e.set_ydata(e)
        line_p.set_ydata(p)
        autoscale(ax_e, e)
        autoscale(ax_p, p)

        if mode == "live":
            title.set_text(f"SpO2: {s or '--'} %      HR: {h or '--'} bpm")
        elif mode == "csv":
            title.set_text("Recording mode (ms,ECG,RED,IR): press Record to save a CSV for the triage console")
            if rec["file"]:
                note.set_text(f"Recording... {rec['rows'] / RATE_HZ:.0f} s")
        elif status["last_raw"] and status["port"]:
            title.set_text(f"{status['port']}: board is sending \"{status['last_raw'][:60]}\". "
                           "Re-upload ecg_spo2_v1_esp32.")
        else:
            title.set_text(status["text"])
        return line_e, line_p, title, note

    _anim = FuncAnimation(fig, update, interval=50, cache_frame_data=False)
    plt.show()
    stop_recording()


if __name__ == "__main__":
    main()
