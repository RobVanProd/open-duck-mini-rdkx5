# Phase 2 z=0.0075 Post-Push Stability Next Recipe

status: `PASS_PHASE2_Z0075_POST_PUSH_STABILITY_RECIPE_READY`
stage: `stage_z0075_post_push_stability`
source_status: `HOLD_INTERMEDIATE_PUSH_ROBUSTNESS`
diagnosis_status: `HOLD_PHASE2_INTERMEDIATE_PUSH_ACTUATOR_ENVELOPE_EXCESS`

This is an offline planning artifact. It did not train, SSH, deploy, touch the robot, or run grounded replay.

## Inputs

- policy: `policy/candidates/phase2_z0075_iter21_early_lunge_gain095_rate150_20260704/candidate.onnx`
- policy_sha256: `72aa93c2ab249d2e9b22bb5415ef6c96c7407833fbfd21233892b6daa6afda14`
- corrected_bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- corrected_bridge_sha256: `3661543d0745073b561eb4fa2ae8f9616368ee8b72cb397f8b953dada532c8c0`
- restore_checkpoint: `outputs/analysis/phase2_limit198_ppo_loc_warmstart_step0_checkpoint`
- restore_checkpoint_present: `True`
- behavior_prior_enabled: `True`
- behavior_prior_mlp_npz: `outputs/analysis/phase2_z0075_iter21_early_lunge_gain095_rate150_candidate/candidate_mlp.npz`
- behavior_prior_sha256: `71f520712a10613d3e2304a33cbcd641f6bb59fb0d5c1dc3e34a5c8fe93569b2`
- behavior_prior_scale: `-0.22`
- behavior_prior_huber_delta: `0.06`
- behavior_prior_role: Frozen state-conditioned Iter21 teacher-action prior; this is used to preserve the behavior anchor because PPO step-0 compression was rejected.

## Measured Boundary

- strongest_confirmed_pass: `None`
- hold: `z=0.0075 terrain with intermediate push magnitude 0.075-0.125`
- duration_complete: `None`
- falls: `None`
- failed_seeds: `None`

## Failure Summary

| seed | classification | samples | last push tick | ticks to pitch>0.8 | ticks to height<0.08 | final pitch | final height | max excess joint | max excess |
|---:|---|---:|---:|---:|---:|---:|---:|---|---:|
| 1 | `ACTUATOR_ENVELOPE_EXCESS` | 750 | 714 | None | None | 0.2848 | 0.1584 | `right_ankle` | 0.0583 |
| 3 | `ACTUATOR_ENVELOPE_EXCESS` | 750 | 701 | None | None | 0.1040 | 0.1702 | `right_ankle` | 0.0097 |
| 5 | `PUSH_WINDOW_PITCHOVER` | 599 | 549 | -8 | 0 | -1.4099 | 0.0630 | `None` | 0.0000 |

## Recipe Intent

- Continue from the corrected-bridge PPO-compatible warm-start; do not train from scratch.
- Use the frozen Iter21 teacher-action behavior prior to preserve the gait; restore-policy KL alone failed to preserve forward progress in the A100 post-push run.
- Keep z=0.0075 rough terrain and intermediate push magnitude 0.075-0.125 as the target boundary.
- Preserve the reset-settle10 rough-terrain/no-push behavior as a regression gate.
- Remove the single-tick right-ankle envelope excesses without loosening the corrected actuator envelope.
- Extend push-recovery tracking beyond the old 25-tick/0.5s window because seed 5 pitches over inside the longer 1.2s recovery window.
- Add base-height, pitch, and pitch-rate pressure so push recovery is graded beyond immediate push success.

## Key Recipe Changes

- `terrain_hfield_z_scale`: `0.0075`
- `push_magnitude_min`: `0.075`
- `push_magnitude_max`: `0.125`
- `push_interval_s`: `[1.0, 1.5]`
- `push_recovery_tracking_window_steps`: `60`
- `push_recovery_tracking_joint_indices`: `2,3,4,11,12,13`
- `right_pitch_chain_indices`: `11,12,13`
- `push_recovery_actuator_tracking_scale`: `-0.025`
- `base_height_scale`: `-0.9`
- `forward_pitch_scale`: `-0.55`
- `forward_pitch_rate_scale`: `-0.12`
- `actuator_tracking_scale`: `-0.012`
- `restore_policy_kl_scale`: `4.5`
- `behavior_prior_scale`: `-0.22`
- `behavior_prior_huber_delta`: `0.06`
- `reset_settle_ticks_for_gates`: `10`
- `reset_mode_for_gates`: `home-support`

## Preferred A100 / Colab Command

```bash
python3 \
    tools/run_colab_cli_cuda_workflow.py \
    --workflow \
    phase2-b0g \
    --session \
    open-duck-phase2-a100 \
    --candidate-name \
    phase2_z0075_iter21_behavior_prior_post_push_recovery \
    --phase2-restore-checkpoint-path \
    outputs/analysis/phase2_limit198_ppo_loc_warmstart_step0_checkpoint \
    --phase2-terrain-hfield-z-scale \
    0.0075 \
    --phase2-num-timesteps \
    122880 \
    --phase2-ppo-num-envs \
    64 \
    --phase2-ppo-batch-size \
    512 \
    --candidate-checkpoint-sweep \
    --candidate-checkpoint-sweep-commands \
    0.0,0.08 \
    --candidate-checkpoint-sweep-duration \
    1.0 \
    --candidate-checkpoint-sweep-jax-platform \
    cpu \
    --candidate-timeout-s \
    10800 \
    --phase2-final-training-args-json \
    '["--terrain-hfield-z-scale", "0.0075", "--push-enable", "--push-interval-min-s", "1.0", "--push-interval-max-s", "1.5", "--push-magnitude-min", "0.075", "--push-magnitude-max", "0.125", "--push-recovery-actuator-tracking-scale", "-0.025", "--push-recovery-actuator-tracking-huber-delta", "0.03", "--push-recovery-tracking-window-steps", "60", "--push-recovery-tracking-joint-indices", "2,3,4,11,12,13", "--base-height-scale", "-0.9", "--forward-pitch-scale", "-0.55", "--forward-pitch-rate-scale", "-0.12", "--actuator-tracking-scale", "-0.012", "--restore-policy-kl-scale", "4.5", "--tracking-lin-vel-scale", "3", "--tracking-sigma", "0.01", "--forward-progress-scale", "2.8", "--command-progress-scale", "1.7", "--command-progress-shortfall-scale", "-4.5", "--command-progress-required-ratio", "0.45", "--action-rate-scale", "-0.07", "--action-magnitude-scale", "-0.004", "--lin-vel-x-min", "0.06", "--lin-vel-x-max", "0.1", "--lin-vel-y-min", "0", "--lin-vel-y-max", "0", "--ang-vel-yaw-min", "0", "--ang-vel-yaw-max", "0", "--zero-command-probability", "0.15", "--enable-behavior-prior", "--behavior-prior-mlp-npz", "outputs/analysis/phase2_z0075_iter21_early_lunge_gain095_rate150_candidate/candidate_mlp.npz", "--behavior-prior-scale", "-0.22", "--behavior-prior-huber-delta", "0.06"]' \
    --run
```

## Local ROCm Fallback Command

Use as backend evidence only unless it clears the same canonical CPU gates.

```bash
../envs/open-duck-playground/bin/python \
    tools/run_actuator_bridge_training_smoke.py \
    --playground-path \
    ../Open_Duck_Playground \
    --env-python \
    ../envs/open-duck-playground/bin/python \
    --output-root \
    outputs/phase2_domain_randomization/stage_z0075_post_push_stability_local_rocm \
    --run \
    --platform \
    gpu \
    --local-rocm-safe-env \
    --timeout-s \
    7200 \
    --task \
    rough_terrain_backlash \
    --num-timesteps \
    122880 \
    --export-min-step \
    1 \
    --ppo-num-envs \
    16 \
    --ppo-num-evals \
    4 \
    --ppo-episode-length \
    750 \
    --ppo-unroll-length \
    20 \
    --ppo-batch-size \
    128 \
    --ppo-num-minibatches \
    1 \
    --ppo-num-updates-per-batch \
    2 \
    --restore-checkpoint-path \
    outputs/analysis/phase2_limit198_ppo_loc_warmstart_step0_checkpoint \
    --terrain-hfield-z-scale \
    0.0075 \
    --push-enable \
    --push-interval-min-s \
    1.0 \
    --push-interval-max-s \
    1.5 \
    --push-magnitude-min \
    0.075 \
    --push-magnitude-max \
    0.125 \
    --push-recovery-actuator-tracking-scale \
    -0.025 \
    --push-recovery-actuator-tracking-huber-delta \
    0.03 \
    --push-recovery-tracking-window-steps \
    60 \
    --push-recovery-tracking-joint-indices \
    2,3,4,11,12,13 \
    --base-height-scale \
    -0.9 \
    --forward-pitch-scale \
    -0.55 \
    --forward-pitch-rate-scale \
    -0.12 \
    --actuator-tracking-scale \
    -0.012 \
    --restore-policy-kl-scale \
    4.5 \
    --tracking-lin-vel-scale \
    3 \
    --tracking-sigma \
    0.01 \
    --forward-progress-scale \
    2.8 \
    --command-progress-scale \
    1.7 \
    --command-progress-shortfall-scale \
    -4.5 \
    --command-progress-required-ratio \
    0.45 \
    --action-rate-scale \
    -0.07 \
    --action-magnitude-scale \
    -0.004 \
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
    --zero-command-probability \
    0.15 \
    --enable-behavior-prior \
    --behavior-prior-mlp-npz \
    outputs/analysis/phase2_z0075_iter21_early_lunge_gain095_rate150_candidate/candidate_mlp.npz \
    --behavior-prior-scale \
    -0.22 \
    --behavior-prior-huber-delta \
    0.06
```

## Post-Training Gate Commands

### z0075_x008_no_push

```bash
../envs/open-duck-playground/bin/python \
    tools/run_candidate_seed_sweep.py \
    --policies \
    '<candidate.onnx>' \
    --fit-json \
    outputs/analysis/actuator_response_fit_corrected_knee.json \
    --playground-path \
    ../Open_Duck_Playground \
    --env-python \
    ../envs/open-duck-playground/bin/python \
    --task \
    rough_terrain_backlash \
    --command-x \
    0.08 \
    --duration \
    15 \
    --bridge-mode \
    fitted \
    --jax-platform \
    cpu \
    --seeds \
    0,1,2,3,4,5,6,7 \
    --terrain-hfield-z-scale \
    0.0075 \
    --reset-settle-ticks \
    10 \
    --reset-mode \
    home-support \
    --output-md \
    outputs/analysis/PHASE2_Z0075_POST_PUSH_STABILITY_Z0075_X008_NO_PUSH.md \
    --output-json \
    outputs/analysis/PHASE2_Z0075_POST_PUSH_STABILITY_Z0075_X008_NO_PUSH.json \
    --run
```

### z0075_x000_no_push

```bash
../envs/open-duck-playground/bin/python \
    tools/run_candidate_seed_sweep.py \
    --policies \
    '<candidate.onnx>' \
    --fit-json \
    outputs/analysis/actuator_response_fit_corrected_knee.json \
    --playground-path \
    ../Open_Duck_Playground \
    --env-python \
    ../envs/open-duck-playground/bin/python \
    --task \
    rough_terrain_backlash \
    --command-x \
    0.0 \
    --duration \
    15 \
    --bridge-mode \
    fitted \
    --jax-platform \
    cpu \
    --seeds \
    0,1,2,3,4,5,6,7 \
    --terrain-hfield-z-scale \
    0.0075 \
    --reset-settle-ticks \
    10 \
    --reset-mode \
    home-support \
    --output-md \
    outputs/analysis/PHASE2_Z0075_POST_PUSH_STABILITY_Z0075_X000_NO_PUSH.md \
    --output-json \
    outputs/analysis/PHASE2_Z0075_POST_PUSH_STABILITY_Z0075_X000_NO_PUSH.json \
    --run
```

### z0075_x008_gentle_push

```bash
../envs/open-duck-playground/bin/python \
    tools/run_candidate_seed_sweep.py \
    --policies \
    '<candidate.onnx>' \
    --fit-json \
    outputs/analysis/actuator_response_fit_corrected_knee.json \
    --playground-path \
    ../Open_Duck_Playground \
    --env-python \
    ../envs/open-duck-playground/bin/python \
    --task \
    rough_terrain_backlash \
    --command-x \
    0.08 \
    --duration \
    15 \
    --bridge-mode \
    fitted \
    --jax-platform \
    cpu \
    --seeds \
    0,1,2,3,4,5,6,7 \
    --terrain-hfield-z-scale \
    0.0075 \
    --reset-settle-ticks \
    10 \
    --reset-mode \
    home-support \
    --output-md \
    outputs/analysis/PHASE2_Z0075_POST_PUSH_STABILITY_Z0075_X008_GENTLE_PUSH.md \
    --output-json \
    outputs/analysis/PHASE2_Z0075_POST_PUSH_STABILITY_Z0075_X008_GENTLE_PUSH.json \
    --eval-push-enable \
    --eval-push-interval-min-s \
    1.0 \
    --eval-push-interval-max-s \
    1.5 \
    --eval-push-magnitude-min \
    0.05 \
    --eval-push-magnitude-max \
    0.1 \
    --push-recovery-window-s \
    1.2 \
    --push-recovery-max-abs-pitch-rad \
    0.8 \
    --push-recovery-min-base-height-m \
    0.08 \
    --run
```

### z0075_x000_gentle_push

```bash
../envs/open-duck-playground/bin/python \
    tools/run_candidate_seed_sweep.py \
    --policies \
    '<candidate.onnx>' \
    --fit-json \
    outputs/analysis/actuator_response_fit_corrected_knee.json \
    --playground-path \
    ../Open_Duck_Playground \
    --env-python \
    ../envs/open-duck-playground/bin/python \
    --task \
    rough_terrain_backlash \
    --command-x \
    0.0 \
    --duration \
    15 \
    --bridge-mode \
    fitted \
    --jax-platform \
    cpu \
    --seeds \
    0,1,2,3,4,5,6,7 \
    --terrain-hfield-z-scale \
    0.0075 \
    --reset-settle-ticks \
    10 \
    --reset-mode \
    home-support \
    --output-md \
    outputs/analysis/PHASE2_Z0075_POST_PUSH_STABILITY_Z0075_X000_GENTLE_PUSH.md \
    --output-json \
    outputs/analysis/PHASE2_Z0075_POST_PUSH_STABILITY_Z0075_X000_GENTLE_PUSH.json \
    --eval-push-enable \
    --eval-push-interval-min-s \
    1.0 \
    --eval-push-interval-max-s \
    1.5 \
    --eval-push-magnitude-min \
    0.05 \
    --eval-push-magnitude-max \
    0.1 \
    --push-recovery-window-s \
    1.2 \
    --push-recovery-max-abs-pitch-rad \
    0.8 \
    --push-recovery-min-base-height-m \
    0.08 \
    --run
```

### z0075_x008_intermediate_push

```bash
../envs/open-duck-playground/bin/python \
    tools/run_candidate_seed_sweep.py \
    --policies \
    '<candidate.onnx>' \
    --fit-json \
    outputs/analysis/actuator_response_fit_corrected_knee.json \
    --playground-path \
    ../Open_Duck_Playground \
    --env-python \
    ../envs/open-duck-playground/bin/python \
    --task \
    rough_terrain_backlash \
    --command-x \
    0.08 \
    --duration \
    15 \
    --bridge-mode \
    fitted \
    --jax-platform \
    cpu \
    --seeds \
    0,1,2,3,4,5,6,7 \
    --terrain-hfield-z-scale \
    0.0075 \
    --reset-settle-ticks \
    10 \
    --reset-mode \
    home-support \
    --output-md \
    outputs/analysis/PHASE2_Z0075_POST_PUSH_STABILITY_Z0075_X008_INTERMEDIATE_PUSH.md \
    --output-json \
    outputs/analysis/PHASE2_Z0075_POST_PUSH_STABILITY_Z0075_X008_INTERMEDIATE_PUSH.json \
    --eval-push-enable \
    --eval-push-interval-min-s \
    1.0 \
    --eval-push-interval-max-s \
    1.5 \
    --eval-push-magnitude-min \
    0.075 \
    --eval-push-magnitude-max \
    0.125 \
    --push-recovery-window-s \
    1.2 \
    --push-recovery-max-abs-pitch-rad \
    0.8 \
    --push-recovery-min-base-height-m \
    0.08 \
    --run
```

### z0075_x000_intermediate_push

```bash
../envs/open-duck-playground/bin/python \
    tools/run_candidate_seed_sweep.py \
    --policies \
    '<candidate.onnx>' \
    --fit-json \
    outputs/analysis/actuator_response_fit_corrected_knee.json \
    --playground-path \
    ../Open_Duck_Playground \
    --env-python \
    ../envs/open-duck-playground/bin/python \
    --task \
    rough_terrain_backlash \
    --command-x \
    0.0 \
    --duration \
    15 \
    --bridge-mode \
    fitted \
    --jax-platform \
    cpu \
    --seeds \
    0,1,2,3,4,5,6,7 \
    --terrain-hfield-z-scale \
    0.0075 \
    --reset-settle-ticks \
    10 \
    --reset-mode \
    home-support \
    --output-md \
    outputs/analysis/PHASE2_Z0075_POST_PUSH_STABILITY_Z0075_X000_INTERMEDIATE_PUSH.md \
    --output-json \
    outputs/analysis/PHASE2_Z0075_POST_PUSH_STABILITY_Z0075_X000_INTERMEDIATE_PUSH.json \
    --eval-push-enable \
    --eval-push-interval-min-s \
    1.0 \
    --eval-push-interval-max-s \
    1.5 \
    --eval-push-magnitude-min \
    0.075 \
    --eval-push-magnitude-max \
    0.125 \
    --push-recovery-window-s \
    1.2 \
    --push-recovery-max-abs-pitch-rad \
    0.8 \
    --push-recovery-min-base-height-m \
    0.08 \
    --run
```

## Acceptance

- z=0.0075 x=0.08 intermediate push 0.075-0.125 passes 8/8 with zero falls.
- z=0.0075 x=0.0 intermediate push preserves command semantics and does not drift.
- z=0.0075 gentle-push regression remains 8/8 at x=0.08 and x=0.0.
- Corrected per-joint actuator envelope remains authoritative: p95 velocity excess is zero and instantaneous excess is reviewed rather than ignored.
- Tracking p95 remains at or below the corrected-bridge gate threshold used by the rate150 candidate.

## Falsifier

If seed 5 still pitches over under intermediate push while the right-ankle single-tick excesses are removed, stop increasing push magnitude and collect on-policy post-push recovery labels instead of loosening limits.
