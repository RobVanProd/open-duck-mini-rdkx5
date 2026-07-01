# Phase 2 z=0.0025 Zero-Command Seed-5 Recovery Decision

status: `HOLD_ZERO_COMMAND_RECOVERY_NOT_DISTILLED`

## Trigger

The rate1p9 contact+phase student passed the x=0.08 z=0.0025 full gate 8/8, but failed
the x=0.0 z=0.0025 full gate on seed 5:

- seed 5 samples: `43`
- termination: `fall_or_nan`
- mean_local_vx: `-0.3468 m/s`
- base_height_min: `0.0575 m`
- max_tracking_p95: `0.2106 rad`

## Diagnostics

### Zero-Action Policy

The constant-zero ONNX policy also fails x=0.0 seed 5.

`rough_terrain_backlash`, z-scale `0.0025`:

- status: `HOLD_CANDIDATE_FALL_OR_TERMINATION`
- samples: `44`
- mean_local_vx: `-0.3652 m/s`
- base_height_min: `0.0410 m`

`flat_terrain_backlash`:

- status: `HOLD_CANDIDATE_FALL_OR_TERMINATION`
- samples: `48`
- mean_local_vx: `-0.3322 m/s`
- base_height_min: `0.0420 m`

Interpretation: seed 5 is not solved by commanding zero action. A zero-action relabel is
not an adequate stand-recovery oracle for this reset.

### BEST_WALK_ONNX_2

`BEST_WALK_ONNX_2` completes x=0.0 seed 5 for 15s on z=0.0025 rough terrain:

- status: `HOLD_CANDIDATE_TARGET_VELOCITY`
- samples: `750`
- termination: `duration_complete`
- mean_local_vx: `0.0019 m/s`
- base_height_min: `0.1456 m`
- max_tracking_p95: `0.0380 rad`
- p95 velocity excess: `0.0000 rad/s`
- max instantaneous velocity excess: `2.9900 rad/s`

Interpretation: the active stand-recovery behavior exists, but BEST has an instantaneous
velocity spike and is not directly promotable as a candidate.

## Distillation Attempts

### One-Trace Zero-Action Relabel

Added the failed 43-sample seed-5 trace relabeled to zero action. The resulting student
still failed x=0.0 seed 5:

- samples: `44`
- mean_local_vx: `-0.3620 m/s`
- base_height_min: `0.0441 m`

### Weighted Zero-Action Relabel

Upweighted the same short seed-5 zero-action relabel entry with `sample_weight=20`.
The resulting student still failed x=0.0 seed 5:

- samples: `43`
- mean_local_vx: `-0.3501 m/s`
- base_height_min: `0.0569 m`

### BEST Recovery Trace

Added a full-duration BEST x=0.0 seed-5 recovery trace as the stand-recovery label source.
The resulting student still failed x=0.0 seed 5:

- samples: `48`
- mean_local_vx: `-0.3100 m/s`
- base_height_min: `0.0588 m`

## Decision

The rate1p9 candidate remains the best boundary result because it passes x=0.08 8/8
in-envelope, but it is not promotable due to x=0.0 seed 5.

The blocker is no longer "add more zero-action samples." Zero action itself fails the
reset, and one-shot BC does not distill BEST's active recovery behavior into the current
contact+phase MLP. The next branch should treat x=0 seed-5 recovery as a closed-loop
stand-recovery representation/training problem:

- collect more active stand-recovery traces, not zero-action labels;
- prefer live-oracle DAgger on the student's own x=0 drift states;
- consider a recurrent/frame-stacked student or a separate command-conditioned stand
  recovery head;
- preserve the existing rate1p9 x=0.08 full-gate pass as the boundary reference.

No robot test, SSH, deploy, grounded replay, runtime behavior change, PPO training, or
policy deployment was performed.
