# PPO Trainable Warm-Start z0.0075 Push Decision

status: `HOLD_NO_TASK_MATCHED_TRAINABLE_WARMSTART`

Offline candidate-screen diagnostic only. No training, robot test, SSH, deploy,
grounded replay, or runtime behavior change was performed.

## Question

Several PPO-compatible step-0 checkpoints pass earlier, easier corrected-bridge
gates. The current Phase 2 robustness blocker is different:

```text
task: rough_terrain_backlash
terrain_hfield_z_scale: 0.0075
reset_mode: home-support
reset_settle_ticks: 10
bridge: fitted corrected bridge
command_x: 0.08
pushes: 0.075-0.125, interval 1.0-1.5s
screen seeds: 0,1,2,6,7
```

This diagnostic asks whether either older PPO-compatible warm-start can be used
as the trainable parent for the current z0.0075 push stage.

## Inputs

| label | ONNX | sha256 |
|---|---|---|
| `limit198_step0` | `outputs/analysis/phase2_limit198_ppo_loc_warmstart_step0.onnx` | `1dc894eebc144d790f1a6b4be6ada5a05e748f215f2053c72610347955deb3bb` |
| `rate165_step0` | `outputs/analysis/phase2_rate165_ppo_loc_warmstart_step0.onnx` | `3aa2770022d2b5b0e6cf77df45d4ce1a2aeb2c86e80f57e3892a6ad9bd65ad5a` |

Reference comparison:

| label | current-gate status |
|---|---|
| `ppo_loc_iter24_step0` | `2/5` pass on the same z0.0075 push screen, with failures on seeds 0, 6, and 7 |

## Result

Artifact:

```text
outputs/analysis/PPO_TRAINABLE_WARMSTART_Z0075_PUSH_SCREEN.md
outputs/analysis/ppo_trainable_warmstart_z0075_push_screen.json
```

### Per-Policy Summary

| policy | pass | falls | duration complete | mean track ratio | mean vx | p95 excess mean | max excess mean | single support mean | double support mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `limit198_step0` | 0/5 | 2/5 | 3/5 | 0.1630 | 0.0130 | 0.0000 | 0.5745 | 26.0032 | 73.7059 |
| `rate165_step0` | 0/5 | 3/5 | 2/5 | 1.1016 | 0.0881 | 0.0000 | 0.2350 | 12.7626 | 86.1933 |

### Failure Shape

`limit198_step0`:

- Seeds 0, 1, and 2 complete duration but hold on target velocity.
- Seeds 6 and 7 fall.
- It has zero p95 velocity excess, but nonzero max corrected-envelope spikes.
- It is safer than `rate165_step0`, but too slow and not robust under the
  current push gate.

`rate165_step0`:

- Seeds 0, 1, and 2 fall early with high body pitch and low base height.
- Seeds 6 and 7 complete duration but hold on target velocity.
- It moves more aggressively but is not stable.

## Decision

Neither older PPO-compatible step-0 checkpoint is a valid trainable parent for
the current z0.0075 rough+push Phase 2 stage.

Do not launch a long PPO/domain-randomization run from:

```text
outputs/analysis/phase2_limit198_ppo_loc_warmstart_step0_checkpoint
outputs/analysis/phase2_rate165_ppo_loc_warmstart_step0_checkpoint
outputs/analysis/ppo_loc_iter24_live_oracle_seed2_active_rate150_step0_checkpoint
```

unless a new task-matched behavior-preserving screen first clears the current
z0.0075 push gate. The older z0.0026/no-push `8/8` gates are not transferable
evidence for this stage.

The next aligned Phase 2 action is to produce a trainable checkpoint whose
step-0 export is selected by the current z0.0075 rough+push corrected-bridge
gate, not by action fidelity alone and not by earlier/easier stage gates.
