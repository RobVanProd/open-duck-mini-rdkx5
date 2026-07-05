# Phase 2 z0.0075 Iter22 Live-Oracle History-Context Rate150

Status: `HOLD_LIVE_ORACLE_RECOVERS_SEED7_REGRESSES_0_6`

This deployable-contract feed-forward student was trained on the first
live-oracle DAgger aggregate from the history-context branch:

`outputs/analysis/live_oracle_dagger_phase_student/iter_022_history_context/live_oracle_dagger_aggregate_manifest.json`

It keeps the runtime policy interface:

`obs[1,101] -> continuous_actions[1,14]`

## Files

- `candidate.onnx`
- `candidate_mlp.npz`
- student report: `outputs/analysis/PHASE2_Z0075_ITER22_LIVE_ORACLE_HISTORY_CONTEXT_RATE150_STUDENT.md`
- compact screen: `outputs/analysis/PHASE2_Z0075_ITER22_LIVE_ORACLE_HISTORY_CONTEXT_RATE150_X008_SEED0_1_2_6_7_SCREEN.md`
- decision: `outputs/analysis/PHASE2_Z0075_ITER22_LIVE_ORACLE_HISTORY_CONTEXT_RATE150_DECISION.md`

## Hashes

- candidate ONNX sha256: `f76a9db11a99dba8de5c01e2c3fe5c46b461209df449401046839cc3adc3f1e5`
- student NPZ sha256: `cd28c90f8a09460fad17c6eda2a933eca7fbf7ab5fb15fa19955ca670c4d4dca`
- aggregate manifest sha256: `f948bbe63d927e55f7db4b13484df160f37bec3e98c2f1dd3bbfe9a6fff1703c`

## Compact Screen

| seed | status | samples | track_ratio | max_vel_excess |
|---:|---|---:|---:|---:|
| 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 639 | 0.0197 | 0.0000 |
| 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.3979 | 0.0000 |
| 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.4087 | 0.0000 |
| 6 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 120 | 2.0231 | 0.0000 |
| 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.3726 | 0.0000 |

## Decision

Do not promote. It recovered seed7 but regressed seeds 0 and 6. The live-oracle
wrapper has been updated to collect the next iteration with canonical
`--reset-settle-ticks 10`.
