# Left-Knee Offset Correction Recorded

status: `PASS_CORRECTION_RECORDED_FROM_OPERATOR_REPORT`

This is a reduced record of the operator-reported hardware/config correction.
It is not a raw robot log and does not imply a walking validation pass.

## Reported Change

```text
date: 2026-06-27
backup: /home/sunrise/duck_backups/20260627T165814Z_left_knee_offset/duck_config.json
left_knee: -1.488 -> 0.0371
right_knee: 0.0798 unchanged
```

Reported hashes:

```text
backup:  087868f8178598f49a2ab4eab1c77b73ed8cd3af33174c543119cb016d69e9e9
current: 131a7b8fce1107b14f4727562f44f9e17324caf7fc22512ad7115911f050991b
```

Reported short stand monitor after update:

```text
Configured knee soft offsets:
  left_knee        +0.0371 rad +2.13 deg
  right_knee       +0.0798 rad +4.57 deg

left joint        +2.44 deg
right joint       +3.07 deg
L-R joint         -0.63 deg
home_delta L-R    +0.00 deg
```

Torque was reportedly left off at the end of the monitor run.

## Interpretation

The old `left_knee=-1.488` offset was a major calibration outlier. After this
correction, the previous actuator response fit and any prior real-robot
tracking conclusions involving the left knee should be treated as stale for
final hardware validation.

## Next Gate

Before robot walking, rerun supported actuator tracking diagnostics on the
corrected hardware and regenerate:

```text
outputs/analysis/actuator_response_fit_corrected_knee.json
outputs/analysis/ACTUATOR_RESPONSE_FIT_CORRECTED_KNEE.md
```

No grounded replay or walking policy replay is authorized by this record.
