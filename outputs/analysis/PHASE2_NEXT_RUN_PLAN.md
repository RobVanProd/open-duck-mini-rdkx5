# Phase 2 Next Run Plan

status: `PASS_PHASE2_NEXT_RUN_PLAN_READY`
launch_status: `PASS_PHASE2_COLAB_GPU_SESSION_READY`

## Current Decision

- current_status: `HOLD_PHASE2_TERRAIN_Z005_NOT_CLEARED`
- blocking_gate: `z005_x008_nopush`
- candidate: `policy/candidates/phase2_stagea2_seed5_recovery_command_gated_gain099_20260629/candidate.onnx`
- candidate_sha256: `209b85a75cf9cbbcf10df573c1b530921943a72e81082111889c15f63a9a2c7b`
- restore_checkpoint: `outputs/phase2_domain_randomization/stage_a2_preserve_narrow_flat_no_push_gpu/smoke_20260628T031553Z_gpu/2026_06_27_232221_491520`
- restore_checkpoint_present: `True`

## Readiness

- colab_status: `PASS_COLAB_SESSION_VISIBLE`
- colab_session: `open-duck-l4`
- colab_hardware: `A100`
- colab_active: `True`
- git_status: `PASS_GIT_REMOTE_READ_AUTH`
- git_branch: `codex/live-oracle-dagger-phase-student`
- git_remote_read_auth_ok: `True`

The Colab check is read-only (`colab sessions` / `colab status`). The Git check is read-only (`git ls-remote`) and does not push.

## Preferred Colab GPU Command

Use this when a visible Colab GPU session is available:

```bash
python3 \
    tools/run_colab_cli_cuda_workflow.py \
    --workflow \
    phase2-z005-support \
    --session \
    open-duck-l4 \
    --candidate-name \
    phase2_z005_support_baseheight_cuda \
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

## Local ROCm Fallback Command

This is fallback/backend evidence only unless it clears the same post-training gates:

```bash
../envs/open-duck-playground/bin/python \
    tools/run_actuator_bridge_training_smoke.py \
    --playground-path \
    ../Open_Duck_Playground \
    --env-python \
    ../envs/open-duck-playground/bin/python \
    --output-root \
    outputs/phase2_domain_randomization/stage_z005_support_baseheight_local_rocm_safeenv_8env_81920 \
    --run \
    --platform \
    gpu \
    --local-rocm-safe-env \
    --timeout-s \
    2700 \
    --task \
    rough_terrain_backlash \
    --num-timesteps \
    81920 \
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
    0.000003 \
    --ppo-entropy-cost \
    0.001 \
    --ppo-clipping-epsilon \
    0.02 \
    --ppo-max-grad-norm \
    0.1 \
    --restore-policy-kl-scale \
    4 \
    --tracking-lin-vel-scale \
    3 \
    --tracking-sigma \
    0.01 \
    --forward-progress-scale \
    2.5 \
    --forward-wrong-direction-scale \
    -4 \
    --forward-wrong-direction-allowed-reverse-ratio \
    0.02 \
    --command-progress-scale \
    1.5 \
    --command-progress-shortfall-scale \
    -4 \
    --command-progress-required-ratio \
    0.45 \
    --command-progress-warmup-steps \
    30 \
    --action-rate-huber-delta \
    0.05 \
    --actuator-tracking-huber-delta \
    0.03 \
    --forward-swing-clearance-huber-delta \
    0.003 \
    --forward-swing-advance-huber-delta \
    0.002 \
    --action-rate-scale \
    -0.08 \
    --action-magnitude-scale \
    -0.005 \
    --base-height-scale \
    -0.8 \
    --forward-pitch-scale \
    -0.4 \
    --forward-pitch-rate-scale \
    -0.08 \
    --forward-contact-support-scale \
    -0.35 \
    --forward-contact-support-no-contact-weight \
    2.0 \
    --forward-contact-support-asymmetry-weight \
    0.25 \
    --forward-single-support-scale \
    0.1 \
    --forward-double-support-scale \
    -0.15 \
    --forward-double-support-dwell-scale \
    -0.25 \
    --forward-double-support-dwell-grace-steps \
    16 \
    --forward-swing-clearance-scale \
    -0.0005 \
    --forward-swing-clearance-target-m \
    0.018 \
    --forward-swing-advance-scale \
    -0.002 \
    --forward-swing-advance-target-m \
    0.004 \
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
    --push-interval-min-s \
    7 \
    --push-interval-max-s \
    12 \
    --push-magnitude-min \
    0.02 \
    --push-magnitude-max \
    0.1 \
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
    -0.01 \
    --terrain-hfield-z-scale \
    0.005
```

## Promotion Rule

Promotion still requires full corrected-bridge post-training gates, not a smoke pass:

- z=0.005 x=0.08 no-push, 8 seeds, 15s
- z=0.005 x=0.0 no-push, 8 seeds, 15s
- z=0.002 x=0.08 no-push, 8 seeds, 15s
- z=0.002 x=0.0 no-push, 8 seeds, 15s
- z=0.002 x=0.08 gentle-push, 8 seeds, 15s
- z=0.002 x=0.0 gentle-push, 8 seeds, 15s

No robot, SSH, deploy, grounded replay, or runtime behavior change is authorized by this plan.
