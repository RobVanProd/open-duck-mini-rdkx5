# Support-Transition Recovery Fine-Tune Smoke Result

status: `HOLD_X0_HARD_SEED_FAILURE_NOT_FIXED`

This was a tiny offline CPU PPO smoke from the reviewed support-transition
recovery plan. It did not SSH, deploy, touch the robot, modify runtime config,
or overwrite any policy.

## Inputs

```text
plan: docs/SUPPORT_TRANSITION_RECOVERY_FINETUNE_PLAN.md
dry-run manifest: outputs/analysis/support_transition_recovery_finetune/dry_run_manifest.json
final manifest: outputs/analysis/support_transition_recovery_finetune/final_manifest.json
restore checkpoint: outputs/analysis/ppo_bc_swish_cmd_pitch_rl_2p25_step0_checkpoint
platform: CPU
timesteps: 1040 exported PPO steps
```

Training completed:

```text
status: PASS_SMOKE_RUN
elapsed_s: 61.21
reward at step 1040: 38.2625
```

The smoke exported an ONNX under `/tmp`, but it is not committed because the
first required gate failed.

## Gate

The required first gate was x=0.0, fitted actuator bridge, 15 seconds, seeds
0-7:

```text
artifact: outputs/analysis/SUPPORT_TRANSITION_RECOVERY_FINETUNE_X0_FITTED_15S.md
json: outputs/analysis/support_transition_recovery_finetune_x0_fitted_15s.json
```

Smoke result:

```text
falls: 2 / 8
duration complete: 6 / 8
failed seeds: 1, 7
seed 1 samples: 32
seed 7 samples: 33
mean vx: -0.0023 m/s
```

The passing seeds were clean, but the hard seeds fell immediately:

```text
seed 1 base_height_min: 0.0817 m
seed 1 max_tracking_p95: 0.2729 rad
seed 7 base_height_min: 0.0827 m
seed 7 max_tracking_p95: 0.3268 rad
```

## Baseline Control

After this smoke failed the stricter x=0 gate, the original step-0 warm start
was rerun under the same gate:

```text
artifact: outputs/analysis/CMD_PITCH_RL_2P25_STEP0_FLAT_X0_FITTED_15S.md
json: outputs/analysis/cmd_pitch_rl_2p25_step0_flat_x0_fitted_15s.json
```

The baseline also failed on the same two seeds:

```text
falls: 2 / 8
failed seeds: 1, 7
seed 1 samples: 31
seed 7 samples: 34
```

So the support-transition smoke did not create a new x=0 hard-seed failure; it
also did not fix the pre-existing hard-seed failure exposed by the stricter
`flat_terrain`, 15-second gate.

## Decision

Do not run the x=0.08 gate for this smoke. The plan's first stop rule was:

```text
x=0.0 falls on any seed
```

This smoke violates that rule. The support-transition reward mix did not clear
the stricter x=0 hard-seed stability gate.

## Interpretation

The result is useful because it separates plumbing from behavior:

```text
restore/export path: pass
stricter x=0 flat gate on original warm start: hold
support-transition smoke objective: same hold pattern
robot candidate: no
```

The next offline work should not scale this exact recipe to A100. The first
task is to fix the seed 1/7 x=0 flat-terrain hard-seed failure or choose a
canonical gate intentionally. More x=0.08 tuning is premature while the stricter
x=0 gate fails.
