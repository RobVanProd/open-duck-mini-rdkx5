# Phase 2 z=0.005 Motion-Floor Next Recipe

status: `PASS_Z005_MOTION_FLOOR_RECIPE_READY`
stage: `stage_z005_motion_floor`
supersedes_recipe: `phase2-z005-support`
diagnosis_status: `HOLD_Z005_SUPPORT_OVER_REGULARIZED_LOW_PROGRESS`

## Root Cause Summary

- The T4 z=0.005 support run completed training and stayed under the corrected velocity envelope.
- The recovered latest checkpoint under-moved at x=0.08 in the local debug sweep: track_ratio_mean 0.1773, vx_mean 0.0142.
- The failure was low forward progress, not actuator velocity excess.
- The next recipe returns to the A2 restore checkpoint; it does not continue from the under-moving T4 latest checkpoint.

## Recipe Intent

- Preserve the corrected-bridge A2 walking behavior while adapting to z=0.005 terrain.
- Keep no-push z=0.005 as the active rung; do not advance to push or stronger terrain.
- Raise command-progress pressure so support rewards cannot win by freezing.
- Reduce support/base-height damping relative to phase2-z005-support to avoid suppressing forward motion.
- Keep corrected actuator bridge limits authoritative and reject velocity excess at the gate.

## Key Changes

- `num_timesteps`: 81920 -> 122880
- `restore_policy_kl_scale`: 4.0 -> 3.0
- `ppo_learning_rate`: 0.000003 -> 0.000004
- `command_progress_scale`: 1.5 -> 3.0
- `command_progress_shortfall_scale`: -4 -> -8
- `command_progress_required_ratio`: 0.45 -> 0.50
- `forward_progress_scale`: 2.5 -> 4.0
- `forward_contact_support_scale`: -0.35 -> -0.12
- `forward_double_support_dwell_scale`: -0.25 -> -0.05
- `base_height_scale`: -0.8 -> -0.35
- `action_rate_scale`: -0.08 -> -0.055
- `actuator_tracking_scale`: -0.01 -> -0.005

## Preferred Colab GPU Command

```bash
python3 \
    tools/run_colab_cli_cuda_workflow.py \
    --workflow \
    phase2-z005-motion-floor \
    --session \
    open-duck-l4 \
    --candidate-name \
    phase2_z005_motion_floor_cuda \
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

## Local ROCm Fallback

```bash
../envs/open-duck-playground/bin/python \
    tools/run_actuator_bridge_training_smoke.py \
    --playground-path \
    ../Open_Duck_Playground \
    --env-python \
    ../envs/open-duck-playground/bin/python \
    --output-root \
    outputs/phase2_domain_randomization/stage_z005_motion_floor_local_rocm_safeenv_8env_122880 \
    --run \
    --platform \
    gpu \
    --local-rocm-safe-env \
    --timeout-s \
    2700 \
    --task \
    rough_terrain_backlash \
    --num-timesteps \
    122880 \
    --export-min-step \
    1 \
    --ppo-num-envs \
    8 \
    --ppo-num-evals \
    4 \
    --ppo-episode-length \
    750 \
    --ppo-unroll-length \
    20 \
    --ppo-batch-size \
    64 \
    --ppo-num-minibatches \
    1 \
    --ppo-num-updates-per-batch \
    2 \
    --restore-checkpoint-path \
    outputs/phase2_domain_randomization/stage_a2_preserve_narrow_flat_no_push_gpu/smoke_20260628T031553Z_gpu/2026_06_27_232221_491520 \
    --ppo-learning-rate \
    0.000004 \
    --ppo-entropy-cost \
    0.001 \
    --ppo-clipping-epsilon \
    0.025 \
    --ppo-max-grad-norm \
    0.12 \
    --restore-policy-kl-scale \
    3 \
    --tracking-lin-vel-scale \
    3 \
    --tracking-sigma \
    0.01 \
    --forward-progress-scale \
    4 \
    --command-progress-scale \
    3 \
    --command-progress-shortfall-scale \
    -8 \
    --command-progress-required-ratio \
    0.5 \
    --command-progress-warmup-steps \
    30 \
    --forward-wrong-direction-scale \
    -6 \
    --forward-wrong-direction-allowed-reverse-ratio \
    0.01 \
    --action-rate-scale \
    -0.055 \
    --action-magnitude-scale \
    -0.003 \
    --base-height-scale \
    -0.35 \
    --forward-pitch-scale \
    -0.3 \
    --forward-pitch-rate-scale \
    -0.06 \
    --forward-contact-support-scale \
    -0.12 \
    --forward-contact-support-no-contact-weight \
    1.0 \
    --forward-contact-support-asymmetry-weight \
    0.1 \
    --forward-single-support-scale \
    0.05 \
    --forward-double-support-scale \
    -0.05 \
    --forward-double-support-dwell-scale \
    -0.05 \
    --forward-double-support-dwell-grace-steps \
    24 \
    --forward-swing-clearance-scale \
    -0.00025 \
    --forward-swing-clearance-target-m \
    0.016 \
    --forward-swing-clearance-huber-delta \
    0.003 \
    --forward-swing-advance-scale \
    -0.001 \
    --forward-swing-advance-target-m \
    0.004 \
    --forward-swing-advance-huber-delta \
    0.002 \
    --alive-scale \
    2 \
    --imitation-scale \
    0 \
    --lin-vel-x-min \
    0.06 \
    --lin-vel-x-max \
    0.1 \
    --lin-vel-y-min \
    0 \
    --lin-vel-y-max \
    0 \
    --ang-vel-yaw-min \
    0 \
    --ang-vel-yaw-max \
    0 \
    --command-resample-steps \
    600 \
    --zero-command-probability \
    0.15 \
    --dr-friction-min \
    0.98 \
    --dr-friction-max \
    1.02 \
    --dr-frictionloss-scale-min \
    0.995 \
    --dr-frictionloss-scale-max \
    1.005 \
    --dr-armature-scale-min \
    1 \
    --dr-armature-scale-max \
    1.005 \
    --dr-com-jitter-m \
    0.002 \
    --dr-mass-scale-min \
    0.995 \
    --dr-mass-scale-max \
    1.005 \
    --dr-torso-mass-delta-min \
    -0.005 \
    --dr-torso-mass-delta-max \
    0.005 \
    --dr-qpos-jitter-rad \
    0.002 \
    --dr-actuator-gain-scale-min \
    0.995 \
    --dr-actuator-gain-scale-max \
    1.005 \
    --dr-leg-geometry-jitter-scale \
    0.001 \
    --noise-level \
    0.5 \
    --noise-hip-pos \
    0.0075 \
    --noise-knee-pos \
    0.0075 \
    --noise-ankle-pos \
    0.0075 \
    --noise-joint-vel \
    0.75 \
    --noise-gravity \
    0.04 \
    --noise-gyro \
    0.04 \
    --noise-accelerometer \
    0.02 \
    --no-push-enable \
    --actuator-bridge-delay-min-ticks \
    3 \
    --actuator-bridge-delay-max-ticks \
    3 \
    --actuator-bridge-tau-min-s \
    0.06 \
    --actuator-bridge-tau-max-s \
    0.14 \
    --actuator-bridge-velocity-limit-min-rad-s \
    2 \
    --actuator-bridge-velocity-limit-max-rad-s \
    3.25 \
    --actuator-bridge-per-joint-variation \
    0.1 \
    --actuator-tracking-scale \
    -0.005 \
    --actuator-tracking-huber-delta \
    0.03 \
    --terrain-hfield-z-scale \
    0.005
```

## Acceptance

- z=0.005 x=0.08 no-push passes 8/8, zero falls, no velocity excess, tracking p95 <= 0.20, track ratio >= 0.40.
- z=0.005 x=0.0 no-push passes 8/8, zero falls, no velocity excess, |mean vx| <= 0.005.
- z=0.002 no-push and gentle-push regression gates remain passing.

## Falsifier

If this recipe also stays under envelope but under-moves at x=0.08, stop adding z=0.005 support penalties and introduce an intermediate z=0.0035 terrain rung or a terrain-specific command-progress curriculum.

No robot, SSH, deploy, grounded replay, or runtime behavior change is authorized by this recipe.
