# Left pitch-chain gain suspended x=0.08 result

Date: 2026-07-12

Status: `REJECT_GAIN_31_34_HOLD_TRACKING_VISUAL_CLEAN`

Frozen intervention: left hip pitch P 31, left knee P 34; all other gains and
runtime variables unchanged.

```text
samples:                  747 / 747
CRC/reset/write errors:   0 / 0 / 0
control overruns:         0
dt max:                   0.02018 s
cleanup:                  normal gains restored, torque disabled
```

Matched gate comparison:

| joint | normal P30 p95 | P31/34 p95 | change |
|---|---:|---:|---:|
| left hip pitch | 0.0513 | 0.0514 | +0.0001 rad |
| left knee | 0.0572 | 0.0569 | -0.0003 rad |

The hip did not improve and the knee improvement was only 0.017 degrees. Head
yaw also reached 0.0558 rad in the gain run. The unchanged gate therefore holds.
Rob reported the motion looked clean, but visual quality does not override the
numeric result. Do not increase gains post hoc.

The runs were not state-matched: mean policy accelerometer Y was 0.4331 m/s^2
in the normal-gain run and 0.9532 m/s^2 in the gain run, causing different
closed-loop policy targets. A fixed-target A/B replay is required to isolate
actuator gain from policy/IMU feedback before concluding whether gain has any
causal tracking effect.

Evidence hashes:

```text
JSONL:    e659a5def5ca642343dadbcf687b1641600917630fc2190520a030656f94e06d
terminal: edc6068946c0ee17c95b20f4facc49e8924941694d030815516a8d452b265c6e
analysis: 4aebc55bfcc87bc401c2d36ec0737e68d082c83a1095c024f8af699b35ed5b55
```
