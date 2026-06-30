# Phase 2 z=0.002 Tracking-Margin Next Recipe

status: `PASS_Z002_TRACKING_MARGIN_RECIPE_READY`
stage: `stage_z002_tracking_margin`
supersedes_recipe: `phase2-z0035-motion-floor`
diagnosis_status: `HOLD_Z0035_UNDER_MOVING`

This is an offline planning artifact. It did not train, SSH, deploy, or touch the robot.

## Root Cause Summary

- The z=0.002 C0/C2 policies still move at x=0.08 under the compact corrected-bridge sweep, with track ratio about 0.30.
- The z=0.002 policies miss the strict tracking gate at about 0.219 rad, so they need tracking margin recovery.
- The z=0.0035 motion-floor run drops to track ratio about 0.16, so terrain height escalation is eroding forward progress before causing any velocity-envelope excess.
- The next run should recover z=0.002 tracking margin from the moving C0 parent before trying a higher terrain height again.

## Recipe Intent

- Warm-start from the z=0.002 C0 245760 checkpoint, not from scratch.
- Keep terrain at z=0.002 and no pushes; this rung is about tracking margin, not harder terrain.
- Use a very small PPO update with strong restore-policy KL to avoid eroding the moving gait.
- Apply a mild target-rate penalty and light motion-floor terms while keeping forward progress pressure active.
- Reject any policy that fixes tracking by freezing or drifting at x=0.08.

## Key Settings

- `workflow`: `phase2-z002-tracking-margin`
- `terrain_hfield_z_scale`: `0.002`
- `num_timesteps`: `122880`
- `restore_policy_kl_scale`: `6.0`
- `ppo_learning_rate`: `2e-06`
- `ppo_clipping_epsilon`: `0.015`
- `ppo_max_grad_norm`: `0.08`
- `target_rate_scale`: `-0.02`
- `actuator_tracking_scale`: `-0.005`
- `command_progress_scale`: `3.5`
- `command_progress_shortfall_scale`: `-10.0`
- `command_progress_required_ratio`: `0.55`
- `forward_progress_scale`: `4.5`
- `action_rate_scale`: `-0.04`
- `push_enable`: `False`
- `actuator_bridge_velocity_limit_range_rad_s`: `[2.0, 3.25]`

## Preferred Colab GPU Command

```bash
python3 \
    tools/run_colab_cli_cuda_workflow.py \
    --workflow \
    phase2-z002-tracking-margin \
    --session \
    open-duck-l4 \
    --candidate-name \
    phase2_z002_tracking_margin_cuda \
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

- z=0.002 x=0.08 no-push passes compact sweep with track ratio >= 0.25 and tracking p95 <= 0.20.
- z=0.002 x=0.0 no-push remains passing in the compact sweep.
- Full post-training z=0.002 seed gates pass before this policy can be used as a parent for terrain escalation.
- No robot validation is authorized by this recipe.

## Falsifier

If tracking improves only by reducing x=0.08 track ratio below 0.25, stop scalar tracking-margin training and switch to a teacher-action or trust-region continuity mechanism around the moving z=0.002 policy.
