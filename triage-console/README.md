# Cardiac Triage Console: ECG and PPG signal processing

Prototype software for the TNBC 2026–27 Portable Cardiac Triage System. The console ranks patients by triage priority from SpO₂, blood pressure, heart rate and ECG rhythm.

- The **ECG analysis** tab detects R-peaks in a real ECG recording. It turns them into heart rate and a rhythm category for the triage score.
- The **PPG analysis** tab detects every pulse in a real PPG recording. It turns them into pulse rate and a signal-quality score, checks each pulse against the simultaneous ECG, and measures pulse arrival time (R-peak to pulse foot) for PTT.

Prototype only, not for clinical use.

## Run the demo

Open `index.html` in a browser. It is one self-contained file (detector code and sample recordings included), so it works offline with no build step or server.

### ECG analysis tab

1. Pick a recording. MIT-BIH record 100 is normal sinus rhythm with cardiologist annotations, so accuracy is scored live. Record 208 has frequent PVCs, to show an irregular rhythm.
2. The detector runs automatically. You see heart rate, beat count, RR variation, atypical beats, the suggested ECG category and, for record 100, sensitivity and PPV.
3. Scroll through the strip with the slider, or click the RR plot to jump to a spot.
4. Under **Send to triage**, enter a patient ID and click **Fill reading** to carry heart rate and the ECG category into the Queue tab.

### PPG analysis tab

1. Pick a recording:
   - **Resting recording:** 5 min of clean PPG with ECG at 100 Hz.
   - **ICU patient:** 5.5 min at 250 Hz. The bedside monitor raised a false asystole alarm at 5:00 because the ECG leads failed, but the PPG kept showing pulses. It also has real motion artifacts.
2. The strip shows the ECG on top and the PPG below. It marks systolic peaks (dots), pulse feet (triangles), noisy pulses (hollow red) and the pulse arrival time from each R-peak to its pulse.
3. The charts show pulse rate over time (with ECG heart rate behind it), the average pulse shape, and pulse arrival time for every beat. Click a chart to move the strip there.
4. **Send to triage** fills heart rate with the pulse rate. It ticks poor signal on HR if fewer than 80% of pulses are clean.

### Uploading your own CSV (both tabs)

Use a header row. The console picks the columns by name:

| Tab | Signal column | Also used |
|---|---|---|
| ECG | `ECG`, `II` or `MLII` (otherwise the last column) | |
| PPG | `PLETH`, `PPG` or `IR` (then `RED`, otherwise the first column) | an `ECG` or `II` column, to check each pulse |

A column named `time` sets the sampling rate. It is read as seconds, or as milliseconds if it's named `ms`. Without one, type the rate in. The PhysioNet BIDMC CSVs (`bidmc_XX_Signals.csv`) and a raw MAX30102 export (`ms, red, ir`) both work as they are. Raw sensor IR is upside down, and the PPG tab flips it automatically.

## Results

### ECG R-peaks, MIT-BIH record 100

| Recording | Beats | Sensitivity | PPV | Browser time |
|---|---|---|---|---|
| Record 100, first 5 min | 371 | 100% | 100% | ~0.1 s |
| Record 100, full 30 min (Python) | 2,273 | 100% | 99.96% | |

A detection counts as correct within ±75 ms of an annotated beat.

### PPG pulses, checked against the simultaneous ECG

| Recording | Pulses | Clean | Pulses matched to an ECG beat | Pulse rate vs ECG HR | Pulse arrival time (median, IQR) |
|---|---|---|---|---|---|
| Resting, 5 min, 100 Hz | 432 | 99.8% | 99.8% | 87.0 vs 87.0 bpm | 279 ms (272–287) |
| ICU a103l, 5.5 min, 250 Hz | 654 | 89.4% | 96.0% | 127.1 vs 127.1 bpm | 490 ms (482–499)* |

\* Longer than the usual 150–400 ms at the finger. Bedside monitors can delay the PPG waveform, so this delay is only useful for trends on that recording.

On the ICU recording, all 316 pulses in the first 2.5 minutes match an ECG beat one to one. The unmatched pulses are in the motion-artifact and lead-failure stretches later on. The JavaScript, Python and MATLAB versions give the same results on both recordings. The MATLAB code was run in GNU Octave 8.4.

## How the ECG detector works

Implemented identically in the `<script>` inside `index.html` marked "R-peak detector", `python/rpeak.py` and `matlab/rpeak_detect.m`:

1. **Bandpass 5–15 Hz.** 2nd-order high-pass and low-pass biquads, run forward and backward so the peaks don't shift in time.
2. **First pass (Pan–Tompkins style).** Derivative, square, 150 ms moving average, adaptive threshold. This gives rough beat locations.
3. **QRS template.** The median of the first-pass beats, from 100 ms before to 150 ms after the R-peak.
4. **Template matching.** Normalized cross-correlation with the template. A beat must:
   - match above the threshold (default 0.5)
   - reach 40% of the typical R height, which rejects T-waves that match in shape only
   - be at least 200 ms from the previous beat
5. **Refine.** Each beat moves to the sharpest point within ±50 ms.

**Rhythm summary.** Heart rate comes from the median RR interval, and RR variation is the standard deviation of RR divided by its mean. A beat whose template match is below 0.8 counts as atypical (possible ectopic beat). The ECG category rules are listed in the Scoring guide tab. They are placeholders for clinical review.

## How the PPG detector works

Implemented identically in the `<script>` inside `index.html` marked "PPG pulse detector", `python/ppg.py` and `matlab/ppg_detect.m`:

1. **Bandpass 0.5–8 Hz.** Same biquad filters as the ECG, run forward and backward. This removes slow drift from breathing and movement and keeps the pulse wave.
2. **Orientation.** An upright PPG rises faster than it falls. If the signal's steepest falls are bigger than its steepest rises, it is upside down (normal for raw sensor IR) and gets flipped. This can be overridden in the console.
3. **Systolic peaks (Elgendi et al., 2013).** Clip negatives and square. Then compare a 111 ms moving average (one systolic peak wide) with a 667 ms one (one beat wide). Each block where the short average is above the long one plus 0.02 × the signal mean, and that lasts at least 111 ms, holds one peak: its highest point. Peaks closer than 300 ms are merged.
4. **Pulse foot (tangent intersection).** The tangent at the steepest point of the upstroke meets the horizontal line through the minimum before it. This is the standard reference point for PTT because it is less affected by wave reflections than the peak.
5. **Quality.** Each pulse is correlated with the median pulse shape. A pulse is clean if the correlation is at least 0.8 (the same cut-off as the ECG atypical-beat rule) and its amplitude is 0.3–3× the typical amplitude. Pulse rate comes from the median interval between clean pulses.
6. **Check against ECG and pulse arrival time.** The most common R-peak-to-foot delay between 80 and 800 ms is found first. Each R-peak is then paired with the foot closest to that delay, within ±120 ms (or 30% of RR if smaller). This works even when the delay is longer than one heartbeat. Strictly, R-peak to foot is the pulse arrival time: PTT plus the heart's pre-ejection period. It is the delay that ECG + PPG devices use as their PTT signal for blood pressure trends.

## Folder layout

```
index.html                       the console (Queue, ECG analysis, PPG analysis, Scoring guide),
                                 with both detectors and all sample recordings built in
data/mitdb100_5min.csv           MIT-BIH record 100 excerpt (time_s, ecg_mV)
data/mitdb100_5min_rpeaks.csv    reference R-peak times for that excerpt
data/ppg_resting_100hz.csv       resting PPG + ECG (time_s, ppg, ecg_mV)
data/ppg_icu_a103l_250hz.csv     ICU PPG + ECG (time_s, pleth, ecg_II_mV)
python/rpeak.py                  ECG reference implementation and scoring
python/ppg.py                    PPG reference implementation and ECG pairing
matlab/rpeak_detect.m            ECG R-peaks (base MATLAB, no toolboxes)
matlab/rpeak_score.m             sensitivity / PPV against reference beats
matlab/ppg_detect.m              PPG peaks, feet, quality, pulse rate (base MATLAB)
matlab/ppg_pair_ecg.m            pulse arrival time for each R-peak
matlab/run_ppg_demo.m            runs both PPG recordings, prints results, plots 10 s of each
```

### MATLAB

Run from the repo root:

```matlab
addpath matlab

% ECG
d = readmatrix('data/mitdb100_5min.csv'); fs = 360;
[pk, info] = rpeak_detect(d(:,2), fs);
ref = round(readmatrix('data/mitdb100_5min_rpeaks.csv') * fs) + 1;
s = rpeak_score(pk, ref, fs)

% PPG (prints pulses, pulse rate, match with ECG and pulse arrival time for both recordings)
run_ppg_demo
```

### Python

```bash
pip install numpy scipy wfdb
cd python
python rpeak.py path/to/mitdb/100      # full MIT-BIH record from PhysioNet
python ppg.py path/to/challenge/a103l  # any WFDB record with a PLETH channel
```

## Next steps

- SpO₂ from the MAX30102 red and IR channels (ratio of ratios, then a calibration curve)
- Calibrate pulse arrival time against cuff readings to turn it into a blood pressure trend
- Port both detectors to ESP32 firmware (C/C++) and run them on live AD8232 + MAX30102 data

## Data

- **MIT-BIH Arrhythmia Database:** Moody GB, Mark RG. The impact of the MIT-BIH Arrhythmia Database. *IEEE Eng in Med and Biol* 20(3):45–50, 2001. Distributed by PhysioNet under the Open Data Commons Attribution License v1.0.
- **PhysioNet/CinC Challenge 2015, record a103l:** Clifford GD, Silva I, Moody B, et al. The PhysioNet/Computing in Cardiology Challenge 2015: Reducing False Arrhythmia Alarms in the ICU. *Computing in Cardiology* 42:273–276, 2015. Distributed by PhysioNet under ODC-By 1.0.
- **NeuroKit2 example dataset `bio_resting_5min_100hz`:** Makowski D, Pham T, Lau ZJ, et al. NeuroKit2: A Python toolbox for neurophysiological signal processing. *Behavior Research Methods* 53:1689–1696, 2021. MIT licence.
- **PhysioNet:** Goldberger AL, et al. PhysioBank, PhysioToolkit, and PhysioNet. *Circulation* 101(23):e215–e220, 2000.
- **PPG peak method:** Elgendi M, Norton I, Brearley M, Abbott D, Schuurmans D. Systolic peak detection in acceleration photoplethysmograms measured from emergency responders in tropical conditions. *PLoS ONE* 8(10):e76585, 2013.
