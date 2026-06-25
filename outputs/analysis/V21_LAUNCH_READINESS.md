# V21 Launch Readiness

status: `HOLD_COLAB_SESSION_MISSING`
timestamp: `20260625T083335Z`

## Required Checks

| check | status | detail |
|---|---|---|
| soft prior config | `True` | 50 rows, dataset `c4833a96744101d9` |
| V21 plan | `True` | recipe `movement_bootstrap_v21`, phase gate x `0.04` |
| Playground soft-prior patch | `True` | default-off hook present |
| Colab session | `False` | [colab] Session 'open-duck-l4' not found. |

## Launch Command

```bash
python3 tools/run_colab_cli_cuda_workflow.py --session open-duck-l4 --workflow staged-curriculum --staged-recipe movement_bootstrap_v21 --staged-phase-gate-seeds 0-3 --staged-phase-gate-command-x 0.04 --staged-phase-gate-bridge-mode vanilla --staged-phase-gate-freeze-check --run
```

## Safety

This preflight did not start training, SSH, deploy, change robot runtime
behavior, or touch the robot.

## PR Status

- `RobVanProd/open-duck-mini-rdkx5#74` ok=`True` state=`OPEN` draft=`True` mergeable=`MERGEABLE` checks=`2`
- `RobVanProd/Open_Duck_Playground#4` ok=`True` state=`OPEN` draft=`True` mergeable=`MERGEABLE` checks=`2`
