# Phase 2 z=0.0035 Motion-Floor Next Recipe

status: `PASS_Z0035_MOTION_FLOOR_RECIPE_READY`
stage: `stage_z0035_motion_floor`
supersedes_recipe: `phase2-z005-motion-floor`
diagnosis_status: `HOLD_Z005_MOTION_FLOOR_UNDER_MOVING`

This is an offline planning artifact. It did not train, SSH, deploy, or touch the robot.

## Root Cause Summary

- The packaged candidate passes z=0.002 corrected-bridge terrain and gentle-push gates.
- The z=0.005 support, motion-floor, and behavior-prior motion-floor attempts stayed under the corrected velocity envelope but under-moved at x=0.08.
- The motion-prior T4 compact sweep best completed x=0.08 track ratio was 0.1703, below the compact promotion floor 0.25.
- The next curriculum step should test an intermediate terrain height rather than adding more regularization at z=0.005.

## Recipe Intent

- Warm-start from the same corrected-bridge A2 checkpoint; do not train from scratch.
- Use z=0.0035 rough terrain as an intermediate rung between passing z=0.002 and failing z=0.005.
- Keep the motion-floor command-progress pressure that preserves forward intent.
- Keep the corrected actuator envelope authoritative and reject velocity excess at the gate.
- Do not use the behavior prior in this rung because the z=0.005 behavior-prior run did not improve forward progress.

## Key Settings

- `workflow`: `phase2-z0035-motion-floor`
- `terrain_hfield_z_scale`: `0.0035`
- `num_timesteps`: `122880`
- `restore_policy_kl_scale`: `3.0`
- `ppo_learning_rate`: `4e-06`
- `command_progress_scale`: `3.0`
- `command_progress_shortfall_scale`: `-8.0`
- `command_progress_required_ratio`: `0.5`
- `forward_progress_scale`: `4.0`
- `base_height_scale`: `-0.35`
- `actuator_tracking_scale`: `-0.005`
- `push_enable`: `False`
- `actuator_bridge_velocity_limit_range_rad_s`: `[2.0, 3.25]`

## Preferred Colab GPU Command

```bash
python3 \
    tools/run_colab_cli_cuda_workflow.py \
    --workflow \
    phase2-z0035-motion-floor \
    --session \
    open-duck-l4 \
    --candidate-name \
    phase2_z0035_motion_floor_cuda \
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

## Acceptance

- z=0.0035 x=0.08 no-push passes 8/8, zero falls, no velocity excess, tracking p95 <= 0.20, track ratio >= 0.40.
- z=0.0035 x=0.0 no-push passes 8/8, zero falls, no velocity excess, |mean vx| <= 0.005.
- z=0.002 no-push and gentle-push regression gates remain passing.
- Passing z=0.0035 is not a robot-validation clearance; it only authorizes returning to z=0.005 with a smaller gap.

## Falsifier

If z=0.0035 also under-moves while staying under envelope, stop terrain height escalation and re-check the z=0.002 moving policy under the same post-training gate path before another training run.
