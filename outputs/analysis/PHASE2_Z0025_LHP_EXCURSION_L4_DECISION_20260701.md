# Phase 2 z=0.0025 Left-Hip-Pitch Excursion L4 Decision

status: `HOLD_LHP_EXCURSION_PROGRESS_REGRESSION`

## Executive Summary

The targeted `left_hip_pitch` correction trained successfully on Colab L4 and the artifact
was recovered. The run is not promoted.

The intended one-joint rate correction did not preserve forward progress. All exported
checkpoints pass the compact x=0.0 screen, but all hold at x=0.08 by low forward progress.
This repeats the key lesson from the broader seed-consistency run: reward-side rate
penalties, even when narrowed to the measured driver joint, are still too blunt for the
z=0.0025 boundary issue.

No full 15-second multi-seed gates were run because the compact x=0.08 screen already
regressed below the prior boundary candidate.

Robot validation remains blocked.

## Colab Artifact

- session: `open-duck-l4-z0025-lhp-excursion`
- workflow: `phase2-z0025-boundary`
- remote artifact:
  `/content/open_duck_colab_cli_phase2-z0025-boundary_20260701T120208Z_artifacts.tar.gz`
- local artifact:
  `outputs/analysis/colab_cli/open-duck-l4-z0025-lhp-excursion-phase2-z0025-boundary-20260701T120141Z/manual_download/open_duck_colab_cli_phase2-z0025-boundary_20260701T120208Z_artifacts.tar.gz`
- local artifact sha256:
  `947cf48909212d717a2ad462342165de961368fbd92bf488bc085eb8dd0048b4`
- training return code: `0`
- training elapsed: `946.82432326 s`
- pinned stack:
  - JAX/JAXLIB `0.7.2`
  - Brax `0.14.2`
  - MuJoCo/MJX `3.9.0`
  - Playground `0.0.5`

The Colab session was stopped after the artifact was manually downloaded. The wrapper was
interrupted only after the artifact was local; the remote CPU checkpoint sweep was not used.

## Recipe

The run used the targeted recipe from:

- `outputs/analysis/PHASE2_Z0025_LEFT_HIP_PITCH_EXCURSION_NEXT_RECIPE.md`

Key override:

```text
--phase2-forward-swing-target-rate-limit-scale -0.0015
--phase2-forward-swing-target-rate-limit-joint-indices 2
--phase2-forward-swing-target-rate-limit-values 2.50
--phase2-forward-swing-target-rate-limit-huber-delta 0.02
--phase2-forward-progress-scale 4.1
--phase2-command-progress-scale 3.15
--phase2-command-progress-shortfall-scale -8.25
--phase2-command-progress-required-ratio 0.50
```

## Exports

| step | ONNX sha256 |
|---:|---|
| 40960 | `67c6e0526bbebaa448fa7538bc783f8d81e3039a26a3e17068f9914b804a7b9f` |
| 81920 | `de23ab2433800a008cd25eb9ba1641ffdb7d90a86b2628e146925ded18dda489` |
| 122880 | `827b4832672e7b669365305538bfea47fe3aa3bd5061a1b42c0c91d93ecd09f5` |

Reward increased through training (`36.55 -> 46.70`), but the compact candidate gate did
not improve. This is another case where reward went up while deployability went down.

## Local Compact Checkpoint Sweep

Sweep output:

- `outputs/analysis/phase2_z0025_lhp_excursion_l4_checkpoint_sweep_local/CANDIDATE_CHECKPOINT_SWEEP.md`
- `outputs/analysis/phase2_z0025_lhp_excursion_l4_checkpoint_sweep_local/candidate_checkpoint_sweep.json`

| checkpoint | x=0.0 status | x=0.08 status | x=0.08 track ratio | x=0.08 mean vx | max sent vel p95 | max tracking p95 |
|---|---|---|---:|---:|---:|---:|
| `40960` | `PASS_CANDIDATE_SIM_GATE` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.1611 | 0.0129 | 1.4187 | 0.2140 |
| `81920` | `PASS_CANDIDATE_SIM_GATE` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.1638 | 0.0131 | 1.4106 | 0.2127 |
| `122880` | `PASS_CANDIDATE_SIM_GATE` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.1525 | 0.0122 | 1.4141 | 0.2122 |

Best compact checkpoint: `81920`.

Prior z=0.0025 boundary compact reference:

- x=0.08 track ratio: `0.2350`
- x=0.08 mean vx: `0.0188 m/s`

Targeted LHP run best compact result:

- x=0.08 track ratio: `0.1638`
- x=0.08 mean vx: `0.0131 m/s`

This is a clear progress regression.

## Decision

Stop reward-side target-rate penalty tuning for this z=0.0025 boundary failure.

Both tested variants regressed forward progress:

1. all-six-pitch-chain swing-rate penalty
2. `left_hip_pitch`-only swing-rate penalty

The next branch should use a data/teacher correction or gate-aware relabeling approach for
the four failing seeds from the prior boundary candidate:

- seeds `0` and `4`: remove local `left_hip_pitch` instantaneous excursions without
  changing the rest of the gait.
- seeds `3` and `6`: add forward-progress support without adding a scalar penalty that
  slows all seeds.

Do not promote any checkpoint from this run.
