# Software

Code that runs on a computer, not the device: data logging, accuracy analysis against reference instruments, and any display or UI.

Add a short note here on how to run your tool when you add one.

## Cardiac Triage Console (prototype)

`triage-console/` holds the ECG and PPG triage prototype, built by Shaina (software lead).
To run it, open `triage-console/index.html` in any browser. No install needed.
See `triage-console/README.md` for the detectors, sample data, and the Python and MATLAB versions.

## Test data

- `test-data/spo2-synthetic/`: **made-up** SpO₂ and heart rate scenarios (healthy, hypoxemia, critical, deteriorating, bradycardia, finger dropout, motion spikes) for testing triage logic. Not real sensor data. See its README.
- Real ECG recorded with our own board is in `firmware/ecg-v1/data/`. The CSVs load straight into the triage console.
