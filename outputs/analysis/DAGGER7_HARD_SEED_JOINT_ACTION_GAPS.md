# DAgger-7 Hard-Seed Joint Action Gaps

status: `PASS_HARD_SEED_JOINT_GAPS_CHARACTERIZED`

Offline analysis only. No robot tests, SSH, deploy, training, or runtime
changes were performed.

## Inputs

Relabel traces:

```text
outputs/analysis/dagger6_targeted_recovery_teacher_relabel_x008_traces/seed_001/trace.jsonl
outputs/analysis/dagger6_targeted_recovery_teacher_relabel_x008_traces/seed_007/trace.jsonl
```

For these files:

```text
original_action = failing DAgger-6 student action
action = source-VX teacher relabel action
gap = abs(original_action - action)
```

## Seed 1

Rows: `31`

Largest action gaps:

| joint | p50 | p95 | max |
|---|---:|---:|---:|
| right_knee | 0.0955 | 0.2234 | 0.3188 |
| left_ankle | 0.0640 | 0.1668 | 0.1789 |
| head_yaw | 0.0557 | 0.1465 | 0.1602 |
| left_knee | 0.0679 | 0.1428 | 0.1513 |
| right_hip_pitch | 0.0759 | 0.1345 | 0.1368 |
| head_pitch | 0.0521 | 0.1256 | 0.1615 |
| right_hip_roll | 0.0536 | 0.1133 | 0.1704 |
| right_ankle | 0.0509 | 0.1095 | 0.1700 |

Final samples before collapse:

| tick | vx | vy | height | contacts |
|---:|---:|---:|---:|---|
| 21 | 0.0309 | 0.5126 | 0.1790 | `10` |
| 22 | 0.0565 | 0.5657 | 0.1768 | `10` |
| 23 | 0.0749 | 0.6309 | 0.1739 | `10` |
| 24 | 0.0827 | 0.7003 | 0.1696 | `10` |
| 25 | 0.0845 | 0.7840 | 0.1634 | `10` |
| 26 | 0.0902 | 0.8730 | 0.1547 | `10` |
| 27 | 0.0975 | 0.9697 | 0.1436 | `10` |
| 28 | 0.0678 | 1.0773 | 0.1306 | `10` |
| 29 | 0.0515 | 1.2019 | 0.1152 | `00` |
| 30 | 0.0309 | 1.3054 | 0.0974 | `10` |

Interpretation: seed 1 is a left-support lateral-collapse case. Teacher
correction is largest on the right knee and both pitch-chain support/swing
joints, but nearest-manifest action mismatch is not high enough to explain the
failure by BC fit alone.

## Seed 7

Rows: `32`

Largest action gaps:

| joint | p50 | p95 | max |
|---|---:|---:|---:|
| right_hip_pitch | 0.0465 | 0.1987 | 0.3574 |
| right_knee | 0.0671 | 0.1899 | 0.2862 |
| head_yaw | 0.0529 | 0.1872 | 0.2353 |
| neck_pitch | 0.0612 | 0.1862 | 0.1933 |
| left_knee | 0.0490 | 0.1792 | 0.3055 |
| left_hip_pitch | 0.0487 | 0.1623 | 0.2772 |
| right_ankle | 0.0629 | 0.1561 | 0.2404 |
| left_ankle | 0.0450 | 0.1541 | 0.2269 |

Final samples before collapse:

| tick | vx | vy | height | contacts |
|---:|---:|---:|---:|---|
| 22 | 0.0833 | -0.5653 | 0.1733 | `01` |
| 23 | 0.0613 | -0.6161 | 0.1709 | `01` |
| 24 | 0.0509 | -0.6639 | 0.1677 | `01` |
| 25 | 0.0251 | -0.7205 | 0.1636 | `01` |
| 26 | 0.0013 | -0.7911 | 0.1584 | `01` |
| 27 | -0.0127 | -0.8763 | 0.1513 | `01` |
| 28 | -0.0299 | -0.9615 | 0.1420 | `01` |
| 29 | -0.0380 | -1.0481 | 0.1298 | `01` |
| 30 | -0.0352 | -1.1341 | 0.1142 | `00` |
| 31 | -0.0188 | -1.2256 | 0.0949 | `01` |

Interpretation: seed 7 is a right-support lateral-collapse case with a real
local action-fit issue. The largest mismatches are right hip pitch, right knee,
and both pitch-chain joints. A split recovery fit should focus on this support
phase rather than globally increasing all recovery labels again.

## Next Use

Use these joint gaps to design the next deployable-policy branch:

```text
seed 1:
  closed-loop lateral/height stabilization during left support

seed 7:
  local right-support pitch-chain action fit
  especially right_hip_pitch, right_knee, right_ankle
```

Do not read this as robot validation permission.
