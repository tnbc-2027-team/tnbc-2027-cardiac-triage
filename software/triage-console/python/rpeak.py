"""Reference R-peak detector (Python) - same steps as the JS version in the console.

1. Bandpass 5-15 Hz (2nd-order high-pass + low-pass biquads, run forward and backward)
2. First pass: Pan-Tompkins style (derivative -> square -> 150 ms moving average -> adaptive threshold)
3. Template: median beat around first-pass R-peaks
4. Normalized cross-correlation (NCC) with the template; peaks above threshold with 200 ms refractory
5. Refine each detection to the largest |bandpassed| sample within +-50 ms
"""
import numpy as np
from scipy.signal import lfilter


def biquad(kind, f0, fs, q=0.7071):
    w = 2 * np.pi * f0 / fs
    alpha = np.sin(w) / (2 * q)
    c = np.cos(w)
    if kind == "hp":
        b = [(1 + c) / 2, -(1 + c), (1 + c) / 2]
    else:
        b = [(1 - c) / 2, 1 - c, (1 - c) / 2]
    a = [1 + alpha, -2 * c, 1 - alpha]
    return np.array(b) / a[0], np.array(a) / a[0]


def filtfwdbwd(x, b, a):
    y = lfilter(b, a, x)
    return lfilter(b, a, y[::-1])[::-1]


def bandpass(x, fs):
    x = x - np.median(x)
    for kind, f in (("hp", 5.0), ("lp", 15.0)):
        b, a = biquad(kind, f, fs)
        x = filtfwdbwd(x, b, a)
    return x


def first_pass(bp, fs):
    d = np.diff(bp, prepend=bp[0])
    sq = d * d
    w = int(0.15 * fs)
    mwi = np.convolve(sq, np.ones(w) / w, mode="same")
    refr = int(0.2 * fs)
    init = mwi[: 2 * int(fs)]
    spk, npk = init.max() * 0.5, init.mean() * 0.5
    peaks, last = [], -refr
    for i in range(1, len(mwi) - 1):
        if mwi[i] > mwi[i - 1] and mwi[i] >= mwi[i + 1]:
            thr = npk + 0.25 * (spk - npk)
            if mwi[i] > thr and i - last > refr:
                peaks.append(i); last = i
                spk = 0.125 * mwi[i] + 0.875 * spk
            else:
                npk = 0.125 * mwi[i] + 0.875 * npk
    return refine(bp, np.array(peaks), fs)


def refine(bp, idx, fs, win=0.05):
    h = int(win * fs)
    out = []
    for i in idx:
        lo, hi = max(0, i - h), min(len(bp), i + h + 1)
        out.append(lo + int(np.argmax(np.abs(bp[lo:hi]))))
    return np.unique(out)


def build_template(bp, peaks, fs, pre=0.10, post=0.15):
    a, b = int(pre * fs), int(post * fs)
    beats = [bp[p - a: p + b] for p in peaks if p - a >= 0 and p + b <= len(bp)]
    return np.median(np.array(beats), axis=0), a


def ncc(bp, tpl):
    n = len(tpl)
    t = (tpl - tpl.mean()) / (np.linalg.norm(tpl - tpl.mean()) + 1e-12)
    num = np.correlate(bp, t, mode="valid")
    c1 = np.concatenate([[0], np.cumsum(bp)])
    c2 = np.concatenate([[0], np.cumsum(bp * bp)])
    s1 = c1[n:] - c1[:-n]
    s2 = c2[n:] - c2[:-n]
    var = np.maximum(s2 - s1 * s1 / n, 1e-12)
    return num / np.sqrt(var)


def detect(x, fs, thr=0.5, amp_gate=0.4):
    """thr: minimum NCC with the template. amp_gate: candidate must reach this
    fraction of the median R amplitude (stops T-waves that match in shape only)."""
    import bisect
    bp = bandpass(np.asarray(x, float), fs)
    fp = first_pass(bp, fs)
    tpl, offset = build_template(bp, fp, fs)
    r = ncc(bp, tpl)
    amp = np.median(np.abs(bp[fp]))
    refr, h = int(0.2 * fs), int(0.05 * fs)
    cand = [i for i in range(1, len(r) - 1) if r[i] > thr and r[i] >= r[i - 1] and r[i] >= r[i + 1]]
    picked = []
    for i in sorted(cand, key=lambda k: -r[k]):  # strongest match first
        p = i + offset
        if np.abs(bp[max(0, p - h): p + h + 1]).max() < amp_gate * amp:
            continue
        j = bisect.bisect(picked, i)
        if (j > 0 and i - picked[j - 1] <= refr) or (j < len(picked) and picked[j] - i <= refr):
            continue
        picked.insert(j, i)
    peaks = refine(bp, np.array(picked) + offset, fs)
    return peaks, bp, tpl, fp


def rhythm(peaks, fs):
    rr = np.diff(peaks) / fs
    med = np.median(rr)
    local = np.array([np.median(rr[max(0, i - 4): i + 5]) for i in range(len(rr))])
    premature = int(np.sum(rr < 0.8 * local))
    return dict(hr=60 / med, cv=float(np.std(rr) / np.mean(rr)), premature=premature,
                premature_pct=100 * premature / len(rr))


def score(det, ref, fs, tol=0.075):
    t = int(tol * fs)
    ref = np.asarray(ref); used = np.zeros(len(ref), bool); tp = 0
    for d in det:
        j = np.searchsorted(ref, d)
        for k in (j - 1, j):
            if 0 <= k < len(ref) and not used[k] and abs(ref[k] - d) <= t:
                used[k] = True; tp += 1; break
    fp, fn = len(det) - tp, len(ref) - tp
    return dict(tp=tp, fp=fp, fn=fn, se=tp / (tp + fn), ppv=tp / (tp + fp))


if __name__ == "__main__":
    import sys, wfdb
    rec = sys.argv[1]
    r = wfdb.rdrecord(rec, channels=[0]); a = wfdb.rdann(rec, "atr")
    beats = set("NLRBAaJSVrFejnE/fQ")
    ref = np.array([s for s, sym in zip(a.sample, a.symbol) if sym in beats])
    peaks, bp, tpl, fp = detect(r.p_signal[:, 0], r.fs)
    print("first pass:", score(fp, ref, r.fs))
    print("template  :", score(peaks, ref, r.fs))
