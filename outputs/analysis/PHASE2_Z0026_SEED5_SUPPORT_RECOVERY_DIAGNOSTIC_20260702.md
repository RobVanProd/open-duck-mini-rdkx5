# Phase 2 z0.0026 Seed-5 Support-Recovery Diagnostic

status: `HOLD_SUPPORT_RECIPE_REVERSES`

## Purpose

The preserved teacher-continuity 81920 checkpoint is the current best z=0.0026 terrain parent:

- x=0.08 full gate: `7/8` duration complete.
- seed 5 is the lone fall/reverse collapse.
- seed 5 trace shows support/contact collapse, not corrected-envelope velocity excess.

This diagnostic tested whether the stronger `phase2-z005-support` support-stability recipe, run at z=0.0026 and warm-started from the 81920 checkpoint, could remove seed 5 without damaging the gait.

No robot, SSH, deploy, or grounded replay was performed.

## Tooling Fix

The first package-only dry run exposed a packaging bug: `--phase2-restore-checkpoint-path` was present in argv, but the restore checkpoint was not included in the required package path list and would have been excluded by the tar filter.

Fix committed in `tools/run_colab_cli_cuda_workflow.py`:

- explicit Phase 2 restore checkpoint overrides are validated as required package inputs.
- candidate restore checkpoints and behavior-prior paths are handled the same way.
- `outputs/analysis/phase2_restore_checkpoints/` is allowed by the Colab package tar filter.
- the preserved 81920 checkpoint is now available at:

`outputs/analysis/phase2_restore_checkpoints/phase2_z0026_teacher_continuity_81920`

## A100 Runs

### 64-env bounded run

Command intent:

- workflow: `phase2-z005-support`
- restore checkpoint: `phase2_z0026_teacher_continuity_81920`
- terrain z-scale: `0.0026`
- timesteps: `40960`
- artifact checkpoint mode: `all`
- post-training gates skipped for artifact recovery

Result:

`HOLD_REMOTE_NO_SENTINEL`

The Colab job reached environment setup and `RUN_PLANNED`, then the detached process disappeared without an exit sentinel or checkpoint. Remote stdout/stderr were recovered. No Python traceback was present.

### 8-env foreground diagnostic

Command intent:

- same restore checkpoint and recipe family
- timesteps: `4096`
- PPO envs: `8`
- PPO evals: `1`
- batch size: `128`
- foreground remote run for better failure visibility

Result:

- remote training completed enough to export:
  `2026_07_02_011119_10240.onnx`
- manual artifact archive recovered:
  `outputs/analysis/colab_cli/open-duck-a100-phase2-seed5-support-phase2-z005-support-20260702T010157Z/manual_download/phase2_z005_support_diag8_manual_artifacts.tar.gz`

## Local Compact Gate Evidence

The diagnostic ONNX was screened locally on CPU against the corrected fitted bridge, `rough_terrain_backlash`, z-scale `0.0026`.

### x=0.08 seed 5, 1 second

| metric | value |
|---|---:|
| status | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` |
| samples | 50 |
| termination | `duration_complete` |
| mean local vx | `-0.0653 m/s` |
| track ratio | `-0.8163` |
| body pitch p95 | `0.0498 rad` |
| base height min | `0.1462 m` |
| max pitch velocity p95 | `1.8673 rad/s` |
| p95/max velocity excess | `0.0000 / 0.0000` |
| max tracking p95 | `0.2410 rad` |
| min swing peak | `0.0134 m` |
| min swing segments | `1` |
| min rel-x range p95 | `0.0036 m` |
| single support | `6.0%` |
| double support | `90.0%` |

The tiny support run removed the immediate fall in the short seed-5 screen, but it did so by producing stable backward / low-progress double-support behavior. It did not recover forward walking.

Seeds 0 and 1 of the interrupted 8-seed compact x=0.08 screen both held on tracking before the screen was stopped, so there is no evidence this diagnostic ONNX is a better parent.

## Decision

Do not promote the `phase2-z005-support` recovery direction as-is.

The next recipe should target seed-5 reverse/support collapse without moving into the double-support standstill/reverse basin. The useful evidence from this diagnostic is:

1. A100 Colab can run the corrected restore checkpoint when the env count is small.
2. The restore packaging path is now fixed and durable.
3. Strong support/double-support shaping is too blunt: it stabilizes seed 5 in the short screen but preserves the wrong sign of motion.
4. The next correction should preserve teacher-continuity motion and add a narrower anti-reverse / base-height stability term, not a broad z005-support recipe.
