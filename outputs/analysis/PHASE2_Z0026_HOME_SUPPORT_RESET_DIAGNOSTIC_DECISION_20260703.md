# Phase 2 z=0.0026 Home-Support Reset Diagnostic Decision

status: `HOLD_Z0026_HOME_SUPPORT_LOW_PROGRESS`

This was an offline evaluator diagnostic only. It did not SSH, deploy, run
robot tests, change robot runtime behavior, train, or run grounded replay.

## Purpose

The z=0.0026 seed-5 failure was traced to a no-contact randomized reset state.
This diagnostic added an eval-only `--reset-mode home-support` path that starts
the closed-loop evaluator from sim home qpos, zero qvel, and home ctrl before
the policy loop. The default reset mode remains `playground`.

The goal was to test whether the `81920` teacher-continuity parent fails because
the policy cannot handle z=0.0026 motion, or because the current randomized
reset can start it outside a physically representative standing support
manifold.

## Parent

```text
outputs/analysis/colab_cli_downloads/extracted/open_duck_colab_cli_phase2-z002-teacher-continuity_20260701T223519Z/open_duck_colab_cli_phase2-z002-teacher-continuity_20260701T223519Z/open_duck_training_phase2_z002_teacher_continuity_cli/smoke_20260701T223737Z_gpu/2026_07_01_224518_81920.onnx
```

## x=0.08 Short Screen

Artifact:

```text
outputs/analysis/PHASE2_Z0026_TC81920_HOME_SUPPORT_X008_SHORT.md
```

Result:

```text
duration:             2.0 s
seeds:                0-7
reset_mode:           home-support
falls:                0/8
duration_complete:    8/8
status:               HOLD_CANDIDATE_TRACKING on all seeds
mean_vx:              0.0248 m/s
track_ratio:          0.3099
max_pitch_vel_p95:    1.7518 rad/s
p95_vel_excess:       0.0000
max_tracking_p95:     0.2054 rad
single_support:       8.0 %
double_support:       92.0 %
```

The seed-5 fall disappears under home-support reset. The remaining x=0.08 hold
is low-progress/double-support tracking, not instability and not corrected
velocity-envelope excess.

## x=0.0 Short Screen

Artifact:

```text
outputs/analysis/PHASE2_Z0026_TC81920_HOME_SUPPORT_X000_SHORT.md
```

Result:

```text
duration:             2.0 s
seeds:                0-7
reset_mode:           home-support
falls:                0/8
duration_complete:    8/8
status:               PASS_CANDIDATE_SIM_GATE on all seeds
mean_vx:              0.0051 m/s
max_pitch_vel_p95:    1.0279 rad/s
p95_vel_excess:       0.0000
max_tracking_p95:     0.0959 rad
double_support:       100.0 %
```

The same parent preserves x=0.0 standing semantics under home-support reset.

## Decision

The current `playground` randomized reset is too broad to treat the z=0.0026
seed-5 fall as a normal grounded-start policy failure. Seed 5 begins from a
no-contact state produced by reset randomization, and replacing that start with
home-support removes the fall.

This does not promote the parent. Under grounded-home reset it still moves too
slowly at x=0.08 and remains double-support dominant. The next training/eval
branch should use an explicit reset contract:

- grounded-home/support reset for the normal walking gate, if that matches the
  real robot start protocol
- a separate unsupported-start recovery gate only if recovery from airborne or
  no-contact reset states is intentionally required

Do not silently mix these two contracts. The Phase 2 walking candidate still
needs to clear the full corrected-bridge moving-command gate before robot
validation.
