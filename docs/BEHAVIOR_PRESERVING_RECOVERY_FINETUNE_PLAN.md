# Behavior-Preserving Recovery Fine-Tune Plan

Purpose: define the next offline PPO fine-tune after the support-transition
smoke showed that scalar stability/contact rewards can erase forward motion.
This is a planning artifact and dry-run manifest, not a robot approval.

## Current Baseline

Best current deployable warm start:

```text
checkpoint: outputs/analysis/ppo_bc_swish_cmd_pitch_rl_2p25_step0_checkpoint
onnx: outputs/analysis/ppo_bc_swish_cmd_pitch_rl_2p25_step0.onnx
canonical model: flat_terrain_backlash
bridge: fitted actuator bridge
```

Matched 15-second canonical x=0.08 gate:

```text
artifact: outputs/analysis/CMD_PITCH_RL_2P25_STEP0_BACKLASH_X008_FITTED_15S.md
duration complete: 8 / 8
falls: 0
mean vx: 0.0348 m/s
mean track ratio: 0.4344
hold reason: fitted tracking error
```

This checkpoint is not robot-ready, but it has the behavior that must be
preserved:

```text
stable at x=0.0 on canonical backlash
coherent low forward motion at x=0.08
target-rate p95 inside the measured actuator envelope
```

## Why The Support-Transition Smoke Is Closed

The tiny support-transition recovery smoke passed canonical x=0 hard seeds, but
regressed badly on the matched x=0.08 gate:

```text
artifact: outputs/analysis/SUPPORT_TRANSITION_RECOVERY_MATCHED_BASELINE_DECISION.md
duration complete: 7 / 8
fall/termination: seed 3
mean vx: -0.0284 m/s
mean track ratio: -0.3549
```

Interpretation: the posture/contact terms improved apparent stability by
suppressing useful movement. Do not scale that exact reward mix to A100.

## Proposed Next Smoke

Use a behavior-preserving fine-tune:

```text
restore: cmd_pitch_rl_2p25_step0 checkpoint
task: flat_terrain_backlash
bridge: fitted actuator bridge
behavior prior: frozen warm-start MLP
behavior_prior_scale: -0.10
behavior_prior_huber_delta: 0.03
learning_rate: 1e-5
ppo_clip: 0.02
max_grad_norm: 0.10
target_rate_scale: -0.0002
actuator_tracking_scale: -0.002
forward_progress_scale: 1.0
forward_shortfall_scale: -0.5
forward_wrong_direction_scale: -1.0
```

Dry-run manifest:

```text
outputs/analysis/behavior_preserving_recovery_finetune/dry_run_manifest.json
```

The key difference from the rejected support-transition smoke is the frozen
behavior prior:

```text
outputs/analysis/ppo_loc_swish_cmd_pitch_rl_2p25_candidate/candidate_mlp.npz
```

This prior should make "improve by standing still" expensive while still
allowing a small PPO update to reduce target-rate/tracking errors.

## Required Smoke Gate

Before any long GPU/A100 run, run only a tiny CPU or short GPU smoke and export
one ONNX. Then gate it on the canonical model:

```text
x=0.0, flat_terrain_backlash, fitted bridge, 15 s, seeds 0-7
x=0.08, flat_terrain_backlash, fitted bridge, 15 s, seeds 0-7
```

Compare against the warm-start baseline, not just pass/fail:

```text
x=0.0: must not introduce any fall
x=0.08: must keep duration_complete at 8 / 8
x=0.08: mean vx should stay near or above 0.0348 m/s
x=0.08: mean track ratio should stay near or above 0.4344
x=0.08: max pitch tracking p95 must improve meaningfully from ~0.20 rad
```

## Stop Rule

Stop this branch if the smoke:

```text
- reduces x=0.08 mean vx or track ratio below the warm-start baseline
- introduces any x=0.08 fall
- passes by standing still
- improves posture while fitted tracking remains near ~0.20 rad
```

If this holds, the next useful direction is not another scalar PPO recipe. It
is a larger on-policy dataset or a stronger closed-loop recovery mechanism
that explicitly learns from the source-vx selector's successful in-envelope
rollouts.

## Robot Boundary

This plan does not authorize:

```text
robot test
SSH/deploy
runtime behavior change
duck_config.json edit
policy overwrite
grounded replay
```

Robot validation remains blocked.
