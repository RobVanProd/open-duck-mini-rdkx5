# Phase 2 Curriculum Gate Ledger

status: `HOLD_PHASE2_STAGE_Z005_SUPPORT`
generated_at: `2026-06-29T18:03:12Z`

This is a read-only stage-advancement ledger. It did not train, SSH, deploy, or touch the robot.

## Candidate

- candidate: `policy/candidates/phase2_stagea2_seed5_recovery_command_gated_gain099_20260629/candidate.onnx`
- candidate_sha256: `209b85a75cf9cbbcf10df573c1b530921943a72e81082111889c15f63a9a2c7b`

## Stage Status

| stage | status | held gates | missing gates | advance if pass |
|---|---|---|---|---|
| `stage_a2_z002_regression` | `PASS_STAGE` | `none` | `none` | `stage_z005_support` |
| `stage_z005_support` | `HOLD_STAGE` | `z005_x008_nopush, z005_x000_nopush` | `none` | `stage_z005_gentle_push` |

## Gate Matrix

| gate | status | runs | falls | complete | x | z | push | track ratio mean | vx mean | max tracking p95 | max vel excess | push success | reasons |
|---|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|---|
| `z002_x008_nopush` | `PASS_GATE` | 8 | 0 | 8 | 0.080 | 0.002 | `False` | 0.4053 | 0.0324 | 0.1975 | 0.0000 | NA | none |
| `z002_x000_nopush` | `PASS_GATE` | 8 | 0 | 8 | 0.000 | 0.002 | `False` | NA | 0.0007 | 0.0663 | 0.0000 | NA | none |
| `z002_x008_gentle_push` | `PASS_GATE` | 8 | 0 | 8 | 0.080 | 0.002 | `True` | 0.4104 | 0.0328 | 0.1944 | 0.0000 | 0.9704 | none |
| `z002_x000_gentle_push` | `PASS_GATE` | 8 | 0 | 8 | 0.000 | 0.002 | `True` | NA | 0.0007 | 0.0687 | 0.0000 | 0.9704 | none |
| `z005_x008_nopush` | `HOLD_GATE` | 8 | 1 | 7 | 0.080 | 0.005 | `False` | -0.0687 | -0.0055 | 0.1968 | 0.0000 | NA | fall_count 1 != 0; duration_complete_count 7 != 8; track_ratio_mean -0.06870628283133526 < 0.4 |
| `z005_x000_nopush` | `HOLD_GATE` | 8 | 1 | 7 | 0.000 | 0.005 | `False` | NA | -0.0322 | 0.1953 | 0.0000 | NA | fall_count 1 != 0; duration_complete_count 7 != 8; abs mean vx 0.03217386128413998 > 0.005 |

## Decision

- current_stage: `stage_z005_support`
- decision: continue z=0.005 support training from the corrected-bridge candidate.
- do not advance to z=0.005 push or stronger terrain until z=0.005 no-push gates pass.
