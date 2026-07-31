# Phase 2 z0.0075 Iter26 Dual-Anchor Weight2 History-Context Rate150

Status: `HOLD_ITER26_DUAL_ANCHOR_WEIGHT2_BROAD_REGRESSION`

This deployable-contract feed-forward student was trained on:

`outputs/analysis/phase2_z0075_iter26_dual_anchor_weight2_aggregate_manifest.json`

It keeps the runtime policy interface:

`obs[1,101] -> continuous_actions[1,14]`

## Files

- `candidate.onnx`
- `candidate_mlp.npz`
- student report: `outputs/analysis/PHASE2_Z0075_ITER26_DUAL_ANCHOR_WEIGHT2_HISTORY_CONTEXT_RATE150_STUDENT.md`
- x=0.08 compact screen: `outputs/analysis/PHASE2_Z0075_ITER26_DUAL_ANCHOR_WEIGHT2_HISTORY_CONTEXT_RATE150_X008_SEED0_1_2_6_7_SCREEN.md`
- decision: `outputs/analysis/PHASE2_Z0075_ITER26_DUAL_ANCHOR_WEIGHT2_HISTORY_CONTEXT_RATE150_DECISION.md`

## Hashes

- candidate ONNX sha256: `c7e859c94cf1ff155927619b9c99481b71fe878f7174d27537a76fe94565dc53`
- student NPZ sha256: `47860855424eee2d2282a80d07d90e50fc5d37e00a7f7fa29e68832375fb9ba6`
- aggregate manifest sha256: `a26a8d0dd1dcdd4e0a244def7768e5ef0d74962c84880e2966bae8f2949f90ef`

## Compact x=0.08 Screen

| seed | status | samples | track_ratio | max_vel_excess |
|---:|---|---:|---:|---:|
| 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 554 | 0.7815 | 0.0000 |
| 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 593 | -0.0009 | 0.0000 |
| 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 286 | -0.5101 | 0.0000 |
| 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.3491 | 0.0000 |
| 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 397 | 0.9271 | 0.0000 |

## Decision

Do not promote. Weight2 produced a broad regression; scalar dual-anchor
weighting is not the right next mechanism for this BC student.
