# V7 x=0.08 Onset Analysis

source: `outputs/analysis/movement_bootstrap_v7_x008_failure_trace/v7_x008_trace.jsonl`
status: `PASS_V7_ONSET_ANALYZED`
samples: `59`
done: tick `58` / `1.16s`

## Key Findings

- The fitted-bridge rollout is an over-drive/lunge failure, not an actuator-envelope or saturation failure.
- Forward velocity exceeds the `0.08 m/s` command by tick `3` / `0.06s`; max local vx reaches `1.3183 m/s` at tick `58`.
- Body pitch does not cross `0.25 rad` until tick `15` / `0.30s`, after the velocity overshoot has already started.
- Base height falls below `0.12 m` at tick `52` / `1.04s`, near the end of the pitch-over.
- Contact changes are frequent but not a single obvious first-cause event; the velocity overshoot begins before the large pitch collapse.

## Threshold Crossings

| event | tick | time_s | pitch_rad | vx_m_s | height_m | contacts |
|---|---:|---:|---:|---:|---:|---|
| `pitch_abs_gt_0p25` | 15 | 0.30 | 0.2653 | 0.1199 | 0.1515 | `[1, 1]` |
| `pitch_abs_gt_0p50` | 39 | 0.78 | 0.5154 | 0.1686 | 0.1493 | `[1, 1]` |
| `pitch_abs_gt_1p00` | 52 | 1.04 | 1.0261 | 0.7275 | 0.1188 | `[1, 0]` |
| `local_vx_gt_0p08` | 3 | 0.06 | 0.0007 | 0.0977 | 0.1608 | `[1, 1]` |
| `local_vx_gt_0p24` | 43 | 0.86 | 0.6043 | 0.2658 | 0.1470 | `[1, 1]` |
| `local_vx_gt_0p50` | 49 | 0.98 | 0.8365 | 0.5266 | 0.1351 | `[1, 1]` |
| `height_lt_0p12` | 52 | 1.04 | 1.0261 | 0.7275 | 0.1188 | `[1, 0]` |
| `height_lt_0p08` | 56 | 1.12 | 1.3822 | 1.1060 | 0.0752 | `[1, 1]` |

## Contact Events

| tick | time_s | from | to | pitch_rad | vx_m_s | height_m |
|---:|---:|---|---|---:|---:|---:|
| 2 | 0.04 | `[0, 1]` | `[1, 1]` | 0.0025 | 0.0718 | 0.1580 |
| 6 | 0.12 | `[1, 1]` | `[0, 1]` | 0.0377 | 0.0806 | 0.1658 |
| 11 | 0.22 | `[0, 1]` | `[1, 1]` | 0.1608 | 0.1438 | 0.1555 |
| 52 | 1.04 | `[1, 1]` | `[1, 0]` | 1.0261 | 0.7275 | 0.1188 |
| 53 | 1.06 | `[1, 0]` | `[1, 1]` | 1.1037 | 0.8141 | 0.1108 |
| 57 | 1.14 | `[1, 1]` | `[0, 1]` | 1.4818 | 1.2096 | 0.0585 |
| 58 | 1.16 | `[0, 1]` | `[1, 0]` | 1.4993 | 1.3183 | 0.0388 |

## Timeline

| tick | time_s | pitch | pitch_rate | height | vx | contacts | max_pitch_err | err_joint | lin_vel_reward | imitation |
|---:|---:|---:|---:|---:|---:|---|---:|---|---:|---:|
| 0 | 0.00 | 0.0031 | 0.0000 | 0.1537 | -0.0325 | `[0, 1]` | 0.4057 | `left_knee` | 0.7054 | -12.8667 |
| 1 | 0.02 | 0.0050 | 0.0978 | 0.1564 | -0.0260 | `[0, 1]` | 0.3453 | `right_ankle` | 0.8134 | -7.0805 |
| 2 | 0.04 | 0.0025 | -0.1292 | 0.1580 | 0.0718 | `[1, 1]` | 0.2791 | `right_ankle` | 2.4833 | -0.8612 |
| 3 | 0.06 | 0.0007 | -0.0899 | 0.1608 | 0.0977 | `[1, 1]` | 0.2032 | `right_ankle` | 2.4228 | 1.2301 |
| 4 | 0.08 | 0.0078 | 0.3573 | 0.1633 | 0.0772 | `[1, 1]` | 0.1467 | `left_ankle` | 1.2633 | 0.7840 |
| 5 | 0.10 | 0.0207 | 0.6454 | 0.1652 | 0.0775 | `[1, 1]` | 0.1578 | `left_ankle` | 0.9577 | 0.0025 |
| 6 | 0.12 | 0.0377 | 0.8481 | 0.1658 | 0.0806 | `[0, 1]` | 0.1548 | `left_ankle` | 2.2792 | -1.1687 |
| 10 | 0.20 | 0.1354 | 1.2705 | 0.1583 | 0.1524 | `[0, 1]` | 0.1050 | `left_hip_pitch` | 0.9632 | -0.1633 |
| 11 | 0.22 | 0.1608 | 1.2684 | 0.1555 | 0.1438 | `[1, 1]` | 0.1026 | `left_hip_pitch` | 1.1300 | 0.2532 |
| 15 | 0.30 | 0.2653 | 1.2795 | 0.1515 | 0.1199 | `[1, 1]` | 0.1129 | `right_knee` | 2.1315 | -3.0067 |
| 20 | 0.40 | 0.3428 | 0.4765 | 0.1500 | 0.1061 | `[1, 1]` | 0.0798 | `left_knee` | 2.3355 | 0.6091 |
| 25 | 0.50 | 0.3768 | 0.3176 | 0.1509 | 0.0853 | `[1, 1]` | 0.0618 | `left_ankle` | 2.4931 | -0.9348 |
| 30 | 0.60 | 0.4116 | 0.3815 | 0.1512 | 0.0804 | `[1, 1]` | 0.0674 | `left_ankle` | 2.5000 | 0.4078 |
| 35 | 0.70 | 0.4579 | 0.5360 | 0.1505 | 0.1127 | `[1, 1]` | 0.0905 | `left_knee` | 2.2469 | -1.3084 |
| 40 | 0.80 | 0.5342 | 0.9410 | 0.1489 | 0.1883 | `[1, 1]` | 0.1087 | `left_knee` | 0.7744 | -2.1564 |
| 45 | 0.90 | 0.6651 | 1.6024 | 0.1449 | 0.3352 | `[1, 1]` | 0.0814 | `left_knee` | 0.0037 | 0.6749 |
| 50 | 1.00 | 0.8930 | 2.8236 | 0.1308 | 0.5837 | `[1, 1]` | 0.0576 | `right_ankle` | 0.0000 | 0.4072 |
| 52 | 1.04 | 1.0261 | 3.5060 | 0.1188 | 0.7275 | `[1, 0]` | 0.0560 | `left_ankle` | 0.0000 | -0.9954 |
| 53 | 1.06 | 1.1037 | 3.8805 | 0.1108 | 0.8141 | `[1, 1]` | 0.0681 | `left_ankle` | 0.0000 | -4.4961 |
| 55 | 1.10 | 1.2828 | 4.6739 | 0.0893 | 0.9999 | `[1, 1]` | 0.0587 | `left_ankle` | 0.0000 | -8.2676 |
| 57 | 1.14 | 1.4818 | 4.9812 | 0.0585 | 1.2096 | `[0, 1]` | 0.0510 | `left_ankle` | 0.0000 | -2.4201 |
| 58 | 1.16 | 1.4993 | 0.8745 | 0.0388 | 1.3183 | `[1, 0]` | 0.0532 | `left_ankle` | 0.0000 | 0.7393 |

## V8 Implication

Prioritize a velocity-overshoot and pitch-stability fix over more actuator-envelope work. The trace supports adding penalties/rewards for command overshoot, body pitch/pitch-rate during forward command, and possibly contact-timing regularization after overshoot is controlled.
