# Colab Session Status

status: `PASS_COLAB_SESSION_VISIBLE`
timestamp: `20260629T091639Z`

- robot_touched: `false`
- training_started: `false`
- deploy_performed: `false`
- colab_executable: `/home/lsd/.local/bin/colab`

## Visible Sessions

```text
[open-duck-a100] gpu-a100-s-kkb-ass1c2-3rfkg8zz5reqn | Hardware: A100 | Variant: GPU
```

## Probed Session Names

| session | exists | status |
|---|---:|---|
| `open-duck-l4` | `False` | `[colab] Session 'open-duck-l4' not found.` |
| `open-duck-a100` | `True` | `[open-duck-a100] gpu-a100-s-kkb-ass1c2-3rfkg8zz5reqn | Hardware: A100 | Variant: GPU | Status: IDLE` |
| `open-duck-a100a` | `False` | `[colab] Session 'open-duck-a100a' not found.` |

## Next Command

Run this only after confirming the session is the desired CUDA/A100 runtime:

```bash
python3 tools/run_colab_cli_cuda_workflow.py --workflow phase2-b0e --session open-duck-a100 --candidate-name phase2_b0e_motion_preserving_tracking_cuda --candidate-timeout-s 10800 --candidate-checkpoint-sweep --candidate-checkpoint-sweep-commands 0.0,0.08 --candidate-checkpoint-sweep-duration 1.0 --candidate-checkpoint-sweep-jax-platform cpu --candidate-checkpoint-sweep-timeout-s 7200 --run
```

## Interpretation

This report is infrastructure-only evidence. It does not approve robot
validation and does not change the Phase 2 gate. A B0E artifact is useful
only after the corrected-bridge rough-terrain gentle-push gates are run
and reviewed locally.
