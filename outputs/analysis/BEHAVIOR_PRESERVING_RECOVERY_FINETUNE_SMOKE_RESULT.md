# Behavior-Preserving Recovery Fine-Tune Smoke Result

status: `HOLD_BEHAVIOR_PRIOR_SMOKE_REGRESSES_X008`

This was an offline-only tiny CPU PPO smoke. It did not SSH, deploy, touch the
robot, change runtime behavior, or overwrite any policy.

## Inputs

```text
plan: docs/BEHAVIOR_PRESERVING_RECOVERY_FINETUNE_PLAN.md
dry run: outputs/analysis/behavior_preserving_recovery_finetune/dry_run_manifest.json
final manifest: outputs/analysis/behavior_preserving_recovery_finetune/final_manifest.json
restore checkpoint: outputs/analysis/ppo_bc_swish_cmd_pitch_rl_2p25_step0_checkpoint
behavior prior: outputs/analysis/ppo_loc_swish_cmd_pitch_rl_2p25_candidate/candidate_mlp.npz
task: flat_terrain_backlash
bridge: fitted actuator bridge
```

The first run attempt failed because the restore checkpoint path was relative
and `runner.py` resolves paths from the Playground context:

```text
HOLD_SMOKE_RUN: checkpoint path does not exist
```

The smoke was rerun with the absolute checkpoint path:

```text
status: PASS_SMOKE_RUN
step: 1040
reward: 45.0407
exported ONNX: /tmp/open_duck_behavior_preserving_recovery/smoke_20260627T035024Z_cpu/2026_06_26_235105_1040.onnx
```

## x=0.08 Canonical Gate

Artifact:

```text
outputs/analysis/BEHAVIOR_PRESERVING_RECOVERY_FINETUNE_BACKLASH_X008_FITTED_15S.md
```

Result:

```text
duration complete: 7 / 8
fall/termination: seed 3 at 74 samples
mean vx: -0.0221 m/s
mean track ratio: -0.2758
```

Per-seed pattern:

```text
tracking holds with reduced-but-still-high tracking: seeds 0, 4, 5, 6
low-progress/reverse holds: seeds 1, 2, 7
fall/termination: seed 3
```

Matched warm-start baseline on the same gate:

```text
artifact: outputs/analysis/CMD_PITCH_RL_2P25_STEP0_BACKLASH_X008_FITTED_15S.md
duration complete: 8 / 8
falls: 0
mean vx: 0.0348 m/s
mean track ratio: 0.4344
hold reason: tracking
```

## Decision

The frozen behavior prior was not strong enough to preserve the warm start's
forward behavior through even a tiny PPO update. It partially reduced tracking
error on moving seeds, but it did so by losing motion on other seeds and
retaining a seed-3 fall.

Do not scale this exact behavior-prior recipe to A100.

The next branch should not be another small scalar adjustment around this
recipe. It needs either:

```text
- stronger behavior preservation tied to per-seed forward progress, or
- on-policy dataset expansion from successful selector rollouts, or
- closed-loop recovery training that targets the early seed-3/seed-1/seed-7
  failure states directly.
```

Robot validation remains blocked.
