# Synthetic SpO₂ test data

> **This is made-up data, not real sensor recordings.** It was generated to test triage logic. Don't use it to judge how accurate our sensor or SpO₂ algorithm is.

Seven hardcoded patient scenarios, each 5 minutes long at one reading per second. Use them to test the High / Medium / Low triage logic and the console's handling of edge cases before we have real MAX30102 data. Shared by Rushil, 2026-11-06.

## Files

| File | Scenario | `priority` column |
|---|---|---|
| `patient_A_healthy.csv` | SpO₂ 97 to 99%, heart rate 67 to 76 | LOW throughout |
| `patient_B_mild_hypoxemia.csv` | SpO₂ 90 to 94%, heart rate 90 to 100 | MEDIUM throughout |
| `patient_C_critical.csv` | SpO₂ 81 to 87%, heart rate 131 to 145 | HIGH throughout |
| `patient_D_deteriorating.csv` | Starts healthy and gets steadily worse | LOW, then MEDIUM from ~90 s, then HIGH from ~210 s |
| `patient_E_bradycardia.csv` | Normal SpO₂, heart rate 40 to 48 | MEDIUM throughout |
| `patient_F_finger_dropout.csv` | Finger comes off the sensor twice (60 to 85 s and 190 to 205 s) | LOW, NO_SIGNAL during dropouts |
| `patient_G_noisy_motion.csv` | Healthy patient with several 3-second motion spikes | LOW, but HIGH during each spike |
| `all_patients_combined.csv` | All seven in one file, with a `patient` column | |

## Columns

| Column | Meaning |
|---|---|
| `time_s` | Seconds from the start |
| `spo2_pct` | SpO₂ in % (empty when there's no signal) |
| `hr_bpm` | Heart rate in bpm (empty when there's no signal) |
| `priority` | Priority for that one second on its own: `LOW`, `MEDIUM`, `HIGH` or `NO_SIGNAL`. It isn't smoothed, so in `patient_G` it marks the false motion spikes as HIGH. |
| `signal_ok` | 1 = good signal, 0 = no signal |

These are already-calculated SpO₂ and heart rate values, not the raw red and IR light signal. So they test what happens *after* SpO₂ is worked out (the triage scoring), not the SpO₂ calculation itself. For raw PPG to test that, see `software/triage-console/data/`.

Good checks to run:
- Does `patient_D` get flagged as it gets worse?
- Does `patient_F` show "no signal" instead of a bad number?
- Does `patient_G` avoid raising a HIGH alarm for a 3-second spike? (Here a good result *disagrees* with the `priority` column.)
