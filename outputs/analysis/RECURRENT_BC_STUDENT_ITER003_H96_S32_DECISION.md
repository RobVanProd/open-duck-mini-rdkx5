# Recurrent BC Student Iter003 H96/S32 Decision

status: `HOLD_RECURRENT_BC_CLOSED_LOOP_UNSTABLE`

## Summary

The recurrent evaluator and trainer work, but the first substantive recurrent
BC student is not a candidate.

Supervised fit improved substantially over the 80-step smoke:

```text
manifest: outputs/analysis/live_oracle_dagger_phase_student/iter_003/live_oracle_dagger_aggregate_manifest.json
hidden_dim: 96
sequence_length: 32
steps: 1500
MAE: 0.0266
p95 action error: 0.0737
target-rate p95: 2.2925 rad/s
ONNX max action error: 5.63e-7
ONNX max hidden error: 9.83e-7
```

However, the canonical closed-loop fitted-bridge gate failed on every seed:

```text
task: flat_terrain_backlash
command_x: 0.08
duration: 15 s
seeds: 0-7
falls: 8/8
duration_complete: 0/8
track_ratio_mean: -0.9339
mean_vx: -0.0747 m/s
max_pitch_vel_p95: 5.24 rad/s on every seed
max_tracking_p95 range: 0.2165-0.2816 rad
```

## Interpretation

This falsifies the cheap version of the recurrence hypothesis:

```text
small Elman RNN + supervised BC on current aggregate manifest
```

The model can fit the oracle labels in supervised sequence space, but in
closed-loop it leaves the demonstrated manifold, drives pitch-chain targets to
the sim slew ceiling, reverses on several seeds, and falls on all seeds.

That means recurrence alone is not enough. The next recurrent attempt must add
closed-loop correction pressure, stronger target-rate regularization, or a
better live-oracle training loop. Do not promote this ONNX and do not run it on
the robot.

## Artifacts

```text
fit:  outputs/analysis/RECURRENT_BC_STUDENT_ITER003_H96_S32.md
gate: outputs/analysis/RECURRENT_BC_STUDENT_ITER003_H96_S32_GATE.md
json: outputs/analysis/recurrent_bc_student_iter003_h96_s32.json
json: outputs/analysis/recurrent_bc_student_iter003_h96_s32_gate.json
```

## Decision

```text
HOLD_RECURRENT_BC_CLOSED_LOOP_UNSTABLE
next: do not tune static feed-forward variants; recurrent path needs closed-loop/live-oracle correction, not plain BC
```
