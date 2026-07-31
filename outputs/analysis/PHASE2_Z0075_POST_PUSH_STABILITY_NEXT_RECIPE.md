# Phase 2 z=0.0075 Post-Push Stability Next Recipe

status: `PASS_PHASE2_Z0075_POST_PUSH_STABILITY_RECIPE_READY`
stage: `stage_z0075_post_push_stability`
source_status: `HOLD_PHASE2_Z0075_INTERMEDIATE_PUSH_STABILITY`
diagnosis_status: `HOLD_PHASE2_INTERMEDIATE_PUSH_POST_RECOVERY_PITCHOVER`

This is an offline planning artifact. It did not train, SSH, deploy, touch the robot, or run grounded replay.

## Inputs

- policy: `policy/candidates/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_rate150_20260703/candidate.onnx`
- policy_sha256: `e2281adeedd2fa4b0d416fecee17bb960275457a81538cb3f98fe57d0e54eb18`
- corrected_bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- corrected_bridge_sha256: `3661543d0745073b561eb4fa2ae8f9616368ee8b72cb397f8b953dada532c8c0`
- restore_checkpoint: `outputs/analysis/phase2_limit198_ppo_loc_warmstart_step0_checkpoint`
- restore_checkpoint_present: `True`

## Measured Boundary

- strongest_confirmed_pass: `z=0.0075 terrain with gentle push magnitude 0.05-0.10`
- hold: `z=0.0075 terrain with intermediate push magnitude 0.075-0.125`
- duration_complete: `6`
- falls: `2`
- failed_seeds: `[0, 7]`

## Failure Summary

| seed | classification | samples | last push tick | ticks to pitch>0.8 | ticks to height<0.08 | final pitch | final height | max excess joint | max excess |
|---:|---|---:|---:|---:|---:|---:|---:|---|---:|
| 0 | `POST_PUSH_DELAYED_PITCHOVER` | 181 | 121 | 26 | 31 | 1.4907 | 0.0094 | `right_hip_pitch` | 1.3268 |
| 7 | `POST_PUSH_DELAYED_PITCHOVER` | 550 | 503 | 14 | 18 | 1.5294 | 0.0201 | `right_hip_pitch` | 0.4477 |

## Recipe Intent

- Continue from the corrected-bridge PPO-compatible warm-start; do not train from scratch.
- Keep z=0.0075 rough terrain and intermediate push magnitude 0.075-0.125 as the target boundary.
- Preserve the already-confirmed z=0.0075 gentle-push pass as a regression gate.
- Extend push-recovery tracking beyond the old 25-tick/0.5s window because failures occur after that window closes.
- Target the pitch chain, including the right hip/knee/ankle excursions seen in seeds 0 and 7, without loosening the corrected actuator envelope.
- Add base-height, pitch, and pitch-rate pressure so post-push recovery is graded beyond immediate push success.

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

## Preferred A100 / Colab Command

```bash
python3 \
    tools/run_colab_cli_cuda_workflow.py \
    --workflow \
    phase2-b0g \
    --session \
    open-duck-phase2-a100 \
    --candidate-name \
    phase2_z0075_post_push_stability_cuda \
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
    '["--terrain-hfield-z-scale", "0.0075", "--push-enable", "--push-interval-min-s", "1.0", "--push-interval-max-s", "1.5", "--push-magnitude-min", "0.075", "--push-magnitude-max", "0.125", "--push-recovery-actuator-tracking-scale", "-0.025", "--push-recovery-actuator-tracking-huber-delta", "0.03", "--push-recovery-tracking-window-steps", "60", "--push-recovery-tracking-joint-indices", "2,3,4,11,12,13", "--base-height-scale", "-0.9", "--forward-pitch-scale", "-0.55", "--forward-pitch-rate-scale", "-0.12", "--actuator-tracking-scale", "-0.012", "--restore-policy-kl-scale", "4.5", "--tracking-lin-vel-scale", "3", "--tracking-sigma", "0.01", "--forward-progress-scale", "2.8", "--command-progress-scale", "1.7", "--command-progress-shortfall-scale", "-4.5", "--command-progress-required-ratio", "0.45", "--action-rate-scale", "-0.07", "--action-magnitude-scale", "-0.004", "--lin-vel-x-min", "0.06", "--lin-vel-x-max", "0.1", "--lin-vel-y-min", "0", "--lin-vel-y-max", "0", "--ang-vel-yaw-min", "0", "--ang-vel-yaw-max", "0", "--zero-command-probability", "0.15"]' \
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
    0.15
```

## Post-Training Gate Commands

### z0075_x008_no_push

```bash
../envs/open-duck-playground/bin/python \
    tools/run_candidate_seed_sweep.py \
    --policy \
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
    --seeds \
    0,1,2,3,4,5,6,7 \
    --terrain-hfield-z-scale \
    0.0075 \
    --output-md \
    outputs/analysis/PHASE2_Z0075_POST_PUSH_STABILITY_Z0075_X008_NO_PUSH.md \
    --output-json \
    outputs/analysis/PHASE2_Z0075_POST_PUSH_STABILITY_Z0075_X008_NO_PUSH.json
```

### z0075_x000_no_push

```bash
../envs/open-duck-playground/bin/python \
    tools/run_candidate_seed_sweep.py \
    --policy \
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
    --seeds \
    0,1,2,3,4,5,6,7 \
    --terrain-hfield-z-scale \
    0.0075 \
    --output-md \
    outputs/analysis/PHASE2_Z0075_POST_PUSH_STABILITY_Z0075_X000_NO_PUSH.md \
    --output-json \
    outputs/analysis/PHASE2_Z0075_POST_PUSH_STABILITY_Z0075_X000_NO_PUSH.json
```

### z0075_x008_gentle_push

```bash
../envs/open-duck-playground/bin/python \
    tools/run_candidate_seed_sweep.py \
    --policy \
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
    --seeds \
    0,1,2,3,4,5,6,7 \
    --terrain-hfield-z-scale \
    0.0075 \
    --output-md \
    outputs/analysis/PHASE2_Z0075_POST_PUSH_STABILITY_Z0075_X008_GENTLE_PUSH.md \
    --output-json \
    outputs/analysis/PHASE2_Z0075_POST_PUSH_STABILITY_Z0075_X008_GENTLE_PUSH.json \
    --eval-push-enable \
    --eval-push-magnitude-min \
    0.05 \
    --eval-push-magnitude-max \
    0.1 \
    --push-recovery-window-s \
    0.5
```

### z0075_x000_gentle_push

```bash
../envs/open-duck-playground/bin/python \
    tools/run_candidate_seed_sweep.py \
    --policy \
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
    --seeds \
    0,1,2,3,4,5,6,7 \
    --terrain-hfield-z-scale \
    0.0075 \
    --output-md \
    outputs/analysis/PHASE2_Z0075_POST_PUSH_STABILITY_Z0075_X000_GENTLE_PUSH.md \
    --output-json \
    outputs/analysis/PHASE2_Z0075_POST_PUSH_STABILITY_Z0075_X000_GENTLE_PUSH.json \
    --eval-push-enable \
    --eval-push-magnitude-min \
    0.05 \
    --eval-push-magnitude-max \
    0.1 \
    --push-recovery-window-s \
    0.5
```

### z0075_x008_intermediate_push

```bash
../envs/open-duck-playground/bin/python \
    tools/run_candidate_seed_sweep.py \
    --policy \
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
    --seeds \
    0,1,2,3,4,5,6,7 \
    --terrain-hfield-z-scale \
    0.0075 \
    --output-md \
    outputs/analysis/PHASE2_Z0075_POST_PUSH_STABILITY_Z0075_X008_INTERMEDIATE_PUSH.md \
    --output-json \
    outputs/analysis/PHASE2_Z0075_POST_PUSH_STABILITY_Z0075_X008_INTERMEDIATE_PUSH.json \
    --eval-push-enable \
    --eval-push-magnitude-min \
    0.075 \
    --eval-push-magnitude-max \
    0.125 \
    --push-recovery-window-s \
    0.5
```

### z0075_x000_intermediate_push

```bash
../envs/open-duck-playground/bin/python \
    tools/run_candidate_seed_sweep.py \
    --policy \
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
    --seeds \
    0,1,2,3,4,5,6,7 \
    --terrain-hfield-z-scale \
    0.0075 \
    --output-md \
    outputs/analysis/PHASE2_Z0075_POST_PUSH_STABILITY_Z0075_X000_INTERMEDIATE_PUSH.md \
    --output-json \
    outputs/analysis/PHASE2_Z0075_POST_PUSH_STABILITY_Z0075_X000_INTERMEDIATE_PUSH.json \
    --eval-push-enable \
    --eval-push-magnitude-min \
    0.075 \
    --eval-push-magnitude-max \
    0.125 \
    --push-recovery-window-s \
    0.5
```

## Acceptance

- z=0.0075 x=0.08 intermediate push 0.075-0.125 passes 8/8 with zero falls.
- z=0.0075 x=0.0 intermediate push preserves command semantics and does not drift.
- z=0.0075 gentle-push regression remains 8/8 at x=0.08 and x=0.0.
- Corrected per-joint actuator envelope remains authoritative: p95 velocity excess is zero and instantaneous excess is reviewed rather than ignored.
- Tracking p95 remains at or below the corrected-bridge gate threshold used by the rate150 candidate.

## Falsifier

If seeds 0/7 still pitch over after push windows while p95 envelope remains clean, stop increasing push magnitude and collect on-policy post-push recovery labels instead of loosening limits.
