# Phase 2 z=0.0075 Live-Oracle Iter3 Seed-0 Recovery Rate150

status: `HOLD_ITER3_DAGGER_DATA_DID_NOT_TRANSFER`

This is an offline behavior-cloned candidate trained from the iter3 live-oracle
DAgger aggregate. It is preserved for reproducibility, but it is not promoted.

## Files

- `candidate.onnx`
- `student.npz`

## Hashes

- candidate.onnx: `c809fe2e784371f2a8c4c3f39507a6ed3efd02b1bea33e1aaf56401537f93151`
- student.npz: `d07c036211b0e213c638660c95aa531d8b4270dafac4885e590c462910a52e17`

## Fit

- manifest: `outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter3_seed0_recovery_run/live_oracle_dagger_aggregate_manifest.json`
- dataset_id: `ddbeda5b717074b6`
- samples: `51175`
- MAE: `0.009558`
- p95 abs error: `0.028781`
- max abs error: `0.403406`
- target-rate p95: `1.369416 rad/s`
- target-rate max: `4.487093 rad/s`
- ONNX max abs error: `0.00000024`

## Compact Boundary Screen

z=0.0075 rough terrain, fitted corrected bridge, intermediate pushes
0.075-0.125:

- x=0.08 seed 0: `HOLD_CANDIDATE_FALL_OR_TERMINATION`, 126 samples,
  track ratio `2.0714`, p95/max velocity excess `0.0000/0.0000`
- x=0.08 seed 7: `HOLD_CANDIDATE_TARGET_VELOCITY`, 750 samples,
  track ratio `0.4257`, p95/max velocity excess `0.0000/0.0962`
- x=0.0 seeds 0 and 1: `PASS_CANDIDATE_SIM_GATE`, mean vx `0.0008 m/s`,
  no velocity excess

## Decision

Do not promote this candidate. The added iter3 live-oracle recovery samples
preserved zero-command behavior but did not fix the x=0.08 seed-0 push/pitch
failure and slightly regressed seed 7 into a max corrected-envelope excess.

No robot validation, SSH, deploy, grounded replay, runtime behavior change, or
PPO training was performed.
