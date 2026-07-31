# Support-Transition Recovery X0 Baseline Comparison

status: `HOLD_STRICT_X0_FLAT_GATE_BASELINE_AND_SMOKE`

This comparison was added after the support-transition smoke failed the stricter
x=0.0 fitted gate. The original step-0 warm start was rerun under the same gate
to determine whether the smoke introduced the failure.

## Gate

```text
task: flat_terrain
command_x: 0.0
duration: 15 s
bridge: fitted
seeds: 0-7
```

## Compared Policies

```text
baseline:
  onnx: outputs/analysis/ppo_bc_swish_cmd_pitch_rl_2p25_step0.onnx
  artifact: outputs/analysis/CMD_PITCH_RL_2P25_STEP0_FLAT_X0_FITTED_15S.md

support smoke:
  source: /tmp/open_duck_support_transition_recovery_finetune/smoke_20260627T021502Z_cpu/2026_06_26_221541_1040.onnx
  artifact: outputs/analysis/SUPPORT_TRANSITION_RECOVERY_FINETUNE_X0_FITTED_15S.md
```

## Result

| policy | falls | duration complete | failed seeds | samples mean | vx mean | base height min mean |
|---|---:|---:|---|---:|---:|---:|
| baseline step-0 | 2 / 8 | 6 / 8 | 1, 7 | 570.6250 | 0.0023 | 0.1350 |
| support smoke step-1040 | 2 / 8 | 6 / 8 | 1, 7 | 570.6250 | -0.0023 | 0.1358 |

Hard-seed details:

| policy | seed | samples | base_height_min | max_pitch_vel_p95 | max_tracking_p95 |
|---|---:|---:|---:|---:|---:|
| baseline step-0 | 1 | 31 | 0.0858 | 1.8460 | 0.2600 |
| support smoke step-1040 | 1 | 32 | 0.0817 | 1.1102 | 0.2729 |
| baseline step-0 | 7 | 34 | 0.0714 | 1.4149 | 0.3086 |
| support smoke step-1040 | 7 | 33 | 0.0827 | 0.8423 | 0.3268 |

## Interpretation

The support-transition smoke did not create a new x=0 hard-seed failure. The
original command-conditioned pitch-rate-limited step-0 warm start already fails
the stricter `flat_terrain`, 15-second x=0.0 fitted gate on seeds 1 and 7.

The smoke also did not fix that failure. It lowered hard-seed target velocity
but did not reduce hard-seed fitted tracking enough to prevent collapse.

Do not run x=0.08 for the support smoke and do not scale this exact recipe to
A100. The next decision is whether the canonical zero-command promotion gate is
the older 10-second `flat_terrain_backlash` gate or the stricter 15-second
`flat_terrain` gate. If the stricter gate is canonical, hard-seed x=0 stability
must be solved before any more x=0.08 tuning.
