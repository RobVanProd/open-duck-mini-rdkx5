# Phase 2 z=0.0075 Late-Lunge Rate150 Decision

status: `HOLD_LATE_LUNGE_TRADEOFF`

## Scope

- offline sim/data curation only; no robot, SSH, deploy, grounded replay, runtime behavior changes, or PPO training.

## Candidate

`policy/candidates/phase2_z0075_late_lunge_rate150_20260704/candidate.onnx`

- candidate sha256: `84a7dea96b37fb088edbf1e69b31494a68cfca27319c00531b96614811d13f39`
- student npz sha256: `e2109e993868d6db16317e4608d9ba2aedffee7c253ce5c91d37e49388adb0de`
- merged manifest: `outputs/analysis/phase2_z0075_iter9_late_lunge_merged_manifest.json`
- dataset samples: `52765`
- dataset id: `d58e3c29a3503c0d`

## What Changed

This run kept the Iter7 seed-diverse manifest and added late-window same-tick
seed-0 neighbor labels for the five Iter7 forward-lunge seeds: `1`, `2`, `4`,
`6`, and `7`.

Unlike Iter8, the relabels covered only the final `80` ticks before each lunge
termination and used sample weight `1.5`, instead of relabeling whole traces at
weight `3.0`.

## Fit Metrics

| metric | value |
|---|---:|
| MAE | 0.010445 |
| p95 abs error | 0.032991 |
| max abs error | 0.884549 |
| target-rate p95 rad/s | 1.368537 |
| target-rate max rad/s | 2.319002 |
| ONNX max abs error | 0.00000030 |

## Full 8-Seed x=0.08 Intermediate-Push Gate

z=0.0075 rough terrain, fitted corrected bridge, x=0.08, intermediate push
`0.075-0.125`.

| seed | status | samples | termination | track ratio | p95 velocity excess | max velocity excess | max tracking p95 |
|---:|---|---:|---|---:|---:|---:|---:|
| 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 150 | `fall_or_nan` | 1.7842 | 0.0000 | 0.1199 | 0.2049 |
| 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 580 | `fall_or_nan` | 0.7284 | 0.0000 | 1.0405 | 0.1847 |
| 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 154 | `fall_or_nan` | 1.6349 | 0.0000 | 0.0000 | 0.1941 |
| 3 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.3365 | 0.0000 | 0.2400 | 0.1859 |
| 4 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 277 | `fall_or_nan` | 1.1543 | 0.0000 | 0.0537 | 0.1822 |
| 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 46 | `fall_or_nan` | -3.9985 | 0.0000 | 0.0000 | 0.2101 |
| 6 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 425 | `fall_or_nan` | 0.8839 | 0.0000 | 1.5385 | 0.1847 |
| 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.3733 | 0.0000 | 0.0000 | 0.1914 |

Distribution summary:

- pass: `1/8`
- falls / terminations: `6/8`
- duration complete: `2/8`
- mean track ratio: `0.3621`
- mean local vx: `0.0290 m/s`
- max p95 corrected-envelope excess: `0.0000 rad/s`
- max instantaneous corrected-envelope excess: `1.5385 rad/s`

## Decision

`HOLD_LATE_LUNGE_TRADEOFF`

Do not promote. Late-window, lower-weight neighbor stabilization avoided the
complete low-progress collapse seen in Iter8 and recovered seed `7`, but it
broke the previous seed-0 pass and still failed six of eight seeds. It also
introduced large instantaneous corrected-envelope excess on seeds `1`, `3`, and
`6`.

This result narrows the next branch: neighbor stabilization must not be applied
as same-tick trajectory copy, even in late windows, unless the action-rate spike
is separately controlled. The remaining problem is not a lack of forward motion;
it is forward lunge/stability with strict instantaneous envelope preservation.

Do not run robot validation. Do not use this candidate as a Phase 2 promotion
artifact.
