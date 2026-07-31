# Phase 2 z=0.0075 Neighbor-Stabilized Rate150 Decision

status: `HOLD_NEIGHBOR_STABILIZATION_OVERDAMPED`

## Scope

- offline sim/data curation only; no robot, SSH, deploy, grounded replay, runtime behavior changes, or PPO training.

## Candidate

`policy/candidates/phase2_z0075_neighbor_stabilized_rate150_20260704/candidate.onnx`

- candidate sha256: `f24e91e4c29cd1f7780894050d4d4106ab3a98f7df56d1c2cadfdf23216fe3b9`
- student npz sha256: `3fe670731c7376ce786d7d1425576ecf98e21a67b955c5aacc2ec665ec81295e`
- merged manifest: `outputs/analysis/phase2_z0075_iter8_neighbor_stabilized_merged_manifest.json`
- dataset samples: `54497`
- dataset id: `a437269144ee7496`

## What Changed

This run kept the Iter7 seed-diverse manifest and added same-tick seed-0
neighbor labels for the five Iter7 forward-lunge seeds: `1`, `2`, `4`, `6`,
and `7`.

The neighbor labels used the seed-0 full-observation pass trace as the source
action trajectory, with pitch-chain action deltas capped by a conservative
`1.5 rad/s` target-velocity proxy.

## Fit Metrics

| metric | value |
|---|---:|
| MAE | 0.014710 |
| p95 abs error | 0.048543 |
| max abs error | 0.813995 |
| target-rate p95 rad/s | 1.298335 |
| target-rate max rad/s | 2.441719 |
| ONNX max abs error | 0.00000030 |

## Full 8-Seed x=0.08 Intermediate-Push Gate

z=0.0075 rough terrain, fitted corrected bridge, x=0.08, intermediate push
`0.075-0.125`.

| seed | status | samples | termination | track ratio | p95 velocity excess | max velocity excess | max tracking p95 |
|---:|---|---:|---|---:|---:|---:|---:|
| 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.2214 | 0.0000 | 0.0000 | 0.1686 |
| 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 315 | `fall_or_nan` | 1.0235 | 0.0000 | 0.9262 | 0.1645 |
| 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 229 | `fall_or_nan` | 1.1787 | 0.0000 | 0.3896 | 0.1669 |
| 3 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 708 | `fall_or_nan` | 0.4640 | 0.0000 | 0.8892 | 0.1675 |
| 4 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 638 | `fall_or_nan` | -0.2001 | 0.0000 | 0.0000 | 0.1525 |
| 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 46 | `fall_or_nan` | -3.8220 | 0.0000 | 0.1800 | 0.2275 |
| 6 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 300 | `fall_or_nan` | -0.5482 | 0.0000 | 0.1622 | 0.1720 |
| 7 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.1635 | 0.0000 | 0.0000 | 0.1596 |

Distribution summary:

- pass: `0/8`
- falls / terminations: `6/8`
- duration complete: `2/8`
- mean track ratio: `-0.1899`
- mean local vx: `-0.0152 m/s`
- max p95 corrected-envelope excess: `0.0000 rad/s`
- max instantaneous corrected-envelope excess: `0.9262 rad/s`

## Decision

`HOLD_NEIGHBOR_STABILIZATION_OVERDAMPED`

Do not promote. Same-tick seed-0 neighbor labels over-corrected the Iter7
forward-lunge failure mode. Seeds `0` and `7` now survive but fail low-progress,
while the rest of the distribution still falls. The run also introduced larger
instantaneous corrected-envelope excess on some seeds despite p95 compliance.

This result is useful as a falsifier: copying a passing seed's action trajectory
into lunge states is too strong and collapses forward motion. The next recovery
should use either a lower-weight / later-window version of neighbor
stabilization or a direct lunge-window action attenuation that does not overwrite
early gait structure.

Do not run robot validation. Do not use this candidate as a Phase 2 promotion
artifact.
