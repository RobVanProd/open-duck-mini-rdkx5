# V21 Launch Readiness

status: `PASS_V21_READY_TO_LAUNCH`
timestamp: `20260625T085941Z`

## Required Checks

| check | status | detail |
|---|---|---|
| soft prior config | `True` | 50 rows, dataset `c4833a96744101d9` |
| V21 plan | `True` | recipe `movement_bootstrap_v21`, phase gate x `0.04` |
| Playground soft-prior patch | `True` | default-off hook present |
| Colab session | `True` | [open-duck-l4] gpu-l4-s-kkb-ass1a0-1gg47a8cm4zf7 | Hardware: L4 | Variant: GPU | Status: IDLE |
| browser-Colab fallback | `True` | `tools/print_cuda_colab_cell.py --staged-curriculum-v21` |

## Launch Command

```bash
python3 tools/run_colab_cli_cuda_workflow.py --session open-duck-l4 --workflow staged-curriculum --staged-recipe movement_bootstrap_v21 --staged-phase-gate-seeds 0-3 --staged-phase-gate-command-x 0.04 --staged-phase-gate-bridge-mode vanilla --staged-phase-gate-freeze-check --run
```

## Browser-Colab Fallback

Use this when `google-colab-cli` cannot see the session but a browser
Colab notebook is already authenticated:

```bash
python3 tools/print_cuda_colab_cell.py --staged-curriculum-v21 --rdk-branch codex/colab-cli-cuda-workflow --playground-branch codex/forward-progress-reward --handoff-dir /home/lsd/robots/cuda_colab_handoff_v21
```

Then open the generated notebook and run its single cell.

## Safety

This preflight did not start training, SSH, deploy, change robot runtime
behavior, or touch the robot.

## PR Status

- `RobVanProd/open-duck-mini-rdkx5#74` ok=`True` state=`OPEN` draft=`True` mergeable=`MERGEABLE` checks=`2`
- `RobVanProd/Open_Duck_Playground#4` ok=`True` state=`OPEN` draft=`True` mergeable=`MERGEABLE` checks=`2`
