# Phase 2 z=0.002 Teacher Continuity Training Start Isolation

status: `HOLD_COLAB_A100_TRAINING_START`

## Question

The corrected Phase 2 teacher-continuity full run disappeared on Colab A100 after launching training. This isolation checked whether the recipe itself is invalid or whether the hosted A100 execution path is failing.

## A100 Foreground Diagnostic

- workflow: `phase2-z002-teacher-continuity`
- candidate_name: `phase2_z002_teacher_continuity_fg64`
- phase2 timesteps override: `64`
- run_dir: `outputs/analysis/colab_cli/open-duck-l4-phase2-z002-teacher-continuity-20260630T041517Z`
- execution mode: `--foreground-remote`
- dependency install: skipped, reused pinned session stack
- contract audit: skipped for speed after prior pass
- result: `HOLD_REMOTE_NO_SENTINEL`

The foreground run emitted the expected corrected command:

`--num-timesteps 64 --actuator-tracking-scale -0.005`

It then disappeared at training startup before writing an exit sentinel, artifact bundle, training summary, checkpoint sweep, or candidate ONNX.

## Local CPU Control

- command: same corrected teacher-continuity recipe, reduced local diagnostic settings
- platform: CPU
- timesteps: `64`
- num_envs: `8`
- output: `outputs/phase2_domain_randomization/stage_z002_teacher_continuity_local_cpu_fg64/smoke_20260630T042347Z_cpu`
- result: `PASS_SMOKE_RUN`
- returncode: `0`
- elapsed_s: `502.08`
- checkpoint: `2026_06_30_002512_10240`
- ONNX: `2026_06_30_002512_10240.onnx`
- reward line: `STEP: 10240 reward: 33.31049346923828 reward_std: 29.646678924560547`

## Interpretation

The recipe and restore/checkpoint paths are valid enough to enter PPO, checkpoint, and export locally. The current blocker is therefore the Colab A100 execution/session path at training startup, not the corrected teacher-continuity recipe itself.

## Decision

`HOLD_COLAB_A100_TRAINING_START`

Do not spend more A100 time on the full detached workflow until the Colab training-start disappearance is isolated. Candidate promotion remains blocked because no valid A100 Phase 2 checkpoint/gate exists from this recipe.

No robot tests, SSH, deployment, grounded replay, or runtime behavior changes were performed.
