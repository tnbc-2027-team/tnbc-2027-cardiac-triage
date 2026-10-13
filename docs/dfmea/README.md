# DFMEA (risk analysis)

The competition requires a DFMEA: a list of how each part of the device could fail, what that would do to the patient, and how we prevent it. Every failure mode must have a fix.

## How to fill it in

1. Pick one part of the device, for example the BP cuff.
2. Ask: how could it fail?
3. Write what that does to the patient or user.
4. Rate **Severity** and **Occurrence** from 1 to 5 using the scale below.
5. Add a fix and the test that proves the fix works.

| Score | Severity | Occurrence |
| --- | --- | --- |
| 1 | No injury, just annoying | Very unlikely |
| 2 | Discomfort | Unlikely |
| 3 | Minor injury, or delayed triage | Possible |
| 4 | Injury needing treatment, or wrong triage | Likely |
| 5 | Serious injury | Very likely |

**Best fixes first:** change the design so the failure can't happen, then add something that catches it. A warning label is the weakest fix.

## Example rows

These are examples, not team decisions.

| Part | Failure | Effect on patient | S | O | Fix | Tested by |
| --- | --- | --- | --- | --- | --- | --- |
| BP cuff | Pump keeps running | Painful pressure on the arm | 5 | 2 | Hardware pressure cut-off and timer | Bench test |
| BP cuff | Power lost mid-inflation | Cuff stays tight | 4 | 2 | Valve that opens when power is lost | Bench test |
| SpO₂ | Reading off on darker skin | Low oxygen missed | 4 | 3 | Test across skin tones; show reading confidence | Accuracy test |

Any failure with severity 5 needs a fix, however unlikely it seems.
