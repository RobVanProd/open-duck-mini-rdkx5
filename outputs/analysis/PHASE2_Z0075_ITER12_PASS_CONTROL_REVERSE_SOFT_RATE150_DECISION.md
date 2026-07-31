# Phase 2 z=0.0075 Iter12 Pass-Control Reverse-Soft Rate150 Decision

status: `HOLD_PASS_CONTROL_WEIGHTING_REGRESSION`

## Scope

- offline sim/data curation only; no robot, SSH, deploy, grounded replay, runtime behavior changes, or PPO training.

## Candidate

`policy/candidates/phase2_z0075_iter12_pass_control_reverse_soft_rate150_20260704/candidate.onnx`

- candidate sha256: `fe106a1cd24ffdf6f982e7064cd2cdcdc6c3433ee43a253caadfe0850a4d400b`
- student npz sha256: `b4da637b5efbb9dccaa8bff7d08a072868a47f942ab12274d59a3b0dbf996de5`
- pass-control manifest: `outputs/analysis/phase2_z0075_iter12_iter10_pass_control_manifest.json` (`6f720e613ad37ece`, 2250 samples)
- weighted pass-control manifest: `outputs/analysis/phase2_z0075_iter12_pass_control_weighted_manifest.json` (`5f61f95b64a3c3f9`, weight 4.0)
- softened reverse manifest: `outputs/analysis/phase2_z0075_iter12_reverse_oracle_soft_weight_manifest.json` (`f42cc71c5126b2bf`, entry weight 0.4)
- merged manifest: `outputs/analysis/phase2_z0075_iter12_pass_control_reverse_soft_merged_manifest.json` (`47912c84835029ba`, 55636 samples)

## What Changed

This run added full-observation pass-control traces from Iter10's known passing seeds `0`, `4`, and `7`, weighted those entries by `4.0`, and softened the Iter11 reverse-oracle relabel entries with an entry weight of `0.4`.

The intent was to preserve Iter10's pass-control behavior while retaining a smaller anti-reverse correction signal.

## Fit Metrics

| metric | value |
|---|---:|
| MAE | 0.009437 |
| p95 abs error | 0.030804 |
| max abs error | 0.425876 |
| target-rate p95 rad/s | 1.381992 |
| target-rate max rad/s | 2.518001 |
| ONNX max abs error | 0.00000024 |

## Full 8-Seed x=0.08 Intermediate-Push Gate

z=0.0075 rough terrain backlash, fitted corrected bridge, x=0.08, push magnitude `0.075-0.125` every `1.0-1.5s`.

| seed | status | samples | termination | track ratio | p95 excess | max excess | tracking p95 | push success |
|---:|---|---:|---|---:|---:|---:|---:|---:|
| 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 690 | `fall_or_nan` | 0.6608 | 0.0000 | 0.0000 | 0.1905 | 0.9091 |
| 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 546 | `fall_or_nan` | 0.7842 | 0.0000 | 0.2696 | 0.1910 | 0.8889 |
| 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 153 | `fall_or_nan` | 1.7330 | 0.0000 | 0.0000 | 0.2091 | 0.5000 |
| 3 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 444 | `fall_or_nan` | -0.2795 | 0.0000 | 0.0000 | 0.1825 | 0.7500 |
| 4 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 311 | `fall_or_nan` | 1.0557 | 0.0000 | 0.0873 | 0.1876 | 0.8000 |
| 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 47 | `fall_or_nan` | -3.9058 | 0.0000 | 0.0000 | 0.2223 | NA |
| 6 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 685 | `fall_or_nan` | 0.6455 | 0.0000 | 0.0000 | 0.1873 | 0.9167 |
| 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 475 | `fall_or_nan` | 0.7873 | 0.0000 | 0.0000 | 0.1934 | 0.8333 |

Distribution summary:

- pass: `0/8`
- falls / terminations: `8/8`
- duration complete: `0/8`
- mean track ratio: `0.1851`
- mean local vx: `0.0148 m/s`
- max p95 corrected-envelope excess: `0.0000 rad/s`
- max instantaneous corrected-envelope excess: `0.2696 rad/s`
- max tracking p95: `0.2223 rad`
- mean push success: `0.7997`

## Decision

`HOLD_PASS_CONTROL_WEIGHTING_REGRESSION`

Do not promote. Explicit pass-control weighting did not preserve Iter10's passing seeds; the candidate failed all eight seeds. It delayed several failures and kept p95 envelope excess at zero, but it traded away every known pass while leaving seed `5` as an early reverse/pitchback failure.

## Next Recommendation

Stop treating additional supervised weighting as a reliable way to compose seed-local fixes in this feed-forward BC student. The next useful branch should either:

1. move to a stateful/live-oracle DAgger representation that can preserve mode-specific behavior, or
2. run a focused diagnostic on seed `5` initial/reset sensitivity before adding more labels.

Do not robot validate this candidate.
