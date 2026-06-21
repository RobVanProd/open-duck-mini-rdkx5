# Sim-To-Real Results Summary

Last updated: 2026-06-21

## Executive Summary

Current recommendation: **do not run grounded replay yet**.

The first evidence gates no longer point to a gross IMU axis flip, policy hash
mismatch, joint order failure, or zero-command policy explosion. The Duck can
hold home pose, pass the labeled IMU tilt sanity check, pass software feedback
joint identity, and run suspended `x=0.0` with clean timing and good tracking.

The first nonzero suspended command, `x=0.08`, looked like normal walking in
the air to the operator, but telemetry shows sustained dynamic tracking lag and
increased servo-bus read errors. This makes ground/contact testing premature.

## Evidence Files

Small summaries:

- `outputs/analysis/FIRST_EVIDENCE_SUMMARY.md`
- `outputs/first_evidence/20260621T202826Z/imu_tilt_labeled_summary.md`
- `outputs/first_evidence/20260621T202826Z/joint_identity_summary.md`
- `outputs/first_evidence/20260621T215022Z/suspended_policy_replay_x0_after_wire_routing_threshold_gate.md`
- `outputs/first_evidence/20260621T215022Z/suspended_policy_replay_x008_thresholds_gate.md`
- `outputs/first_evidence/20260621T215022Z/suspended_policy_replay_x008_thresholds_analysis.md`
- `outputs/first_evidence/20260621T215022Z/suspended_policy_replay_x008_thresholds_warnings.md`

Raw JSONL logs and terminal logs remain outside git by default.

## Config Snapshot

From `outputs/analysis/FIRST_EVIDENCE_SUMMARY.md`:

- board hostname: `ubuntu`
- runtime path: `/home/sunrise/project/Open_Duck_Mini_Runtime-2_RDK_X5`
- policy SHA256: `3c606f9381a1710cc8fecdb7442787dcbfce3ee9bc02a6f1224774ab2b3a1067`
- `imu_upside_down`: `True`
- `start_paused`: `True`
- `phase_frequency_factor_offset`: `0.0`
- IMU calibration file: `None`

Notable live offsets:

- `left_knee`: `-1.4880 rad`
- `right_knee`: `0.0798 rad`

The large left-knee offset remains a watch item, but home pose and joint
identity evidence show the compensated feedback path is not obviously broken.

## Home Pose Gate

From `outputs/first_evidence/20260621T215022Z/home_pose_after_pr4_analysis.md`:

- samples: `213`
- gyro means: `[0.0000, -0.0001, 0.0001]`
- upright accel mean: `[1.6028, 0.4430, 9.6695]`
- accel is +Z dominant
- joint tracking errors are small at home

Status: **PASS / watch x-axis accel bias**.

This weakens the gross IMU-axis-flip hypothesis. Upright accel is not perfectly
centered on x/y, but it is stable and +Z dominant.

## IMU Tilt Gate

From `outputs/first_evidence/20260621T202826Z/imu_tilt_labeled_summary.md`:

- upright accel: `[1.622, 0.338, 9.792]`
- nose forward changes `accel_x` negative: delta `-5.984 m/s^2`
- nose backward changes `accel_x` positive: delta `+4.602 m/s^2`
- left tilt changes `accel_y` negative: delta `-5.498 m/s^2`
- right tilt changes `accel_y` positive: delta `+4.994 m/s^2`

Status: **PASS / IMU frame now less likely as root cause**.

The policy receives raw gyro and accel, not RPY. These logs show the physical
tilt axes are separated and repeatable.

## Foot Contact Gate

From `outputs/analysis/FIRST_EVIDENCE_SUMMARY.md`:

- contact channels changed independently
- all four contact states appeared
- raw GPIO `False` maps to contact `True`

Status: **PASS for electrical responsiveness**.

The operator sequence was not timestamp-labeled, so this proves electrical
response and polarity behavior, not a strict left-first/right-first script.

## Joint Identity Gate

From `outputs/first_evidence/20260621T202826Z/joint_identity_summary.md`:

- all 14 joints passed software feedback identity
- commanded `+/-0.03 rad` produced measured `+/-0.03 rad` responses
- worst small-step tracking error: `0.0060 rad`
- one CRC mismatch printed during the run

Status: **PASS for servo ID/order and feedback sign**.

Physical visual direction is still not fully annotated. This remains less
likely than dynamic tracking because the feedback identity test passed cleanly.

## Suspended Replay `x=0.0`

From
`outputs/first_evidence/20260621T215022Z/suspended_policy_replay_x0_after_wire_routing_threshold_gate.md`:

- samples: `747`
- command: `[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]`
- gate: `WARN_PROCEED_WITH_CAUTION`
- dt mean / p95 / p99 / max: `0.02009 / 0.02009 / 0.02010 / 0.02015 s`
- read errors: `8 / 747 = 1.071%`
- write errors: `0`
- action saturation: `0%`
- bus read burst count: `0`
- post-startup tracking spikes above `0.05 rad`: `0`

Pitch joint post-startup tracking stayed small:

| joint | p95 abs tracking error |
|---|---:|
| left_hip_pitch | `0.0098 rad` |
| left_knee | `0.0082 rad` |
| left_ankle | `0.0074 rad` |
| right_hip_pitch | `0.0100 rad` |
| right_knee | `0.0056 rad` |
| right_ankle | `0.0029 rad` |

Status: **WARN_PROCEED_WITH_CAUTION**.

Interpretation: zero-command suspended replay does not show a wild policy,
gross action mapping failure, or free-air actuator collapse.

## Suspended Replay `x=0.08`

From
`outputs/first_evidence/20260621T215022Z/suspended_policy_replay_x008_thresholds_gate.md`:

- samples: `747`
- command: `[0.08, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]`
- gate: `HOLD_CRC_OR_TIMING`
- dt mean / p95 / p99 / max: `0.02010 / 0.02009 / 0.02010 / 0.02603 s`
- read errors: `20 / 747 = 2.677%`
- write errors: `0`
- read burst detected: `[609, 612, 612]`
- action saturation:
  - `right_hip_pitch`: `2.01%`
  - `right_ankle`: `0.13%`
- largest tracking spike: tick `200`, `left_hip_pitch`, `0.2688 rad`
- post-startup tracking spikes above `0.05 rad`: `2492`

Pitch joint tracking at `x=0.08`:

| joint | p95 abs tracking error | max abs tracking error |
|---|---:|---:|
| left_hip_pitch | `0.1433 rad` | `0.2688 rad` |
| left_knee | `0.1431 rad` | `0.2264 rad` |
| left_ankle | `0.1179 rad` | `0.2002 rad` |
| right_hip_pitch | `0.1287 rad` | `0.1757 rad` |
| right_knee | `0.1673 rad` | `0.2085 rad` |
| right_ankle | `0.1218 rad` | `0.1962 rad` |

Offline lag check, post-startup:

| joint | target range | actual range | best lag |
|---|---:|---:|---:|
| left_hip_pitch | `0.349 rad` | `0.276 rad` | `4 ticks` |
| left_knee | `0.356 rad` | `0.323 rad` | `3 ticks` |
| left_ankle | `0.244 rad` | `0.203 rad` | `3 ticks` |
| right_hip_pitch | `0.249 rad` | `0.270 rad` | `3 ticks` |
| right_knee | `0.361 rad` | `0.321 rad` | `3 ticks` |
| right_ankle | `0.280 rad` | `0.247 rad` | `3 ticks` |

Operator observation: the robot looked like it was walking in the air, with no
explicit visible twitch/asymmetry reported. This is consistent with coherent
gait motion plus measurable phase lag, not total policy nonsense.

Status: **HOLD**.

Interpretation: do not move to grounded replay. The nonzero command already
shows sustained actuator/feedback tracking lag in suspension.

## Root-Cause Ranking

1. **Dynamic actuator tracking / phase lag at nonzero command**
   - Evidence: `x=0.08` pitch joints show p95 errors of `0.1179-0.1673 rad`
     and best target-to-actual lag of `3-4` ticks.
2. **Servo bus read reliability under motion**
   - Evidence: read errors rise from `8/747` at `x=0.0` to `20/747` at
     `x=0.08`, with one read burst. Write errors remain zero and dt is clean,
     so this is not the only explanation, but it is now a serious watch item.
3. **Policy command magnitude / action saturation at `x=0.08`**
   - Evidence: `right_hip_pitch` hits action saturation `2.01%`, while `x=0.0`
     had `0%`.
4. **Joint offsets/home pose**
   - Evidence: large left-knee offset is suspicious, but home pose and small
     identity movements track well after compensation.
5. **Joint sign/order**
   - Evidence: software feedback identity passed all joints; physical visual
     sign notes remain incomplete.
6. **IMU frame/offset**
   - Evidence: home pose and labeled tilt are +Z dominant and axis-separated.
7. **Foot contacts**
   - Evidence: electrical responsiveness passed; suspended replay does not
     depend on ground contact.
8. **Ground contact/friction/load**
   - Evidence: not tested yet; do not test until suspended `x=0.08` dynamics
     are understood.

## Next Action

Choose exactly one next hardware gate: **actuator_sine_sweep**, supported on
the stand, with small default amplitude and telemetry + terminal logging.

Purpose:

- isolate actuator tracking from policy output
- measure phase lag versus frequency on hip pitch, knee, and ankle
- see whether read CRC rate rises with motion speed/amplitude
- decide whether the next minimal fix is bus reliability, velocity/rate limits,
  actuator command shaping, or sim actuator modeling

Do not run grounded replay until this is understood.
