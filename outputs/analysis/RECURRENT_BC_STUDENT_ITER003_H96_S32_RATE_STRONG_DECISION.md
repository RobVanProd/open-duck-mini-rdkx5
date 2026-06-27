# Recurrent BC Student Iter003 H96/S32 Strong-Rate Decision

status: `HOLD_RECURRENT_RATE_REG_WORSE`

## Summary

This bounded follow-up tested whether the first recurrent BC student's
closed-loop failure was mainly caused by insufficient supervised target-rate
regularization.

Configuration:

```text
manifest: outputs/analysis/live_oracle_dagger_phase_student/iter_003/live_oracle_dagger_aggregate_manifest.json
hidden_dim: 96
sequence_length: 32
steps: 1500
target_rate_scale: 1.0
target_rate_limit_rad_s: 2.5
```

Supervised fit:

```text
MAE: 0.0455
p95 action error: 0.1285
target-rate p95: 2.0405 rad/s
target-rate max: 5.6063 rad/s
ONNX max action error: 5.64e-7
ONNX max hidden error: 9.43e-7
```

Canonical fitted-bridge gate:

```text
task: flat_terrain_backlash
command_x: 0.08
duration: 15 s
seeds: 0-7
falls: 8/8
duration_complete: 0/8
samples_mean: 49.75
track_ratio_mean: -4.3735
mean_vx: -0.3499 m/s
max_pitch_vel_p95: 5.24 rad/s on every seed
```

## Interpretation

Stronger supervised target-rate regularization improved the supervised
target-rate p95, but it made closed-loop behavior worse: every seed reversed
hard, fell quickly, and still hit the sim slew ceiling.

This narrows the recurrent path:

```text
plain recurrent BC:      fits labels, fails closed-loop
strong rate recurrent BC: lower supervised rate, worse closed-loop reverse/fall
```

The missing ingredient is not more scalar supervised rate pressure. The next
recurrent attempt needs live closed-loop correction pressure, e.g. rollout-loss,
DAgger with stability-targeted relabeling, or PPO-style correction from the
stateful BC initializer. Do not keep increasing the supervised target-rate
scale as a local tweak.

## Artifacts

```text
fit:  outputs/analysis/RECURRENT_BC_STUDENT_ITER003_H96_S32_RATE_STRONG.md
gate: outputs/analysis/RECURRENT_BC_STUDENT_ITER003_H96_S32_RATE_STRONG_GATE.md
json: outputs/analysis/recurrent_bc_student_iter003_h96_s32_rate_strong.json
json: outputs/analysis/recurrent_bc_student_iter003_h96_s32_rate_strong_gate.json
```

## Decision

```text
HOLD_RECURRENT_RATE_REG_WORSE
next: stop supervised-rate-only recurrent BC; move to closed-loop correction or refit bridge after corrected knee hardware
```
