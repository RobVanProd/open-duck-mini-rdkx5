# Phase 2 z=0.0075 Anti-Lunge Zero50 Rate150 Decision

status: `HOLD_ANTILUNGE_REGRESSED_SEED7`

## Scope

- offline sim/data curation only; no robot, SSH, deploy, grounded replay, runtime behavior changes, or PPO training.

## Candidate

`policy/candidates/phase2_z0075_antilunge_zero50_rate150_20260704/candidate.onnx`

- candidate sha256: `abced43cfaaa2a05f2b6576819dae0950b6a72f946d336a7f541ad0ab8c49b7c`
- student npz sha256: `ff97e0b81f50628327bfad0627636e3eea24caedcee42dc5cdba2a7bd589a492`
- manifest: `outputs/analysis/phase2_z0075_iter5_antilunge_zero50_manifest.json`
- dataset samples: `50273`
- dataset id: `45f8a46ea0430e64`

## What Changed

This run kept the iter4 control-preserving recovery manifest, added a zero-action
teacher relabel of the iter4 seed-0 lunge trace, and weighted the immediate
pre-fall anti-lunge tail window.

The goal was to damp seed-0 forward lunge without losing the seed-7 pass-control
behavior restored by iter4.

## Fit Metrics

| metric | value |
|---|---:|
| MAE | 0.00915827 |
| p95 abs error | 0.02993791 |
| max abs error | 0.37934116 |
| target-rate p95 rad/s | 1.36300147 |
| target-rate max rad/s | 2.34726024 |
| ONNX max abs error | 0.00000030 |
| sample weight max | 8.00000000 |

## Compact Boundary Screen

z=0.0075 rough terrain, x=0.08, intermediate push, seeds 0 and 7.

| seed | status | samples | termination | track ratio | p95 velocity excess | max velocity excess | max tracking p95 | push success |
|---:|---|---:|---|---:|---:|---:|---:|---:|
| 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 205 | `fall_or_nan` | 1.4794 | 0.0000 | 0.0000 | 0.2001 | 0.6667 |
| 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 621 | `fall_or_nan` | 0.6987 | 0.0000 | 2.7400 | 0.1881 | 0.8750 |

Distribution summary:

- falls / terminations: `2/2`
- duration complete: `0/2`
- mean track ratio: `1.0891`
- mean local vx: `0.0871 m/s`
- max p95 corrected-envelope excess: `0.0000 rad/s`
- max instantaneous corrected-envelope excess: `2.7400 rad/s`
- mean push success: `0.7708`

## Decision

`HOLD_ANTILUNGE_REGRESSED_SEED7`

Do not promote. The anti-lunge zero50 labels delayed seed-0 failure relative to
the iter4 early-lunge result, but seed 0 still fell at sample 205 with a high
track ratio. More importantly, seed 7 regressed from the iter4 full-duration pass
to a sample-621 fall.

This confirms that direct zero-action anti-lunge tail weighting is too blunt for
the intermediate-push boundary. It reduces one lunge mode without preserving the
existing seed-7 control behavior.

Do not run robot validation. Do not use this candidate as a Phase 2 promotion
artifact.

## Next Recommendation

Return to the iter2 boundary as the best compact starting point: seed 7 passed,
seed 0 reached sample 689, and p95 envelope compliance was clean. The next
offline refinement should target seed-0 late push-window pitch/base-height
recovery without broad zero-action damping and without sacrificing the seed-7
pass-control trace.
