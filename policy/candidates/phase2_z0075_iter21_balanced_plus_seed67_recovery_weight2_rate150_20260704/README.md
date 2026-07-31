# Phase 2 z0.0075 Iter21 Balanced + Seed6/7 Recovery Weight2 Rate150

Status: `HOLD_WEIGHT2_RECOVERS_0_6_7_BUT_FAILS_SEED1`

This candidate repeats the seed6/7 recovery experiment with those snippets capped at
sample weight 2.0 instead of the prior full gate-aware weight 5.0.

## Files

- `candidate.onnx`
- source manifest: `outputs/analysis/phase2_z0075_iter21_balanced_plus_seed67_recovery_weight2_merged_manifest.json`
- student report: `outputs/analysis/PHASE2_Z0075_ITER21_BALANCED_PLUS_SEED67_RECOVERY_WEIGHT2_RATE150_STUDENT.md`
- compact screen: `outputs/analysis/PHASE2_Z0075_ITER21_BALANCED_PLUS_SEED67_RECOVERY_WEIGHT2_RATE150_X008_SEED0_6_7_SCREEN.md`
- full-gate seed1 hold: `outputs/analysis/phase2_z0075_iter21_balanced_plus_seed67_recovery_weight2_rate150_student/x008_8seed_gate/iter21_balanced_seed67_w2/seed_001/CLOSED_LOOP_ACTUATOR_BRIDGE_EVAL.md`

## Hashes

- candidate ONNX sha256: `4977b1ae2928e44d1059047b7b26d6e1815dcd8dff2a8cb84695fe75be61caed`
- student NPZ sha256: `493403a1ca1af8b0140d352d6914015bb5d71a3d35aa0a4d89debd2f8038f7e5`
- merged manifest sha256: `6dc64894ac8b5c4a44f1d2b8f05c7d92af771835c48d24e3c3eb80d53495841d`

## Compact Screen

x=0.08, `rough_terrain_backlash`, fitted corrected bridge, z=0.0075 roughness,
intermediate pushes, reset mode `home-support`, reset settle `10`.

| seed | status | samples | track_ratio | max_vel_excess |
|---:|---|---:|---:|---:|
| 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.3618 | 0.0000 |
| 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.3438 | 0.0000 |
| 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.3514 | 0.0000 |

This shows the seed6/7 recovery data is useful when down-weighted; unlike the full-weight
variant, seed0 did not regress.

## Full-Gate Hold

The full x=0.08 8-seed gate was stopped after seed1 failed:

- seed0: `PASS_CANDIDATE_SIM_GATE`
- seed1: `HOLD_CANDIDATE_FALL_OR_TERMINATION`
- seed1 samples: `454`
- seed1 track ratio: `0.7801`
- seed1 max pitch-chain sent velocity p95: `1.6065 rad/s`
- seed1 max corrected-envelope excess: `0.0000 rad/s`
- seed1 max tracking p95: `0.1918 rad`
- seed1 base height min: `0.0153 m`

The failure is still post-push stability transfer, not actuator-envelope excess.

## Decision

Do not deploy or promote this candidate. It is a useful improvement over the full-weight
seed6/7 recovery attempt, but it does not clear the full seed distribution.
