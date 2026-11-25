"""
Live plot for ecg-spo2-v1: last 5 seconds of ECG and PPG, with SpO2 and HR in the title.

The Arduino Serial Plotter only shows the last 50 points (0.2 s at 250 lines/s),
which is too short to see a heartbeat. This shows the full window at full rate.

Close the Arduino Serial Monitor / Plotter first: only one program can use the port.

  pip install pyserial matplotlib
  python live_plot.py COM4
"""
import collections
import sys
import threading

import matplotlib.pyplot as plt
import serial
from matplotlib.animation import FuncAnimation

PORT = sys.argv[1] if len(sys.argv) > 1 else "COM4"
BAUD = 115200
RATE_HZ = 250      # ECG lines per second from the sketch
WINDOW_S = 5       # seconds shown
N = RATE_HZ * WINDOW_S

ecg = collections.deque([0] * N, maxlen=N)
ppg = collections.deque([0] * N, maxlen=N)
latest = {"spo2": 0, "hr": 0}
lock = threading.Lock()


def parse(line):
    """'ecg:2051,ppg:812,spo2:98,hr:72' -> (2051, 812, 98, 72), or None if the line is damaged."""
    try:
        fields = dict(part.split(":") for part in line.split(","))
        return int(fields["ecg"]), int(fields["ppg"]), int(fields["spo2"]), int(fields["hr"])
    except (ValueError, KeyError):
        return None


def reader():
    with serial.Serial(PORT, BAUD, timeout=1) as ser:
        while True:
            values = parse(ser.readline().decode(errors="ignore").strip())
            if values is None:
                continue
            e, p, s, h = values
            with lock:
                ecg.append(e)
                ppg.append(p)
                latest["spo2"], latest["hr"] = s, h


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
        title.set_text(f"SpO2: {s or '--'} %      HR: {h or '--'} bpm")
        return line_e, line_p, title

    _anim = FuncAnimation(fig, update, interval=50, cache_frame_data=False)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
