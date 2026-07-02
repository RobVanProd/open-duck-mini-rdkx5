# Phase 2 z0.0026 Teacher Continuity 81920 Seed 5 Failure Analysis

status: `HOLD_SEED5_SUPPORT_COLLAPSE`

This analyzes the traced failing seed from the preserved A100 81920 checkpoint:

`outputs/analysis/colab_cli_downloads/extracted/open_duck_colab_cli_phase2-z002-teacher-continuity_20260701T223519Z/open_duck_colab_cli_phase2-z002-teacher-continuity_20260701T223519Z/open_duck_training_phase2_z002_teacher_continuity_cli/smoke_20260701T223737Z_gpu/2026_07_01_224518_81920.onnx`

## Result

- Seed 5 terminates at 65 ticks / 1.28 s with `fall_or_nan`.
- Mean local vx is `-0.2279 m/s`, track ratio `-2.8483`.
- Base height falls from `0.1498 m` to `0.0667 m`.
- Body pitch reaches `-1.4412 rad`; p95 absolute pitch is `1.2589 rad`.
- Contact state is mostly double support: `83.1%` double, `9.2%` single, `7.7%` flight.

## Actuator Envelope

Pitch-chain sent target rates remain inside the corrected actuator limits:

| joint | p95 rad/s | max rad/s | corrected limit rad/s | p95 utilization | max utilization |
|---|---:|---:|---:|---:|---:|
| left_hip_pitch | 1.3390 | 1.8636 | 2.50 | 0.54 | 0.75 |
| left_knee | 1.7227 | 2.0782 | 3.25 | 0.53 | 0.64 |
| left_ankle | 1.4976 | 1.8521 | 2.75 | 0.54 | 0.67 |
| right_hip_pitch | 1.4391 | 1.6818 | 2.25 | 0.64 | 0.75 |
| right_knee | 1.8446 | 2.1212 | 2.75 | 0.67 | 0.77 |
| right_ankle | 1.4126 | 1.6486 | 2.00 | 0.71 | 0.82 |

This failure is not caused by corrected-envelope velocity excess.

## Contact / Stability Timeline

| ticks | contact state |
|---|---|
| 0-1 | flight |
| 2-4 | double support |
| 5-6 | left only |
| 7-8 | double support |
| 9 | right only |
| 10-56 | double support |
| 57 | right only |
| 58 | double support |
| 59 | right only |
| 60 | left only |
| 61 | double support |
| 62-64 | flight |

The long middle segment is planted double support while local vx trends negative. The terminal collapse starts around tick 45:

| tick | base height | local vx | local vy | pitch | contact |
|---:|---:|---:|---:|---:|---|
| 45 | 0.181 | -0.206 | 0.037 | -0.389 | double |
| 50 | 0.176 | -0.423 | 0.008 | -0.531 | double |
| 55 | 0.169 | -0.641 | -0.007 | -0.743 | double |
| 60 | 0.141 | -1.060 | 0.117 | -1.175 | left only |
| 62 | 0.111 | -1.307 | 0.204 | -1.381 | flight |
| 64 | 0.067 | -1.491 | 0.253 | -1.388 | flight |

## Interpretation

The 81920 checkpoint is close but not promotable: the full x=0.08 z=0.0026 gate is 7/8, with seed 5 as the lone fall. Seed 5 is a support/contact stability failure, not an actuator over-rate failure. It gets stuck in double support, drifts backward, then loses base height and exits contact.

Next training should target seed-5 support/reverse collapse while preserving the 7 passing seeds' in-envelope behavior. Broad actuator tracking penalties are not the primary lever for this failure.
