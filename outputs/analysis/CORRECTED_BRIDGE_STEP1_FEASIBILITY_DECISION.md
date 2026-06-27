# Corrected Bridge Step 1 Feasibility Decision

status: `HOLD_OLD_TEACHER_SOURCE_NOT_CORRECTED_BRIDGE_FEASIBLE`

This is offline sim analysis only. It does not SSH, deploy, train, or touch
robot hardware.

## Inputs

Corrected bridge:

```text
outputs/analysis/actuator_response_fit_corrected_knee.json
sha256: 3661543d0745073b561eb4fa2ae8f9616368ee8b72cb397f8b953dada532c8c0
```

Reroll:

```text
policy: policy/BEST_WALK_ONNX_2.onnx
command_x: 0.08
task: flat_terrain_backlash
bridge_mode: fitted
duration: 15 seconds
seeds: 0-7
artifact: outputs/analysis/CORRECTED_BRIDGE_BEST_WALK_REROLL_X008.md
json: outputs/analysis/corrected_bridge_best_walk_reroll_x008.json
```

Window mine:

```text
artifact: outputs/analysis/CORRECTED_BRIDGE_TEACHER_WINDOWS_X008.md
json: outputs/analysis/corrected_bridge_teacher_windows_x008.json
```

## Reroll Result

`BEST_WALK_ONNX_2` does not clear the corrected bridge gate:

```text
pass: 0/8
duration_complete: 7/8
falls: 1/8
mean track ratio including fall seed: -0.1002
median track ratio among all seeds: 0.4853
max_pitch_vel_p95 mean: 5.1147 rad/s
max corrected per-joint velocity excess mean: 2.4227 rad/s
max tracking p95 mean: 0.2661 rad
```

Per-seed result:

| seed | status | samples | vx | track_ratio | max_vel_p95 | max_vel_excess | tracking_p95 |
|---:|---|---:|---:|---:|---:|---:|---:|
| 0 | `HOLD_CANDIDATE_TRACKING` | 750 | 0.0367 | 0.4591 | 5.0040 | 2.2540 | 0.2637 |
| 1 | `HOLD_CANDIDATE_TRACKING` | 750 | 0.0400 | 0.4997 | 5.1842 | 2.4342 | 0.2642 |
| 2 | `HOLD_CANDIDATE_TRACKING` | 750 | 0.0388 | 0.4852 | 5.0962 | 2.3462 | 0.2606 |
| 3 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 64 | -0.3375 | -4.2187 | 5.2400 | 2.9541 | 0.2940 |
| 4 | `HOLD_CANDIDATE_TRACKING` | 750 | 0.0409 | 0.5117 | 5.1465 | 2.3965 | 0.2598 |
| 5 | `HOLD_CANDIDATE_TRACKING` | 750 | 0.0388 | 0.4851 | 5.2297 | 2.4797 | 0.2651 |
| 6 | `HOLD_CANDIDATE_TRACKING` | 750 | 0.0388 | 0.4854 | 5.0401 | 2.2901 | 0.2590 |
| 7 | `HOLD_CANDIDATE_TRACKING` | 750 | 0.0393 | 0.4911 | 4.9770 | 2.2270 | 0.2620 |

## Corrected Window Mine

Corrected per-joint pitch-chain limits:

| joint | limit rad/s |
|---|---:|
| left_hip_pitch | 2.50 |
| left_knee | 3.25 |
| left_ankle | 2.75 |
| right_hip_pitch | 2.25 |
| right_knee | 2.75 |
| right_ankle | 2.00 |

Window result:

```text
windows checked: 1030
pass windows: 1
pass left-stance windows: 0
pass right-stance windows: 0
top rejection reason: over_corrected_envelope, 1029/1030 windows
```

The single passing window is not a usable stance-balanced teacher source:

```text
seed: 1
ticks: 245-269
center_side: double_support
majority_side: double_support
mean_vx: 0.0462 m/s
left_stance_pct: 24%
right_stance_pct: 24%
max_velocity_excess: 0
```

## Hypothesis Check

Hypothesis:

```text
The previous left-stance / right-knee one-sidedness was an artifact of the old
85 degree knee asymmetry. With the knee fixed, corrected mined windows may
naturally balance across both stance sides.
```

Result:

```text
not supported by this corrected-bridge reroll
```

The corrected bridge does not reveal a balanced set of old-policy teacher
windows. It removes the old asymmetry confound, but the old source is still
dominated by target-rate violations under the corrected per-joint envelope.

## Decision

Do not use old-bridge teacher data or old source-VX selectors as current
training evidence.

Do not carry forward the old right-knee-cap relabel hack as if it were the
current solution. The corrected data did not show a balanced source that makes
the hack unnecessary; it showed the old source is mostly not corrected-bridge
feasible at all.

Next offline work should generate or learn a new deployable policy directly
against the corrected bridge, using the corrected per-joint gate. If using any
old teacher/selector machinery, first rebuild the source data under the
corrected bridge and treat old selectors as historical diagnostics only.
