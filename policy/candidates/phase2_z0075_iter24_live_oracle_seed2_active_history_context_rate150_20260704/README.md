# Phase 2 z0.0075 Iter24 Live-Oracle Seed2-Active History-Context Rate150

Status: `HOLD_ITER24_LIVE_ORACLE_SEED6_REGRESSION`

This deployable-contract feed-forward student was trained on the iter24
corrected reset-settle live-oracle DAgger aggregate:

`outputs/analysis/live_oracle_dagger_phase_student/iter_024_history_context_resetsettle10_seed2_active/live_oracle_dagger_aggregate_manifest.json`

It keeps the runtime policy interface:

`obs[1,101] -> continuous_actions[1,14]`

## Files

- `candidate.onnx`
- `candidate_mlp.npz`
- student report: `outputs/analysis/PHASE2_Z0075_ITER24_LIVE_ORACLE_SEED2_ACTIVE_HISTORY_CONTEXT_RATE150_STUDENT.md`
- x=0.08 compact screen: `outputs/analysis/PHASE2_Z0075_ITER24_LIVE_ORACLE_SEED2_ACTIVE_HISTORY_CONTEXT_RATE150_X008_SEED0_1_2_6_7_SCREEN.md`
- x=0.0 compact screen: `outputs/analysis/PHASE2_Z0075_ITER24_LIVE_ORACLE_SEED2_ACTIVE_HISTORY_CONTEXT_RATE150_X0_SEED0_1_SCREEN.md`
- decision: `outputs/analysis/PHASE2_Z0075_ITER24_LIVE_ORACLE_SEED2_ACTIVE_HISTORY_CONTEXT_RATE150_DECISION.md`

## Hashes

- candidate ONNX sha256: `31a5c2d20d0ae33733c82d0280ca8a297035d74b2a62cc35055b11ebeb152670`
- student NPZ sha256: `ed24bdae116c628f72b4a96eb8dfb88ae060c9987ee348447fc8e25650083c5e`
- aggregate manifest sha256: `3532495e898a2166846f082254384b3a7de88c49637ff713136a7b4dd7c8be6a`

## Compact x=0.08 Screen

| seed | status | samples | track_ratio | max_vel_excess |
|---:|---|---:|---:|---:|
| 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.3256 | 0.0000 |
| 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.3584 | 0.0000 |
| 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.3278 | 0.0000 |
| 6 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 250 | -0.5659 | 0.0000 |
| 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.3437 | 0.0000 |

## Compact x=0.0 Screen

| seed | status | samples | mean_local_vx | max_vel_excess |
|---:|---|---:|---:|---:|
| 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.0007 | 0.0000 |
| 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.0009 | 0.0000 |

## Decision

Do not promote. Iter24 recovered the iter23 seed2 reverse/fall but regressed
seed6 into reverse/fall. The candidate preserves x=0.0 behavior on the compact
screen and stays inside the corrected velocity envelope, but it is not
seed-robust enough for robot validation.
