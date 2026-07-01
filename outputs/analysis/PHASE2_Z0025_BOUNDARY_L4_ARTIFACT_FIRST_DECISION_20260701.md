# Phase 2 z=0.0025 Boundary L4 Artifact-First Decision

status: `HOLD_Z0025_BOUNDARY_NOT_PROMOTED`

## Executive Summary

The artifact-first Colab L4 workflow succeeded. It trained the z=0.0025 boundary recipe,
downloaded the artifact bundle, and recovered the selected ONNX before running the slow
seed gates locally.

The selected candidate is stable and preserves x=0.0 command semantics, but it is not a
Phase 2 promotion:

- z=0.0025, x=0.0: `PASS` 8/8 seeds, no falls, mean vx `0.0006 m/s`
- z=0.0025, x=0.08: `HOLD` 4/8 seeds pass, no falls, mean track ratio `0.2553`
- The x=0.08 hold is not falling. It is a mixed progress/envelope-excursion hold:
  - seeds 3 and 6: low forward progress
  - seeds 0 and 4: target-velocity max excursion

Robot validation remains blocked.

## Colab Artifact

- session: `open-duck-l4-z0025-artifact`
- workflow: `phase2-z0025-boundary`
- command style: `--exec-remote --phase2-skip-post-training-gates`
- artifact:
  `outputs/analysis/colab_cli/open-duck-l4-z0025-artifact-phase2-z0025-boundary-20260701T090250Z/open_duck_colab_cli_phase2-z0025-boundary_20260701T090317Z_artifacts.tar.gz`
- artifact sha256:
  `c291b943630bfa4b73ba7b26e97887591fe8882da2d9bf9985f6db40bc23e11a`
- artifact size: `4.4M`
- pinned stack:
  - JAX/JAXLIB `0.7.2`
  - Brax `0.14.2`
  - MuJoCo/MJX `3.9.0`
  - Playground `0.0.5`

## Selected Checkpoint

- selection status: `HOLD_PARTIAL_CANDIDATE_CHECKPOINT`
- selection reason: `best_available_but_not_promoted`
- selected ONNX:
  `outputs/analysis/colab_cli/open-duck-l4-z0025-artifact-phase2-z0025-boundary-20260701T090250Z/extracted/open_duck_colab_cli_phase2-z0025-boundary_20260701T090317Z/open_duck_training_phase2_z0025_boundary_cli/smoke_20260701T090648Z_gpu/2026_07_01_092118_122880.onnx`
- selected ONNX sha256:
  `b65ee4675bd6c7df97e4a7a1ecfcec48c7afee9f67c203464d2d91fb5eabac90`

Compact 1-second checkpoint sweep picked this checkpoint because it was the best available,
but it did not promote:

- x=0.08 compact track ratio: `0.2350`
- x=0.08 compact mean vx: `0.0188 m/s`
- compact max tracking p95: `0.2124 rad`
- compact max sent target p95: `1.3934 rad/s`

## Full Seed Gates

### z=0.0025 x=0.08

Result: `HOLD_Z0025_BOUNDARY_NOT_PROMOTED`

| metric | value |
|---|---:|
| seeds | 8 |
| falls | 0 |
| duration complete | 8 |
| pass statuses | 4 |
| mean track ratio | 0.2553 |
| mean vx | 0.0204 m/s |
| body pitch p95 mean | 0.1199 rad |
| base height min mean | 0.1526 m |
| max pitch velocity p95 mean | 1.6346 rad/s |
| p95 velocity excess mean | 0.0000 rad/s |
| max instantaneous velocity excess mean | 0.0954 rad/s |
| max tracking p95 mean | 0.1890 rad |
| single support mean | 14.6833% |
| double support mean | 85.2667% |

Per-seed statuses:

| seed | status | vx | track ratio | max vel excess | max tracking p95 |
|---:|---|---:|---:|---:|---:|
| 0 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 0.0211 | 0.2641 | 0.5350 | 0.1919 |
| 1 | `PASS_CANDIDATE_SIM_GATE` | 0.0215 | 0.2692 | 0.0000 | 0.1890 |
| 2 | `PASS_CANDIDATE_SIM_GATE` | 0.0218 | 0.2723 | 0.0000 | 0.1891 |
| 3 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.0169 | 0.2110 | 0.0000 | 0.1867 |
| 4 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 0.0215 | 0.2691 | 0.2280 | 0.1875 |
| 5 | `PASS_CANDIDATE_SIM_GATE` | 0.0203 | 0.2535 | 0.0000 | 0.1932 |
| 6 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.0197 | 0.2465 | 0.0000 | 0.1863 |
| 7 | `PASS_CANDIDATE_SIM_GATE` | 0.0205 | 0.2565 | 0.0000 | 0.1881 |

### z=0.0025 x=0.0

Result: `PASS_COMMAND_SEMANTICS`

| metric | value |
|---|---:|
| seeds | 8 |
| falls | 0 |
| duration complete | 8 |
| pass statuses | 8 |
| mean vx | 0.0006 m/s |
| body pitch p95 mean | 0.0169 rad |
| base height min mean | 0.1526 m |
| max pitch velocity p95 mean | 0.3426 rad/s |
| p95 velocity excess mean | 0.0000 rad/s |
| max tracking p95 mean | 0.0633 rad |

## Interpretation

This candidate is a useful near-boundary diagnostic, not a deployment candidate.

The key positive result is that the gait remains stable for the full 15 seconds on the
z=0.0025 terrain with no falls, and x=0.0 remains quiet. The failure is narrower:
forward motion at x=0.08 is too close to the acceptance boundary, with two low-progress
seeds and two seeds showing instantaneous target-velocity excursions.

The next training change should not broaden randomization. It should preserve the stable
x=0.0 and no-fall behavior while specifically improving z=0.0025 x=0.08 seed consistency:

- reduce max instantaneous pitch-chain target-velocity excursions on seeds 0 and 4
- increase forward progress on seeds 3 and 6
- keep p95 velocity excess at zero and tracking p95 near or below `0.19 rad`

No robot validation is authorized from this result.
