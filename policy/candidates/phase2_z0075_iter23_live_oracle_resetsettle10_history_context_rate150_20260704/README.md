# Phase 2 z0.0075 Iter23 Live-Oracle Reset-Settle10 History-Context Rate150

Status: `HOLD_ITER23_LIVE_ORACLE_SEED2_REVERSE`

This deployable-contract feed-forward student was trained on the corrected
reset-settle live-oracle DAgger aggregate:

`outputs/analysis/live_oracle_dagger_phase_student/iter_023_history_context_resetsettle10/live_oracle_dagger_aggregate_manifest.json`

It keeps the runtime policy interface:

`obs[1,101] -> continuous_actions[1,14]`

## Files

- `candidate.onnx`
- `candidate_mlp.npz`
- student report: `outputs/analysis/PHASE2_Z0075_ITER23_LIVE_ORACLE_RESETSETTLE10_HISTORY_CONTEXT_RATE150_STUDENT.md`
- compact screen: `outputs/analysis/PHASE2_Z0075_ITER23_LIVE_ORACLE_RESETSETTLE10_HISTORY_CONTEXT_RATE150_X008_SEED0_1_2_6_7_SCREEN.md`
- decision: `outputs/analysis/PHASE2_Z0075_ITER23_LIVE_ORACLE_RESETSETTLE10_HISTORY_CONTEXT_RATE150_DECISION.md`

## Hashes

- candidate ONNX sha256: `38536ea5c3efcbd207e48743cbde5a0e899978c4726b3cfca001d2e54e449a33`
- student NPZ sha256: `fcdfdf832c9b2b834c399949a4fb79f63dfb0af71d69fdf1e2236f7f226ffb31`
- aggregate manifest sha256: `b4602b20a53d246a5b95f75a37b68c7020d28c5602a104370504599225c4d467`

## Compact Screen

| seed | status | samples | track_ratio | max_vel_excess |
|---:|---|---:|---:|---:|
| 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.4012 | 0.0000 |
| 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.3544 | 0.0000 |
| 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 282 | -0.5509 | 0.0000 |
| 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.3311 | 0.0000 |
| 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.3479 | 0.0000 |

## Decision

Do not promote. Corrected-settle live-oracle DAgger recovered seeds 0 and 6
relative to iter22 but left seed2 as the active reverse/fall failure.
