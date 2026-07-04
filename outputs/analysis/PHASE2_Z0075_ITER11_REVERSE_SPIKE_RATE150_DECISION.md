# Phase 2 z=0.0075 Iter11 Reverse-Oracle Spike Rate150 Decision

status: `HOLD_REVERSE_ORACLE_TRADEOFF`

## Scope

- offline sim/data curation only; no robot, SSH, deploy, grounded replay, runtime behavior changes, or PPO training.

## Candidate

`policy/candidates/phase2_z0075_iter11_reverse_spike_rate150_20260704/candidate.onnx`

- candidate sha256: `5e4055eaaa3adedd16572e5926b25c5c40f05ff148c45fec7afec825d46402b5`
- student npz sha256: `e71be8f774e1fc70069cb6e519ad945f0e79935193a6fa5e7912c6f7fc6e05f3`
- reverse relabel manifest: `outputs/analysis/phase2_z0075_iter11_reverse_oracle_manifest.json` (`6fbfa42d10a44229`, 462 samples)
- merged manifest: `outputs/analysis/phase2_z0075_iter11_reverse_spike_merged_manifest.json` (`176bae6b19d3c4cc`, 53386 samples)

## What Changed

This run kept the Iter10 spike-local merged dataset and added only reverse-mode live-oracle relabels from Iter10 failed seeds `1` and `5`.
The relabel queried the corrected Phase 1 source manifest on the student's own reverse/pitchback states and weighted low-progress/reverse rows more heavily.

## Fit Metrics

| metric | value |
|---|---:|
| MAE | 0.009807 |
| p95 abs error | 0.031528 |
| max abs error | 0.504130 |
| target-rate p95 rad/s | 1.367101 |
| target-rate max rad/s | 2.743571 |
| ONNX max abs error | 0.00000030 |

## Full 8-Seed x=0.08 Intermediate-Push Gate

z=0.0075 rough terrain backlash, fitted corrected bridge, x=0.08, push magnitude `0.075-0.125` every `1.0-1.5s`.

| seed | status | samples | termination | track ratio | p95 excess | max excess | tracking p95 | push success |
|---:|---|---:|---|---:|---:|---:|---:|---:|
| 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 637 | `fall_or_nan` | 0.6874 | 0.0000 | 0.0000 | 0.1920 | 0.9000 |
| 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 340 | `fall_or_nan` | 1.0537 | 0.0000 | 0.0000 | 0.1928 | 0.6667 |
| 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 392 | `fall_or_nan` | 0.8954 | 0.0000 | 0.0556 | 0.1930 | 0.8333 |
| 3 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.3169 | 0.0000 | 0.0000 | 0.1861 | 0.9231 |
| 4 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 335 | `fall_or_nan` | 1.0414 | 0.0000 | 0.0000 | 0.1881 | 0.8000 |
| 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 47 | `fall_or_nan` | -3.6256 | 0.0000 | 0.0000 | 0.2248 | NA |
| 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.3581 | 0.0000 | 0.0000 | 0.1902 | 0.9231 |
| 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 597 | `fall_or_nan` | 0.6827 | 0.0000 | 0.0000 | 0.1917 | 0.8750 |

Distribution summary:

- pass: `2/8`
- falls / terminations: `6/8`
- duration complete: `2/8`
- mean track ratio: `0.1763`
- mean local vx: `0.0141 m/s`
- max p95 corrected-envelope excess: `0.0000 rad/s`
- max instantaneous corrected-envelope excess: `0.0556 rad/s`
- max tracking p95: `0.2248 rad`
- mean push success: `0.8459`

## Decision

`HOLD_REVERSE_ORACLE_TRADEOFF`

Do not promote. Reverse-oracle relabeling improved some late-lunge/excess behavior: seed `3` and seed `6` became passes, and the worst instantaneous velocity excess dropped to `0.0556 rad/s`. However, it regressed prior pass-control seeds `0`, `4`, and `7`, and seed `5` remains an immediate reverse/pitchback failure. The distribution is worse than Iter10 by pass count (`2/8` vs `3/8`), even though it is cleaner on instantaneous envelope excess.

## Next Recommendation

Treat reverse-oracle relabeling as a useful but over-broad correction. The next branch should not add more global reverse weight. Instead, preserve pass-control seeds explicitly while isolating seed `5` as an early-reset/initial-condition failure and handling seeds `0/1/2/4/7` as post-push pitch/base-height stability failures. Do not robot validate this candidate.
