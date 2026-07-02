# Phase 2 z=0.00245 Motion-Recovery Next Recipe

status: `PASS_Z00245_MOTION_RECOVERY_RECIPE_READY`
stage: `stage_z00245_motion_recovery`
supersedes: `stage_z00245_on_policy_support_recovery`
diagnosis_status: `HOLD_Z00245_ON_POLICY_SUPPORT_LOW_PROGRESS`

This is an offline planning artifact. It did not train, SSH, deploy, or touch the robot.

## Root Cause Summary

- The z=0.00245 A100 support run completed and exported checkpoints.
- All compact x=0.08 screens stayed below the corrected per-joint velocity envelope with zero saturation.
- All compact x=0.08 screens under-moved: track ratio 0.1823-0.2200 and mean vx 0.0146-0.0176 m/s.
- The hold is conservative low progress plus a small tracking miss, not actuator overspeed.

## Recipe Intent

- Warm-start from the same Phase A2 trainable checkpoint; do not train from scratch.
- Keep the z=0.00245 terrain rung; do not advance terrain or add pushes.
- Raise command/forward-progress pressure enough to escape the conservative gait.
- Relax target-rate damping slightly because the failed checkpoints were far below the corrected envelope.
- Keep corrected actuator tracking active and reject any post-training velocity excess at the gate.

## Key Changes

- `phase2_forward_progress_scale`: 4.0 -> 5.0
- `phase2_command_progress_scale`: 3.0 -> 4.0
- `phase2_command_progress_shortfall_scale`: -8.0 -> -12.0
- `phase2_command_progress_required_ratio`: 0.45 -> 0.55
- `phase2_target_rate_scale`: -0.01 -> -0.005
- `phase2_actuator_tracking_scale`: -0.005 unchanged
- `terrain_hfield_z_scale`: 0.00245 unchanged
- `push_enable`: disabled unchanged

## Preferred Colab GPU Command

```bash
python3 \
    tools/run_colab_cli_cuda_workflow.py \
    --workflow \
    phase2-z0025-boundary \
    --session \
    open-duck-a100-phase2-z00245 \
    --candidate-name \
    phase2_z00245_motion_recovery_cuda \
    --phase2-terrain-hfield-z-scale \
    0.00245 \
    --phase2-num-timesteps \
    122880 \
    --phase2-ppo-num-envs \
    64 \
    --phase2-ppo-batch-size \
    512 \
    --phase2-ppo-num-minibatches \
    4 \
    --phase2-ppo-num-updates-per-batch \
    2 \
    --phase2-target-rate-scale \
    -0.005 \
    --phase2-actuator-tracking-scale \
    -0.005 \
    --phase2-forward-progress-scale \
    5.0 \
    --phase2-command-progress-scale \
    4.0 \
    --phase2-command-progress-shortfall-scale \
    -12.0 \
    --phase2-command-progress-required-ratio \
    0.55 \
    --candidate-checkpoint-sweep \
    --candidate-checkpoint-sweep-commands \
    0.0,0.08 \
    --candidate-checkpoint-sweep-duration \
    1.0 \
    --candidate-checkpoint-sweep-jax-platform \
    cpu \
    --candidate-timeout-s \
    10800 \
    --run
```

## Detached Colab GPU Command

```bash
python3 \
    tools/run_colab_cli_cuda_workflow.py \
    --workflow \
    phase2-z0025-boundary \
    --session \
    open-duck-a100-phase2-z00245 \
    --candidate-name \
    phase2_z00245_motion_recovery_cuda \
    --phase2-terrain-hfield-z-scale \
    0.00245 \
    --phase2-num-timesteps \
    122880 \
    --phase2-ppo-num-envs \
    64 \
    --phase2-ppo-batch-size \
    512 \
    --phase2-ppo-num-minibatches \
    4 \
    --phase2-ppo-num-updates-per-batch \
    2 \
    --phase2-target-rate-scale \
    -0.005 \
    --phase2-actuator-tracking-scale \
    -0.005 \
    --phase2-forward-progress-scale \
    5.0 \
    --phase2-command-progress-scale \
    4.0 \
    --phase2-command-progress-shortfall-scale \
    -12.0 \
    --phase2-command-progress-required-ratio \
    0.55 \
    --candidate-checkpoint-sweep \
    --candidate-checkpoint-sweep-commands \
    0.0,0.08 \
    --candidate-checkpoint-sweep-duration \
    1.0 \
    --candidate-checkpoint-sweep-jax-platform \
    cpu \
    --candidate-timeout-s \
    10800 \
    --no-poll \
    --run
```

## Acceptance

- Compact x=0.08 checkpoint sweep must find at least one checkpoint with track ratio >= 0.25 and mean vx >= 0.02 m/s while staying below the corrected envelope.
- Promoted checkpoint must pass the normal corrected-bridge x=0.0 and x=0.08 8-seed gates before any robot consideration.
- x=0.0 command semantics must remain stable; zero-command drift is not acceptable progress.
- No robot, SSH, deploy, grounded replay, or runtime behavior change is authorized by this recipe.

## Falsifier

If this recipe remains in-envelope but still under-moves at x=0.08, stop this scalar-progress-pressure path. The next branch should add a behavior-prior/teacher-continuity mechanism or live-oracle data, not another generic support/safety penalty.
