# Phase 2 z=0.0025 Boundary Next Recipe

status: `PASS_Z0025_BOUNDARY_RECIPE_READY`
stage: `stage_z0025_boundary`
supersedes_recipe: `phase2-z0035-motion-floor`
diagnosis_status: `PASS_Z0024_AND_HOLD_Z0025_SEED5_SUPPORT_COLLAPSE`

This is an offline planning artifact. It did not train, SSH, deploy, or touch the robot.

## Root Cause Summary

- The gain099 corrected-bridge candidate passes the full z=0.0024 rough-terrain matrix.
- Seed 5 passes z=0.0024 but fails at z=0.0025 by backward support collapse.
- The z=0.0025 failure has zero corrected-envelope velocity excess, so actuator rate is not the immediate blocker.
- Prior z=0.0035/z=0.005 support and motion-floor variants jumped past the measured cliff and held by low progress or collapse.

## Recipe Intent

- Warm-start from the trainable A2 checkpoint that produced the gain099 candidate; do not train from scratch.
- Train directly at z=0.0025, the first failing terrain height above the confirmed z=0.0024 rung.
- Use motion-preserving progress pressure and light support/stance penalties, not the stronger z=0.005 support recipe.
- Keep the corrected actuator envelope authoritative and reject any post-training velocity excess.
- Preserve z=0.0024 no-push/gentle-push regressions and x=0.0 command semantics.

## Key Settings

- `workflow`: `phase2-z0025-boundary`
- `terrain_hfield_z_scale`: `0.0025`
- `num_timesteps`: `122880`
- `restore_policy_kl_scale`: `3.0`
- `ppo_learning_rate`: `4e-06`
- `ppo_num_envs`: `64`
- `command_progress_scale`: `3.0`
- `command_progress_shortfall_scale`: `-8.0`
- `command_progress_required_ratio`: `0.5`
- `forward_progress_scale`: `4.0`
- `base_height_scale`: `-0.35`
- `actuator_tracking_scale`: `-0.005`
- `push_enable`: `False`
- `actuator_bridge_velocity_limit_range_rad_s`: `[2.0, 3.25]`
- `narrow_dr`: `{'friction': [0.98, 1.02], 'mass_scale': [0.995, 1.005], 'com_jitter_m': 0.002, 'leg_geometry_jitter_scale': 0.001}`

## Preferred Colab GPU Command

```bash
python3 \
    tools/run_colab_cli_cuda_workflow.py \
    --workflow \
    phase2-z0025-boundary \
    --session \
    open-duck-a100-phase2d \
    --candidate-name \
    phase2_z0025_boundary_cuda \
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

- z=0.0025 x=0.08 no-push passes 8/8, zero falls, no velocity excess, tracking p95 <= 0.20, track ratio >= 0.40.
- z=0.0025 x=0.0 no-push passes 8/8, zero falls, no velocity excess, |mean vx| <= 0.005.
- z=0.0024 x=0.08 and x=0.0 no-push/gentle-push regression gates remain passing.
- Passing z=0.0025 is not robot-validation clearance; it only authorizes the next terrain increment.

## Falsifier

If z=0.0025 still fails seed 5 by backward support collapse while z=0.0024 regressions remain clean, stop terrain escalation and train a targeted seed-5 support-recovery curriculum at z=0.0024->0.0025 before adding wider DR.
