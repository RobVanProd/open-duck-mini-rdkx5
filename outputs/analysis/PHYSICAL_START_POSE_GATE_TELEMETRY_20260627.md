# Physical Start-Pose Gate Telemetry - 2026-06-27

status: `PASS_PHYSICAL_HOME_POSE_VISUAL_CHECK`

## Summary

The supported `home_pose_log_test` passed the software/telemetry portion of the
start-pose gate. Repo-rendered zero/home references were generated afterward,
and Rob confirmed the commanded home pose visually matches the rendered home
pose. This downranks start/home pose mismatch as the leading walking-failure
cause.

This does not prove a fresh joint-by-joint zero recalibration was run after
later robot work. It does mean blind `find_soft_offsets.py` recalibration is
not justified without a visible mismatch.

Motors were turned off after the test.

## Evidence

- config snapshot:
  `outputs/first_evidence/20260627T003945Z_physical_start_pose_gate/20260627T003909Z_rdkx5_config_snapshot.json`
- telemetry:
  `outputs/first_evidence/20260627T003945Z_physical_start_pose_gate/home_pose_physical_pose_gate.jsonl`
- terminal log:
  `outputs/first_evidence/20260627T003945Z_physical_start_pose_gate/home_pose_physical_pose_gate_terminal.log`
- analysis:
  `outputs/first_evidence/20260627T003945Z_physical_start_pose_gate/home_pose_physical_pose_gate_analysis.md`

## Telemetry Result

- samples: `216`
- accel mean: `[1.6831, 0.0569, 9.6848]`, upright +Z dominant
- bus read errors: `0`
- bus write errors: `0`
- analyzer warnings: `none`
- contacts: `0` left / `0` right, expected for supported/free feet

Leg tracking p95 while holding home:

| joint | p95 abs rad | max abs rad |
|---|---:|---:|
| left_hip_pitch | 0.001 | 0.023 |
| left_knee | 0.004 | 0.135 |
| left_ankle | 0.003 | 0.051 |
| right_hip_pitch | 0.002 | 0.031 |
| right_knee | 0.005 | 0.110 |
| right_ankle | 0.000 | 0.001 |

## Current Live Offsets

The fresh snapshot matched the prior live offsets:

| joint | offset rad |
|---|---:|
| left_hip_pitch | -0.0890 |
| left_knee | -1.4880 |
| left_ankle | -0.0767 |
| right_hip_pitch | 0.0660 |
| right_knee | 0.0798 |
| right_ankle | 0.1887 |

## Interpretation

This clears basic supported home holding: the runtime can command home, the
compensated readback tracks it, the bus counters stayed clean, and IMU +Z is
dominant.

It also clears the practical physical home-pose check by operator comparison
against the repo-rendered MJCF home pose.

Runtime commands and readback both apply `duck_config.joints_offsets`, so
telemetry alone can look correct even if physical zero is wrong. However, if
the commanded home pose matches the rendered home pose, the current offsets are
probably close enough for the start-pose gate.

## Next Gate

Do not rerun `find_soft_offsets.py` unless a physical mismatch appears. If
offsets are changed later, back up `duck_config.json`, capture the printed
offsets, compare old vs new, and rerun `home_pose_log_test` after any config
change.

The main work should return to closed-loop gait / actuator / contact behavior.
