# Phase 2 z=0.0075 Intermediate-Push Live-Oracle Iter1 Rate150 Decision

status: `HOLD_FULL_SEED_DISTRIBUTION_REGRESSED`

## Scope

- Offline sim/data collection, BC fit, and corrected-bridge candidate gates only.
- No robot tests, SSH, deploy, grounded replay, runtime behavior changes, or PPO training were performed.

## Candidate

`policy/candidates/phase2_z0075_intermediate_push_live_oracle_iter1_rate150_20260704/candidate.onnx`

- candidate sha256: `2364d1540b6165474075d5506a3681450757304161add0763ae496f706ee7684`
- student npz sha256: `1bf410bd854baee0ea6ae3efc78cc5a532a4fe45ad5e8d1b505d8c0220aa1e8d`
- source manifest: `outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter1_rate150_run/live_oracle_dagger_aggregate_manifest.json`
- dataset_id: `f772391aca069fa4`
- samples: `45501`

## What Changed

This run replaced global spike smoothing with one live-oracle DAgger iteration on
the held iter0 rate150 student. The point was to add local state coverage around
the current student's own rough-terrain/intermediate-push states instead of
hard-capping load-bearing transition labels.

Fit metrics improved in the intended dimension:

| metric | value |
|---|---:|
| action MAE | 0.011864 |
| action p95 abs error | 0.038300 |
| action max abs error | 0.571110 |
| fit target-rate p95 | 1.304301 rad/s |
| fit target-rate max | 1.832521 rad/s |
| ONNX max abs error | 0.00000021 |

## Compact Transfer Screen

The compact boundary screen passed.

| gate | seeds | result | track ratio mean | vx mean | p95 velocity excess | max velocity excess | tracking p95 |
|---|---:|---|---:|---:|---:|---:|---:|
| x=0.08, z=0.0075, intermediate push | 0,7 | 2/2 pass | 0.3349 | 0.0268 | 0.0000 | 0.0000 | 0.1789 max |
| x=0.0, z=0.0075, intermediate push | 0,1 | 2/2 pass | NA | -0.0005 | 0.0000 | 0.0000 | 0.0448 max |

This is the first checked rate150 successor in this branch that removed the
compact seed-7 instantaneous spike without hard label caps and preserved x=0.0
command semantics on the compact check.

## Full x=0.08 8-Seed Gate

The full seed distribution failed and the candidate is not promotable.

| seed | status | samples | termination | track ratio | p95 velocity excess | max velocity excess | max tracking p95 |
|---:|---|---:|---|---:|---:|---:|---:|
| 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | duration_complete | 0.3278 | 0.0000 | 0.0000 | 0.1757 |
| 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 560 | fall_or_nan | 0.7718 | 0.0000 | 0.0000 | 0.1789 |
| 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 643 | fall_or_nan | 0.5482 | 0.0000 | 1.9168 | 0.1834 |
| 3 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 85 | fall_or_nan | -2.6989 | 0.0000 | 2.3114 | 0.1575 |
| 4 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 478 | fall_or_nan | 0.7113 | 0.0000 | 0.1771 | 0.1692 |
| 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 48 | fall_or_nan | -3.6031 | 1.4589 | 3.2400 | 0.3202 |
| 6 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | duration_complete | 0.2247 | 0.0000 | 0.8566 | 0.1785 |
| 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | duration_complete | 0.3420 | 0.0000 | 0.0000 | 0.1789 |

Distribution summary:

- pass: `2/8`
- falls/terminations: `5/8`
- duration complete: `3/8`
- mean track ratio: `-0.4221`
- mean local vx: `-0.0338 m/s`
- max p95 velocity excess: `1.4589 rad/s`
- max instantaneous velocity excess: `3.2400 rad/s`
- mean push success: `0.7605`

## Decision

`HOLD_FULL_SEED_DISTRIBUTION_REGRESSED`

The live current-state coverage fixed the compact seed-7 spike and preserved
the compact x=0.0 behavior, but it overfit the compact boundary. The full
8-seed gate regressed into broad fall/low-progress behavior.

Do not promote this candidate. Do not run robot validation.

## Next Step

Use this run as a diagnostic split:

1. keep the iter1 live-oracle data as useful local spike coverage,
2. collect full-observation failure traces for seeds 1-5 under the same gate,
3. compare those failure states against the iter0 candidate's passing/near-pass
   states,
4. add recovery data with a stability-preserving trust region rather than
   replacing the compact labels wholesale.

The next candidate must preserve the compact zero-spike behavior while
recovering the broader seed distribution. A compact 0/7 pass is not sufficient
for Phase 2 promotion.
