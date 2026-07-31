# Phase 2 z=0.0075 Spike-Local Rate150 Decision

status: `HOLD_SPIKE_LOCAL_RECOVERY_PARTIAL`

## Scope

- offline sim/data curation only; no robot, SSH, deploy, grounded replay, runtime behavior changes, or PPO training.

## Candidate

`policy/candidates/phase2_z0075_spike_local_rate150_20260704/candidate.onnx`

- candidate sha256: `3874e11e4a132ac90e14a0600071e41b5f147ef1a1486e06934a69368ecca70f`
- student npz sha256: `fddc8c75a13ee444ec55be66c82d20a52a08e714e2c09d56d60c69a29de15831`
- curation dataset: `outputs/analysis/phase2_z0075_iter10_spike_local_recovery_windows.json` (`36ffcea123bef3dd`, 559 samples)
- merged manifest: `outputs/analysis/phase2_z0075_iter10_spike_local_merged_manifest.json` (`0c16a7273cf0fbdc`, 52924 samples)

## What Changed

This run kept the Iter7 seed-diverse base and added only spike-local recovery snippets from Iter9 failed seeds.
The snippets preserve each failed trace's own observations/actions, smooth selected pitch-chain action deltas, and avoid same-tick neighbor trajectory copy.

## Fit Metrics

| metric | value |
|---|---:|
| MAE | 0.009697 |
| p95 abs error | 0.031047 |
| max abs error | 0.417011 |
| target-rate p95 rad/s | 1.364341 |
| target-rate max rad/s | 3.030199 |
| ONNX max abs error | 0.00000027 |

## Full 8-Seed x=0.08 Intermediate-Push Gate

z=0.0075 rough terrain backlash, fitted corrected bridge, x=0.08, push magnitude `0.075-0.125` every `1.0-1.5s`.

| seed | status | samples | termination | track ratio | p95 excess | max excess | tracking p95 | push success |
|---:|---|---:|---|---:|---:|---:|---:|---:|
| 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `None` | 0.3521 | 0.0000 | 0.0000 | 0.1824 | 0.9167 |
| 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 419 | `None` | -0.1401 | 0.0000 | 0.0000 | 0.1803 | 0.8571 |
| 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 714 | `None` | 0.6560 | 0.0000 | 0.2900 | 0.1869 | 0.9167 |
| 3 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 527 | `None` | 0.6962 | 0.0000 | 0.0000 | 0.1833 | 0.8889 |
| 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | `None` | 0.3726 | 0.0000 | 0.0000 | 0.1816 | 0.9167 |
| 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 45 | `None` | -3.7453 | 0.0000 | 0.0000 | 0.2203 | NA |
| 6 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 611 | `None` | 0.6569 | 0.0000 | 0.1897 | 0.1804 | 0.9000 |
| 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `None` | 0.3174 | 0.0000 | 0.0000 | 0.1832 | 0.9000 |

Distribution summary:

- pass: `3/8`
- falls / terminations: `5/8`
- duration complete: `3/8`
- mean track ratio: `-0.1043`
- mean local vx: `-0.0083 m/s`
- max p95 corrected-envelope excess: `0.0000 rad/s`
- max instantaneous corrected-envelope excess: `0.2900 rad/s`
- max tracking p95: `0.2203 rad`
- mean push success: `0.8994`

## Decision

`HOLD_SPIKE_LOCAL_RECOVERY_PARTIAL`

Do not promote. Spike-local smoothing recovered seed0 and preserved seed7 while adding seed4, and it reduced Iter9 instantaneous envelope excess, but the full distribution still fails 5/8 seeds and mean track ratio remains negative because seed5 reverses hard.

Compared with Iter9, this recovered seed `0`, preserved seed `7`, and added seed `4`, while reducing the worst instantaneous velocity excess from `1.5385` to `0.2900 rad/s`. It remains a hold because five seeds still fail and seed `5` remains a hard early reverse case.

## Next Recommendation

Keep the spike-local curation result as evidence that local target-rate spikes are controllable. The next branch should separately handle seed5 early reverse and seeds2/3/6 late pitch/base-height collapse; do not return to same-tick neighbor trajectory copy or global damping.

No robot validation. Do not use this candidate as a Phase 2 promotion artifact.
