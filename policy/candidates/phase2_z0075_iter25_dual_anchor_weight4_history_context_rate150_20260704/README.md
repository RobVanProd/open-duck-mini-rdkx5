# Phase 2 z0.0075 Iter25 Dual-Anchor Weight4 History-Context Rate150

Status: `HOLD_ITER25_DUAL_ANCHOR_REGRESSES_SEEDS0_7`

This deployable-contract feed-forward student was trained on:

`outputs/analysis/phase2_z0075_iter25_dual_anchor_weight4_aggregate_manifest.json`

It keeps the runtime policy interface:

`obs[1,101] -> continuous_actions[1,14]`

## Files

- `candidate.onnx`
- `candidate_mlp.npz`
- student report: `outputs/analysis/PHASE2_Z0075_ITER25_DUAL_ANCHOR_WEIGHT4_HISTORY_CONTEXT_RATE150_STUDENT.md`
- x=0.08 compact screen: `outputs/analysis/PHASE2_Z0075_ITER25_DUAL_ANCHOR_WEIGHT4_HISTORY_CONTEXT_RATE150_X008_SEED0_1_2_6_7_SCREEN.md`
- decision: `outputs/analysis/PHASE2_Z0075_ITER25_DUAL_ANCHOR_WEIGHT4_HISTORY_CONTEXT_RATE150_DECISION.md`

## Hashes

- candidate ONNX sha256: `4e6b462a0daac0c624044bee58951846340e6382c960d194dd06de16763e9b3d`
- student NPZ sha256: `e58c985d11b01a250f5f09640a23581b0fed0fcca72ed5426452fc6fa2d7afde`
- aggregate manifest sha256: `d6ddd98a535aec2147db157f978eae80669a9718076cf926b2e8f85db9e02467`

## Compact x=0.08 Screen

| seed | status | samples | track_ratio | max_vel_excess |
|---:|---|---:|---:|---:|
| 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 525 | 0.7229 | 0.0000 |
| 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.3567 | 0.0000 |
| 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.3816 | 0.0000 |
| 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.3273 | 0.0000 |
| 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 470 | 0.8327 | 0.0000 |

## Decision

Do not promote. The weight4 dual-anchor aggregate preserved seed2 and seed6 but
regressed seed0 and seed7 into pitch/base-height failures.
