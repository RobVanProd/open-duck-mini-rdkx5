# Phase 2 z=0.0075 Weight2 Control Rate150 Decision

status: `HOLD_FULL_SEED_DISTRIBUTION_REGRESSED`

## Scope

- offline sim/data curation only; no robot, SSH, deploy, grounded replay, runtime behavior changes, or PPO training.

## Candidate

`policy/candidates/phase2_z0075_weight2_control_rate150_20260704/candidate.onnx`

- candidate sha256: `a05c1629db07db42c54197f151d97b114ca1995862c403f0ddcd2d8a01c029a9`
- student npz sha256: `a243c38d17d5b55972cdf4a96991d280b973bad65ad19f732d289f76d9e2385c`
- manifest: `outputs/analysis/phase2_z0075_iter6_weight2_control_manifest.json`
- dataset samples: `50253`
- dataset id: `084d8e7fd150d37c`

## What Changed

This run returned to the iter2 recovery aggregate, added the seed-0 late
push-window relabel with lower weight `2.0` instead of `4.0`, and kept the
weighted iter2 seed-7 pass-control trace.

The goal was to test whether the prior seed0/seed7 tradeoff came from
overweighting the seed-0 window.

## Fit Metrics

| metric | value |
|---|---:|
| MAE | 0.009053 |
| p95 abs error | 0.030133 |
| max abs error | 0.513354 |
| target-rate p95 rad/s | 1.366491 |
| target-rate max rad/s | 2.448786 |
| ONNX max abs error | 0.00000024 |

## Compact Boundary Screen

z=0.0075 rough terrain, x=0.08, intermediate push, seeds 0 and 7.

| seed | status | samples | termination | track ratio | p95 velocity excess | max velocity excess | max tracking p95 | push success |
|---:|---|---:|---|---:|---:|---:|---:|---:|
| 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.3257 | 0.0000 | 0.0000 | 0.1869 | 0.9167 |
| 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.3823 | 0.0000 | 0.0000 | 0.1904 | 0.9000 |

This is a real improvement over iter3/iter4/iter5 on the compact boundary:
the lower seed-0 weight recovered seed0 while preserving seed7.

## Full 8-Seed x=0.08 Intermediate-Push Gate

The full seed distribution failed and the candidate is not promotable.

| seed | status | samples | termination | track ratio | p95 velocity excess | max velocity excess | max tracking p95 |
|---:|---|---:|---|---:|---:|---:|---:|
| 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.3257 | 0.0000 | 0.0000 | 0.1869 |
| 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 494 | `fall_or_nan` | -0.1076 | 0.0000 | 0.0000 | 0.1811 |
| 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 157 | `fall_or_nan` | 1.6957 | 0.0000 | 0.0000 | 0.2079 |
| 3 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 450 | `fall_or_nan` | -0.2733 | 0.0000 | 0.3926 | 0.1759 |
| 4 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 724 | `fall_or_nan` | 0.6728 | 0.0000 | 0.0000 | 0.1886 |
| 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 47 | `fall_or_nan` | -3.8964 | 0.0000 | 0.0000 | 0.2332 |
| 6 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 246 | `fall_or_nan` | -0.6486 | 0.0000 | 0.0000 | 0.1786 |
| 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.3823 | 0.0000 | 0.0000 | 0.1904 |

Distribution summary:

- pass: `2/8`
- falls / terminations: `6/8`
- duration complete: `2/8`
- mean track ratio: `-0.2312`
- mean local vx: `-0.0185 m/s`
- max p95 corrected-envelope excess: `0.0000 rad/s`
- max instantaneous corrected-envelope excess: `0.3926 rad/s`

## Decision

`HOLD_FULL_SEED_DISTRIBUTION_REGRESSED`

Do not promote. Lower seed-0 weighting solved the compact seed0/seed7 boundary,
but it did not generalize across seeds. The full distribution regressed into
mixed reverse, lunge, and fall modes while preserving p95 envelope compliance.

The result is still useful: the compact seed0/seed7 tradeoff is tunable, and
weight `2.0` is less destructive than weight `4.0` or zero-action anti-lunge
tail weighting. But compact success is not enough for Phase 2 promotion.

Do not run robot validation. Do not use this candidate as a Phase 2 promotion
artifact.

## Next Recommendation

Stop optimizing only the compact seed0/seed7 pair. The next offline step should
collect traced failure states for the full-distribution failures, especially
seeds 1, 2, 5, and 6, then add live-oracle recovery labels with a seed-diverse
trust region. A candidate must preserve the compact seed0/seed7 pass while
improving the full 8-seed distribution; another compact-only pass is not a new
result.
