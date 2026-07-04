# Phase 2 z0.0075 Iter21 Seed6/7 Weight2 + Seed1 Recovery Rate150

Status: `HOLD_SEED1_RECOVERED_SEED2_REGRESSED_REVERSE`

This candidate starts from the balanced + seed6/7 weight2 manifest and adds one low-weight
seed1 post-push recovery snippet. It fixes the seed1 failure while preserving seeds 0, 6,
and 7, but fails seed2 with reverse motion in the missing-seed screen.

## Files

- `candidate.onnx`
- source manifest: `outputs/analysis/phase2_z0075_iter21_balanced_seed67_weight2_plus_seed1_merged_manifest.json`
- student report: `outputs/analysis/PHASE2_Z0075_ITER21_BALANCED_SEED67_WEIGHT2_PLUS_SEED1_RATE150_STUDENT.md`
- compact screen: `outputs/analysis/PHASE2_Z0075_ITER21_BALANCED_SEED67_WEIGHT2_PLUS_SEED1_RATE150_X008_SEED0_1_6_7_SCREEN.md`
- missing-seed screen seed2 hold: `outputs/analysis/phase2_z0075_iter21_balanced_seed67_weight2_plus_seed1_rate150_student/x008_seed2_3_4_5_screen/iter21_seed67_w2_seed1/seed_002/CLOSED_LOOP_ACTUATOR_BRIDGE_EVAL.md`

## Hashes

- candidate ONNX sha256: `2706d5ad727bd1fa0499a0aa3c66042c9942f75c7d591f1301734cc56d6a6960`
- student NPZ sha256: `90210ca4d019677465ec2fa5fb8765d18ea2bdbe34f21e1f38aad7e39c2438e6`
- merged manifest sha256: `98dacdabc03a664bd07fa568145ef18cd8ce2f0422d675c01e0632d85a64f67d`

## Compact Screen

| seed | status | samples | track_ratio | max_vel_excess |
|---:|---|---:|---:|---:|
| 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.3136 | 0.0000 |
| 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.3545 | 0.0000 |
| 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.3061 | 0.0000 |
| 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.3405 | 0.0000 |

## Missing-Seed Hold

The missing-seed screen was stopped after seed2 failed:

- seed2: `HOLD_CANDIDATE_FALL_OR_TERMINATION`
- samples: `282`
- termination: `fall_or_nan`
- track ratio: `-0.4738`
- mean local vx: `-0.0379 m/s`
- max pitch-chain sent velocity p95: `1.5591 rad/s`
- max corrected-envelope excess: `0.0000 rad/s`
- max tracking p95: `0.1842 rad`
- base height min: `0.0816 m`

The new failure is reverse/low-progress collapse, still inside the corrected envelope.

## Decision

Do not deploy or promote this candidate. The low-weight recovery strategy is improving
targeted seeds, but the memoryless student remains seed-fragile: fixing one failure mode
can still move another seed into reverse motion.
