# Phase 2 z0.0075 Iter21 History-Context Rate150

Status: `HOLD_HISTORY_CONTEXT_STILL_REGRESSES_SEED7`

This is a deployable-contract phase-modulated feed-forward student trained from
`outputs/analysis/phase2_z0075_iter21_seed67_w2_seed1_plus_seed2_merged_manifest.json`.
It keeps the runtime policy interface:

`obs[1,101] -> continuous_actions[1,14]`

The modulation path uses richer context already present in the observation:
command, action history, previous motor targets, foot contacts, and phase.

## Files

- `candidate.onnx`
- `candidate_mlp.npz`
- student report: `outputs/analysis/PHASE2_Z0075_ITER21_HISTORY_CONTEXT_RATE150_STUDENT.md`
- compact screen: `outputs/analysis/PHASE2_Z0075_ITER21_HISTORY_CONTEXT_RATE150_X008_SEED0_1_2_6_7_SCREEN.md`
- decision: `outputs/analysis/PHASE2_Z0075_ITER21_HISTORY_CONTEXT_RATE150_DECISION.md`

## Hashes

- candidate ONNX sha256: `84fa4aac2830514cd8671f88201fec731f7f7d26c300abc3eff68c8a971bb086`
- student NPZ sha256: `946f24f1dee2daa7804c6f9bbb6e938db9ff8985380df5cf4a98ad8fce94feb1`
- source manifest sha256: `3398b064c7454faae25d046c630450b4060e3dca58251d0e9c709adfb99029fa`

## Compact Screen

| seed | status | samples | track_ratio | max_vel_excess |
|---:|---|---:|---:|---:|
| 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.3483 | 0.0000 |
| 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.3144 | 0.0000 |
| 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.3787 | 0.0000 |
| 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.2961 | 0.0000 |
| 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 274 | -0.5217 | 0.0000 |

## Decision

Do not promote or validate on the robot. Richer deployable context did not break
the seed7 reverse/fall mode, so the next branch should use live-oracle DAgger or
a diagnostic recurrent/stateful test rather than another static snippet patch.
