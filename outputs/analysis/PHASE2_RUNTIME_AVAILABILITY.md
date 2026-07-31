# Phase 2 Runtime Availability

status: `HOLD_GPU_RUNTIME_UNAVAILABLE`
generated_at: `2026-07-06T10:41:27Z`

Offline only. No robot, SSH, deploy, grounded replay, training-result
promotion, or runtime behavior change was performed.

## Colab Sessions

- None detected.

## Local ROCm GPU Owners

- `2081956    2924 Rl      04:54:49  118  2.4 /home/lsd/robots/envs/lerobot-so101/bin/python train_dreamer.py --logdir /home/lsd/robots/so101_dreamer_ue/training/runs/run11_20260706_continued`

## Stage A Checkpoint State

- checkpoint_count: `0`

## Decision

No adoptable Colab session is visible and local ROCm has active GPU owner processes. Do not start Stage A until one runtime is free.

## Commands

Adopt visible Colab session:

```bash
python3 tools/launch_phase2_stage_a_rate175_colab.py --adopt-existing-session --no-create --run-workflow --output-dir outputs/analysis/phase2_stage_a_rate175_colab_adopt_existing
```

Wait for a visible Colab session:

```bash
python3 tools/launch_phase2_stage_a_rate175_colab.py --adopt-existing-session --wait-for-existing-session --wait-timeout-s 3600 --wait-interval-s 30 --no-create --run-workflow --output-dir outputs/analysis/phase2_stage_a_rate175_colab_wait_adopt
```
