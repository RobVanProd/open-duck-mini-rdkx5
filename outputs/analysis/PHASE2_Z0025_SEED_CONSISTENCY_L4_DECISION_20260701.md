# Phase 2 z=0.0025 Seed-Consistency L4 Decision

status: `HOLD_SEED_CONSISTENCY_PROGRESS_REGRESSION`

## Executive Summary

The z=0.0025 seed-consistency recipe trained successfully on Colab L4 and downloaded its
artifact. The compact checkpoint sweep did not promote any checkpoint.

The intended fix removed the visible target-velocity failure mode in the compact sweep, but
it also reduced x=0.08 forward progress. This triggers the pre-registered falsifier from
`PHASE2_Z0025_SEED_CONSISTENCY_NEXT_RECIPE.md`: do not keep tuning scalar reward weights.

No robot validation is authorized.

## Colab Artifact

- session: `open-duck-l4-z0025-seed-consistency`
- workflow: `phase2-z0025-boundary`
- artifact:
  `outputs/analysis/colab_cli/open-duck-l4-z0025-seed-consistency-phase2-z0025-boundary-20260701T105518Z/open_duck_colab_cli_phase2-z0025-boundary_20260701T105545Z_artifacts.tar.gz`
- artifact sha256:
  `6f060c411f922fd6210bb5cd90f592fc4000b1b055a954120ab0d68210dc773e`
- pinned stack:
  - JAX/JAXLIB `0.7.2`
  - Brax `0.14.2`
  - MuJoCo/MJX `3.9.0`
  - Playground `0.0.5`

## Selected Checkpoint

- selection status: `HOLD_PARTIAL_CANDIDATE_CHECKPOINT`
- selection reason: `best_available_but_not_promoted`
- selected ONNX:
  `outputs/analysis/colab_cli/open-duck-l4-z0025-seed-consistency-phase2-z0025-boundary-20260701T105518Z/extracted/open_duck_colab_cli_phase2-z0025-boundary_20260701T105545Z/open_duck_training_phase2_z0025_boundary_cli/smoke_20260701T105915Z_gpu/2026_07_01_111402_122880.onnx`
- selected ONNX sha256:
  `621b54b520898402828cb62c23d976bf822c3f783f794f4d5330546551c8430b`

## Compact Sweep Result

| checkpoint | x=0.0 status | x=0.08 status | x=0.08 track ratio | x=0.08 mean vx | max sent vel p95 | max tracking p95 |
|---|---|---|---:|---:|---:|---:|
| `40960` | `PASS_CANDIDATE_SIM_GATE` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.1571 | 0.0126 | 1.4134 | 0.2110 |
| `81920` | `PASS_CANDIDATE_SIM_GATE` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.1602 | 0.0128 | 1.4138 | 0.2117 |
| `122880` | `PASS_CANDIDATE_SIM_GATE` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.1732 | 0.0139 | 1.4271 | 0.2147 |

## Comparison To Prior z=0.0025 Boundary Run

Prior artifact-first boundary selected checkpoint:

- compact x=0.08 track ratio: `0.2350`
- compact x=0.08 mean vx: `0.0188 m/s`
- compact max sent vel p95: `1.3934 rad/s`
- full z=0.0025 x=0.08: 0 falls, duration complete 8/8, 4/8 pass statuses

Seed-consistency recipe:

- compact x=0.08 track ratio: `0.1732`
- compact x=0.08 mean vx: `0.0139 m/s`
- compact max sent vel p95: `1.4271 rad/s`
- all compact x=0.08 checkpoints hold by low forward progress

The scalar swing-rate-limit/progress-pressure recipe made the compact policy slower, not
more promotable. Full 15-second gates were not run because the compact sweep already
failed the promotion screen by a larger margin than the prior candidate.

## Decision

Stop scalar reward tuning for this z=0.0025 boundary failure.

The next branch should target the failing seed distribution through data/teacher correction
instead of global penalties:

- preserve the prior boundary candidate's stable 15-second/no-fall behavior
- inspect seed 0/4 max-excess joints directly rather than penalizing all swing pitch-chain
  joints globally
- inspect seed 3/6 low-progress traces and add targeted teacher data or seed-conditioned
  correction if the traces share a local failure mode
- only return to PPO after the correction target is local and measured

Robot validation remains blocked.
