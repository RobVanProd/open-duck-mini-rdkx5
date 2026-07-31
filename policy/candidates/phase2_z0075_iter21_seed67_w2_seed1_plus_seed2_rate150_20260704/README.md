# Phase 2 z0.0075 Iter21 Seed6/7 Weight2 + Seed1 + Seed2 Recovery Rate150

Status: `HOLD_SEED2_RECOVERED_SEED7_REGRESSED_REVERSE`

This candidate adds one low-weight seed2 reverse-recovery snippet to the previous
seed6/7-weight2 + seed1 manifest. It recovers seed2 while preserving seeds 0, 1, and 6,
but regresses seed7 into reverse/low-progress collapse.

## Files

- `candidate.onnx`
- source manifest: `outputs/analysis/phase2_z0075_iter21_seed67_w2_seed1_plus_seed2_merged_manifest.json`
- student report: `outputs/analysis/PHASE2_Z0075_ITER21_SEED67_W2_SEED1_PLUS_SEED2_RATE150_STUDENT.md`
- compact screen: `outputs/analysis/PHASE2_Z0075_ITER21_SEED67_W2_SEED1_PLUS_SEED2_RATE150_X008_SEED0_1_2_6_7_SCREEN.md`

## Hashes

- candidate ONNX sha256: `364cf5ce6c79cdd75a89ff3ee4dc77f8b062296ceeeeaefe1d0dccfb2212ed49`
- student NPZ sha256: `ea928c23978047eb0853f12215aec883492eda94b4152e1e583f70b7d68ad671`
- merged manifest sha256: `3398b064c7454faae25d046c630450b4060e3dca58251d0e9c709adfb99029fa`

## Compact Screen

| seed | status | samples | track_ratio | max_vel_excess |
|---:|---|---:|---:|---:|
| 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.3842 | 0.0000 |
| 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.3679 | 0.0000 |
| 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.3398 | 0.0000 |
| 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.3100 | 0.0000 |
| 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 288 | -0.5495 | 0.0000 |

## Decision

Do not deploy or promote this candidate. The low-weight patch loop is now cycling: seed6/7
recovery regressed seed1, seed1 recovery regressed seed2, and seed2 recovery regressed
seed7. All failures remain inside the corrected actuator envelope, so this is not a
velocity-budget issue.

The next useful branch should change representation or conditioning rather than append
another memoryless low-weight recovery snippet.
