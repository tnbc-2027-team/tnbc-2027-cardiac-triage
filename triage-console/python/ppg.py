"""Reference PPG pulse detector (Python) - same steps as the JS version in the console
and matlab/ppg_detect.m.

1. Bandpass 0.5-8 Hz (2nd-order high-pass + low-pass biquads, forward and backward)
2. Systolic peaks: Elgendi et al. 2013 two-moving-average method
   clip negatives -> square -> MA over 111 ms (peak) and 667 ms (beat)
   -> blocks where MA_peak > MA_beat + 0.02*mean(y) and at least 111 ms wide
   -> the highest point in each block is a systolic peak (300 ms refractory)
3. Pulse foot (onset): tangent-intersection method - the tangent at the steepest
   upslope meets the horizontal line through the preceding minimum
4. Beat quality: correlation with the median pulse shape, plus an amplitude check
5. Pulse rate from the median peak-to-peak interval of good-quality pulses
6. With a simultaneous ECG: pair each R-peak with the next PPG foot
   -> pulse arrival time (R-peak to foot), used as the PTT signal for BP trends
"""
import numpy as np

from rpeak import biquad, filtfwdbwd


def bandpass(x, fs, lo=0.5, hi=8.0):
    x = np.asarray(x, float)
    x = x - np.median(x)
    for kind, f in (("hp", lo), ("lp", hi)):
        b, a = biquad(kind, f, fs)
        x = filtfwdbwd(x, b, a)
    return x


def moving_average(y, w):
    w = max(1, int(w))
    c = np.concatenate([[0], np.cumsum(y)])
    half = w // 2
    lo = np.clip(np.arange(len(y)) - half, 0, len(y))
    hi = np.clip(np.arange(len(y)) - half + w, 0, len(y))
    return (c[hi] - c[lo]) / w


def systolic_peaks(s, fs, w1=0.111, w2=0.667, beta=0.02, refractory=0.3):
    """Elgendi 2013: blocks of interest from two moving averages."""
    y = np.clip(s, 0, None) ** 2
    ma_peak = moving_average(y, round(w1 * fs))
    ma_beat = moving_average(y, round(w2 * fs))
    thr = ma_beat + beta * y.mean()
    on = ma_peak > thr
    peaks, i, n = [], 0, len(s)
    min_w = round(w1 * fs)
    while i < n:
        if on[i]:
            j = i
            while j < n and on[j]:
                j += 1
            if j - i >= min_w:
                peaks.append(i + int(np.argmax(s[i:j])))
            i = j
        else:
            i += 1
    # refractory: keep the higher of two peaks closer than 300 ms
    out, refr = [], round(refractory * fs)
    for p in peaks:
        if out and p - out[-1] < refr:
            if s[p] > s[out[-1]]:
                out[-1] = p
        else:
            out.append(p)
    return np.array(out, int)


def pulse_feet(s, peaks, fs, max_back=0.6):
    """Tangent intersection: time where the tangent at max upslope crosses the
    level of the preceding minimum. Returns fractional sample positions (nan if none)."""
    d = np.gradient(s)
    feet = np.full(len(peaks), np.nan)
    for k, p in enumerate(peaks):
        lo = max(0, p - round(max_back * fs), peaks[k - 1] if k else 0)
        if p - lo < 3:
            continue
        m = lo + int(np.argmin(s[lo:p + 1]))
        if p - m < 2:
            continue
        sl = m + int(np.argmax(d[m:p + 1]))
        if d[sl] <= 0:
            continue
        f = sl - (s[sl] - s[m]) / d[sl]
        feet[k] = min(max(f, m), sl)
    return feet


def beat_quality(s, peaks, fs, corr_min=0.8, amp_lo=0.3, amp_hi=3.0):
    """Correlation of each pulse with the median pulse, plus amplitude sanity check."""
    if len(peaks) < 3:
        return np.zeros(len(peaks)), np.zeros(len(peaks), bool), np.zeros(0), 0
    T = np.median(np.diff(peaks))
    a, b = int(round(0.35 * T)), int(round(0.65 * T))
    ok_idx = [k for k, p in enumerate(peaks) if p - a >= 0 and p + b <= len(s)]
    beats = np.array([s[peaks[k] - a: peaks[k] + b] for k in ok_idx])
    tpl = np.median(beats, axis=0)
    corr = np.zeros(len(peaks))
    for k, bt in zip(ok_idx, beats):
        corr[k] = np.corrcoef(bt, tpl)[0, 1]
    amp = np.array([s[p] - s[max(0, p - a):p + 1].min() for p in peaks])
    medamp = np.median(amp)
    good = (corr >= corr_min) & (amp >= amp_lo * medamp) & (amp <= amp_hi * medamp)
    return corr, good, tpl, a


def detect(x, fs, invert=None):
    s = bandpass(x, fs)
    if invert is None:  # upright PPG rises faster than it falls
        d = np.diff(s)
        invert = np.percentile(d, 99.5) < -np.percentile(d, 0.5)
    if invert:
        s = -s
    peaks = systolic_peaks(s, fs)
    feet = pulse_feet(s, peaks, fs)
    corr, good, tpl, off = beat_quality(s, peaks, fs)
    return dict(s=s, peaks=peaks, feet=feet, corr=corr, good=good, tpl=tpl, offset=off, inverted=bool(invert))


def pulse_rate(peaks, good, fs):
    pp = np.diff(peaks) / fs
    ok = good[1:] & good[:-1]
    use = pp[ok] if ok.sum() >= 3 else pp
    return dict(pr=60 / np.median(use), cv=float(np.std(use) / np.mean(use)),
                good_pct=100 * good.mean(), n=len(peaks))


def pair_with_ecg(rpeaks, feet, fs, lo=0.08, hi=0.8):
    """Pulse arrival time (PAT) for each R-peak.
    1. Typical delay d0 = most common R-to-foot delay between 80 and 800 ms (10 ms bins).
    2. Each R-peak is paired with the foot closest to R + d0, within +-min(120 ms, 30% of RR).
    Works even when the delay is longer than one heartbeat (fast heart rates)."""
    f = np.sort(feet[~np.isnan(feet)])
    rpeaks = np.asarray(rpeaks)
    pat = np.full(len(rpeaks), np.nan)
    if len(f) < 3 or len(rpeaks) < 3:
        return pat, np.nan
    delays = []
    for r in rpeaks:
        j0, j1 = np.searchsorted(f, r + lo * fs), np.searchsorted(f, r + hi * fs)
        delays.extend((f[j0:j1] - r) / fs)
    if not delays:
        return pat, np.nan
    hist, edges = np.histogram(delays, bins=np.arange(lo, hi + 0.01, 0.01))
    d0 = edges[np.argmax(hist)] + 0.005
    tol = min(0.12, 0.3 * np.median(np.diff(rpeaks)) / fs)
    for k, r in enumerate(rpeaks):
        j = np.searchsorted(f, r + d0 * fs)
        best = None
        for jj in (j - 1, j):
            if 0 <= jj < len(f) and abs((f[jj] - r) / fs - d0) <= tol:
                if best is None or abs(f[jj] - r - d0 * fs) < abs(f[best] - r - d0 * fs):
                    best = jj
        if best is not None:
            pat[k] = (f[best] - r) / fs
    return pat, d0


if __name__ == "__main__":
    import sys
    import rpeak
    import wfdb
    rec = wfdb.rdrecord(sys.argv[1])
    names = [n.upper() for n in rec.sig_name]
    ppg = rec.p_signal[:, names.index("PLETH")]
    ecg = rec.p_signal[:, 0]
    r = detect(ppg, rec.fs)
    print("pulses:", len(r["peaks"]), pulse_rate(r["peaks"], r["good"], rec.fs), "inverted", r["inverted"])
    rp, *_ = rpeak.detect(ecg, rec.fs)
    pat, d0 = pair_with_ecg(rp, r["feet"], rec.fs)
    print("R-peaks:", len(rp), "paired:", np.mean(~np.isnan(pat)), "PAT median ms:", 1000 * np.nanmedian(pat))
