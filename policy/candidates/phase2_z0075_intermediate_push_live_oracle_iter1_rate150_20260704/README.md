# Phase 2 z=0.0075 Intermediate-Push Live-Oracle Iter1 Rate150

status: `HOLD_FULL_SEED_DISTRIBUTION_REGRESSED`

This is an offline-only behavior-cloned student trained from a current-student
live-oracle DAgger iteration on the z=0.0075 rough-terrain intermediate-push
boundary.

## Files

- `candidate.onnx`
- `student.npz`

## Hashes

- candidate.onnx: `2364d1540b6165474075d5506a3681450757304161add0763ae496f706ee7684`
- student.npz: `1bf410bd854baee0ea6ae3efc78cc5a532a4fe45ad5e8d1b505d8c0220aa1e8d`

## Fit

- manifest: `outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter1_rate150_run/live_oracle_dagger_aggregate_manifest.json`
- dataset_id: `f772391aca069fa4`
- samples: `45501`
- MAE: `0.011864`
- p95 abs error: `0.038300`
- max abs error: `0.571110`
- target-rate p95: `1.304301 rad/s`
- target-rate max: `1.832521 rad/s`
- ONNX max abs error: `0.00000021`

## Gates

Compact z=0.0075 intermediate-push screen:

- x=0.08 seeds 0,7: `2/2 PASS`, zero p95/max corrected velocity excess.
- x=0.0 seeds 0,1: `2/2 PASS`, zero p95/max corrected velocity excess.

Full x=0.08 z=0.0075 intermediate-push 8-seed gate:

- pass: `2/8`
- falls/terminations: `5/8`
- low-progress holds: `1/8`

## Decision

Do not promote this candidate. The added live-oracle state coverage fixed the
compact spike case but regressed the broad seed distribution.

No robot validation, SSH, deploy, grounded replay, runtime behavior change, or
PPO training was performed.
