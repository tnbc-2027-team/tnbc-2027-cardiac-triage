"""
Live plot for ecg-spo2-v1: last 5 seconds of ECG and PPG, with SpO2 and HR in the title.

The Arduino Serial Plotter only shows the last 50 points (0.2 s at 250 lines/s),
which is too short to see a heartbeat. This shows the full window at full rate.

Close the Arduino Serial Monitor / Plotter first: only one program can use the port.

  pip install pyserial matplotlib
  python live_plot.py          (finds the ESP32's port by itself)
  python live_plot.py COM4     (or name the port)
"""
import collections
import sys
import threading
import time

import matplotlib.pyplot as plt
import serial
from serial.tools import list_ports
from matplotlib.animation import FuncAnimation

PORT_ARG = sys.argv[1] if len(sys.argv) > 1 else None
BAUD = 115200
RATE_HZ = 250      # ECG lines per second from the sketch
WINDOW_S = 5       # seconds shown
N = RATE_HZ * WINDOW_S

ecg = collections.deque([0] * N, maxlen=N)
ppg = collections.deque([0] * N, maxlen=N)
latest = {"spo2": 0, "hr": 0}
status = {"text": "Looking for the ESP32...", "got_data": False, "port": None, "last_raw": ""}
USB_SERIAL_HINTS = ("cp210", "silicon labs", "ch340", "ch910", "wch", "usb-serial", "usb serial", "uart", "ftdi")
lock = threading.Lock()


def parse(line):
    """'ecg:2051,ppg:812,spo2:98,hr:72' -> (2051, 812, 98, 72), or None if the line is damaged."""
    try:
        fields = dict(part.split(":") for part in line.split(","))
        return int(fields["ecg"]), int(fields["ppg"]), int(fields["spo2"]), int(fields["hr"])
    except (ValueError, KeyError):
        return None


def find_port():
    if PORT_ARG:
        return PORT_ARG
    for p in list_ports.comports():
        text = f"{p.description} {p.manufacturer or ''} {p.hwid}".lower()
        if any(h in text for h in USB_SERIAL_HINTS):
            return p.device
    return None


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
                    raw = ser.readline().decode(errors="ignore").strip()
                    values = parse(raw)
                    if values is None:
                        if raw:
                            status["last_raw"] = raw
                        continue
                    e, p, s, h = values
                    with lock:
                        ecg.append(e)
                        ppg.append(p)
                        latest["spo2"], latest["hr"] = s, h
                        status["got_data"] = True
        except serial.SerialException:
            status["got_data"] = False
            status["text"] = f"Can't open {port}: unplugged, or the Arduino Serial Monitor/Plotter is using it"
            time.sleep(1)


def autoscale(ax, data, min_span=20):
    lo, hi = min(data), max(data)
    span = max(hi - lo, min_span)
    mid = (hi + lo) / 2
    ax.set_ylim(mid - span * 0.6, mid + span * 0.6)


def main():
    threading.Thread(target=reader, daemon=True).start()

    t = [i / RATE_HZ - WINDOW_S for i in range(N)]
    fig, (ax_e, ax_p) = plt.subplots(2, 1, sharex=True, figsize=(11, 6))
    line_e, = ax_e.plot(t, list(ecg), lw=1)
    line_p, = ax_p.plot(t, list(ppg), lw=1, color="tab:red")
    ax_e.set_ylabel("ECG (raw, 0 = electrode off)")
    ax_p.set_ylabel("PPG (IR, DC removed)")
    ax_p.set_xlabel("seconds")
    title = fig.suptitle("Waiting for data...")

    def update(_):
        with lock:
            e, p = list(ecg), list(ppg)
            s, h = latest["spo2"], latest["hr"]
        line_e.set_ydata(e)
        line_p.set_ydata(p)
        autoscale(ax_e, e)
        autoscale(ax_p, p)
        if status["got_data"]:
            title.set_text(f"SpO2: {s or '--'} %      HR: {h or '--'} bpm")
        elif status["last_raw"] and status["port"]:
            title.set_text(f"{status['port']}: board is sending \"{status['last_raw'][:70]}\" "
                           "(expected ecg:...,ppg:...). Re-upload ecg_spo2_v1_esp32.")
        else:
            title.set_text(status["text"])
        return line_e, line_p, title

    _anim = FuncAnimation(fig, update, interval=50, cache_frame_data=False)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
