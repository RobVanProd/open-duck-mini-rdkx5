# Phase 2 z=0.0075 Seed0 Push-Window Recovery Rate150 Decision

status: `HOLD_PUSH_WINDOW_PITCHOVER_REGRESSION`

## Scope

- offline sim/data curation only; no robot, SSH, deploy, grounded replay, runtime behavior changes, or PPO training.

## Candidate

`policy/candidates/phase2_z0075_seed0_push_window_recovery_rate150_20260704/candidate.onnx`

- candidate sha256: `7bfbc920dd9c7edb423831c3c0aa05b0a444f15640b5e6974a2ac94169ba495e`
- student npz sha256: `6e52662125413c9318ccd5e8b7626b25ee6ac7e8e76e72161d181a36751547f0`
- manifest: `outputs/analysis/phase2_z0075_iter3_seed0_push_window_recovery_manifest.json`
- dataset samples: `49503`

## What Changed

This run added a source-VX teacher relabel of the iter2 seed-0 failure trace and upweighted only ticks `650-687`, the active late push-window recovery region. The terminal fall row was dropped before relabeling, so the weighted labels are teacher labels on student-visited drift states, not the failed candidate action replay.

## Fit Metrics

| metric | value |
|---|---:|
| MAE | 0.00911961 |
| p95 abs error | 0.02997786 |
| max abs error | 0.45050135 |
| target-rate p95 rad/s | 1.36865532 |
| target-rate max rad/s | 3.87133002 |
| ONNX max abs error | 0.00000030 |
| sample weight max | 8.00000000 |

## Compact Boundary Screen

z=0.0075 rough terrain, x=0.08, intermediate push, traced seeds 0 and 7.

| seed | status | samples | termination | track ratio | p95 velocity excess | max velocity excess | max tracking p95 | push success |
|---:|---|---:|---|---:|---:|---:|---:|---:|
| 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 647 | `fall_or_nan` | 0.7116 | 0.0000 | 0.0000 | 0.1869 | 0.9000 |
| 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 633 | `fall_or_nan` | 0.6591 | 0.0000 | 0.0000 | 0.1913 | 0.8750 |

## Failure Diagnostic

`HOLD_PHASE2_INTERMEDIATE_PUSH_WINDOW_PITCHOVER`

| seed | classification | last push tick | pitch>0.8 tick | height<0.08 tick | max excess |
|---:|---|---:|---:|---:|---:|
| 0 | `PUSH_WINDOW_PITCHOVER` | None | 637 | 642 | 0.0000 |
| 7 | `PUSH_WINDOW_PITCHOVER` | None | 624 | 629 | 0.0000 |

## Decision

`HOLD_PUSH_WINDOW_PITCHOVER_REGRESSION`

Do not promote. Targeted seed0 push-window weighting regressed compact seed7 pass and made seed0 fail earlier than iter2 while preserving envelope compliance.

Do not run robot validation. Do not use this candidate as a Phase 2 promotion artifact.

## Next Recommendation

Stop this narrow weighting path. Next iteration should collect live-oracle labels from the iter3 push-window drift for both seeds or change the recovery objective, while preserving the iter2 seed7 pass as an explicit control.
