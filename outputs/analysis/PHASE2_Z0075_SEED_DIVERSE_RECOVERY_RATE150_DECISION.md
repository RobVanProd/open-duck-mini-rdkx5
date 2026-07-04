# Phase 2 z=0.0075 Seed-Diverse Recovery Rate150 Decision

status: `HOLD_FULL_SEED_DISTRIBUTION_REGRESSED`

## Scope

- offline sim/data curation only; no robot, SSH, deploy, grounded replay, runtime behavior changes, or PPO training.

## Candidate

`policy/candidates/phase2_z0075_seed_diverse_recovery_rate150_20260704/candidate.onnx`

- candidate sha256: `ed29e5cc6aca5650673843af508c0b4846f360bb56a35efe1d4a52a32baef666`
- student npz sha256: `f938d76bb974553d7400dd042b9ff31a44f301858f847381802a41e0a1c0500c`
- merged manifest: `outputs/analysis/phase2_z0075_iter7_seed_diverse_recovery_merged_manifest.json`
- dataset samples: `52365`
- dataset id: `5bf5758380bec2e8`

## What Changed

This run kept the Iter6 weight2-control manifest and added live-oracle
source-vx relabels from the failed full-distribution seeds `1-6`.

The goal was to stop optimizing only the compact seed0/seed7 boundary and test
whether seed-diverse recovery labels improve the full `z=0.0075`,
intermediate-push seed distribution.

## Fit Metrics

| metric | value |
|---|---:|
| MAE | 0.009287 |
| p95 abs error | 0.030996 |
| max abs error | 0.411229 |
| target-rate p95 rad/s | 1.363054 |
| target-rate max rad/s | 2.742286 |
| ONNX max abs error | 0.00000025 |

## Full 8-Seed x=0.08 Intermediate-Push Gate

z=0.0075 rough terrain, fitted corrected bridge, x=0.08, intermediate push
`0.075-0.125`.

| seed | status | samples | termination | track ratio | p95 velocity excess | max velocity excess | max tracking p95 |
|---:|---|---:|---|---:|---:|---:|---:|
| 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.3720 | 0.0000 | 0.0000 | 0.1852 |
| 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 513 | `fall_or_nan` | 0.8139 | 0.0000 | 0.0000 | 0.1860 |
| 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 155 | `fall_or_nan` | 1.7105 | 0.0000 | 0.0000 | 0.2035 |
| 3 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 129 | `fall_or_nan` | -1.8271 | 0.0000 | 0.2339 | 0.1757 |
| 4 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 422 | `fall_or_nan` | 0.7771 | 0.0000 | 0.0000 | 0.1827 |
| 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 47 | `fall_or_nan` | -4.0006 | 0.0000 | 0.0000 | 0.2190 |
| 6 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 430 | `fall_or_nan` | 0.8593 | 0.0000 | 0.0000 | 0.1856 |
| 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 617 | `fall_or_nan` | 0.6758 | 0.0000 | 0.0000 | 0.1851 |

Distribution summary:

- pass: `1/8`
- falls / terminations: `7/8`
- duration complete: `1/8`
- mean track ratio: `-0.0774`
- mean local vx: `-0.0062 m/s`
- max p95 corrected-envelope excess: `0.0000 rad/s`
- max instantaneous corrected-envelope excess: `0.2339 rad/s`

## Comparison Against Iter6

Iter6 passed seeds `0` and `7` and failed the other six seeds. Iter7 kept seed
`0`, lost seed `7`, and still failed seeds `1-6`.

Several failed seeds now move forward before falling (`1`, `4`, `6`, and `7`),
which means the seed-diverse relabels shifted some reverse failures toward
forward attempts. That shift is not enough for promotion because the candidate
still falls on seven seeds and seed `2` remains a fast forward lunge.

## Decision

`HOLD_FULL_SEED_DISTRIBUTION_REGRESSED`

Do not promote. Seed-diverse relabeling is directionally informative but not
sufficient. The new data improved some failed-seed motion signatures while
regressing the full pass count from `2/8` to `1/8` and breaking the previous
seed-7 pass.

Do not run robot validation. Do not use this candidate as a Phase 2 promotion
artifact.

## Next Recommendation

Do not keep adding broad relabel data alone. The next offline step should trace
the Iter7 failures and classify whether the remaining falls are now mostly
forward lunge / pitch-over, reverse pitch-back, or envelope excess. If the
distribution has shifted toward forward lunges, the next dataset should include
failure-mode-specific correction while preserving the Iter6 seed7 pass-control
behavior; a single global sample-weight increase is not justified.
