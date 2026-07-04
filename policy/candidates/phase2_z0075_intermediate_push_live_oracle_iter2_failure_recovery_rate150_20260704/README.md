# Phase 2 z=0.0075 Live-Oracle Iter2 Failure Recovery Rate150

status: `HOLD_PUSH_WINDOW_PITCHOVER_SEED0`

This is an offline-only behavior-cloned student trained from targeted
live-oracle DAgger recovery data on the z=0.0075 rough-terrain
intermediate-push boundary.

## Files

- `candidate.onnx`
- `student.npz`

## Hashes

- candidate.onnx: `23b94150e2914bdb9cab5c90bbb27686cf4eaa6db24ce79000ae72724171a916`
- student.npz: `e1ab2e1d65c28d8952ee696fb9b9a49ae66114e27a4c0b7e04b0cabfc95a98c7`

## Fit

- manifest: `outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_run/live_oracle_dagger_aggregate_manifest.json`
- dataset_id: `ad1f4a6a5446d648`
- samples: `48815`
- MAE: `0.009422`
- p95 abs error: `0.029820`
- max abs error: `0.487725`
- target-rate p95: `1.371563 rad/s`
- target-rate max: `2.462790 rad/s`
- ONNX max abs error: `0.00000030`

## Compact Boundary Screen

z=0.0075 rough terrain, x=0.08, intermediate push 0.075-0.125:

- seed 0: `HOLD_CANDIDATE_FALL_OR_TERMINATION`, 689 samples, track ratio `0.7277`, p95 velocity excess `0.0000`, max velocity excess `0.0638`
- seed 7: `PASS_CANDIDATE_SIM_GATE`, 750 samples, track ratio `0.3747`, p95/max velocity excess `0.0000`

## Decision

Do not promote this candidate. It improves the previous full-distribution
regression by recovering seed 7 and delaying seed 0 to a late push-window
failure, but seed 0 still pitches over during the final active push recovery
window.

No robot validation, SSH, deploy, grounded replay, runtime behavior change, or
PPO training was performed.
