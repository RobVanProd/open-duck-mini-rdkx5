# Phase 2 Domain-Randomized Robustness Plan

status: `READY_DRY_RUN`
warmstart_status: `PASS_TRAINABLE_WARMSTART`

Verified trainable step-0 checkpoint exists; generated commands remain dry-run until invoked explicitly.

This plan is offline-only. It does not SSH, deploy, move the robot, or
start training by itself.

## Locked Inputs

- policy: `/home/lsd/robots/open-duck-mini-rdkx5/policy/candidates/corrected_bridge_cmd_conditioned_rate175_20260627/candidate.onnx`
- policy_sha256: `63506567f7a973be0ff6b2b222bba41736409da713466db442067c0f2a91415e`
- corrected_bridge: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/actuator_response_fit_corrected_knee.json`
- corrected_bridge_sha256: `3661543d0745073b561eb4fa2ae8f9616368ee8b72cb397f8b953dada532c8c0`
- behavior_prior_mlp_npz: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_candidate/candidate_mlp.npz`
- behavior_prior_mlp_npz_sha256: `312f1ef0ba758af5fdeae900ce0a34dab659fe348a9f389988ddaaaa15659497`
- restore_checkpoint: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/ppo_bc_command_conditioned_rate175_step0_checkpoint`
- restore_checkpoint_exists: `True`
- warmstart_fidelity: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/ppo_bc_command_conditioned_rate175_step0_export_fidelity.json`
- warmstart_fidelity_status: `PASS_PPO_BC_WARMSTART_STEP0_EXPORT_FIDELITY`
- warmstart_fidelity_p95_abs_error: `1.1920928955078125e-07`
- warmstart_fidelity_max_abs_error: `3.2782554626464844e-07`

## Blocking Warm-Start Note

The Phase 1 candidate now has a verified PPO step-0 Orbax checkpoint.
It was constructed from the rate175 BC NPZ and passed ONNX action
fidelity against the packaged Phase 1 candidate before PPO updates.
Use this checkpoint for Phase 2; do not launch a scratch PPO run.

## Stages

| stage | task | friction | mass | COM | push | bridge velocity | purpose |
|---|---|---|---|---|---|---|---|
| `stage_a_narrow_flat_no_push` | `flat_terrain_backlash` | `[0.7, 1.0]` | `[0.97, 1.03]` | `[-0.015, 0.015]` | `{'enabled': False, 'interval_s': [8.0, 12.0], 'magnitude': [0.0, 0.0]}` | `[2.0, 3.25]` | preserve Phase 1 gait under weak randomization on flat terrain |
| `stage_b_full_flat_gentle_push` | `flat_terrain_backlash` | `[0.5, 1.25]` | `[0.9, 1.1]` | `[-0.03, 0.03]` | `{'enabled': True, 'interval_s': [6.0, 10.0], 'magnitude': [0.05, 0.25]}` | `[2.0, 3.25]` | full physics randomization on flat terrain with gentle push perturbations |
| `stage_c_rough_gentle_push` | `rough_terrain_backlash` | `[0.5, 1.25]` | `[0.9, 1.1]` | `[-0.03, 0.03]` | `{'enabled': True, 'interval_s': [5.0, 9.0], 'magnitude': [0.05, 0.35]}` | `[2.0, 3.25]` | introduce existing rough hfield terrain after flat robustness passes |
| `stage_d_rough_stronger_push` | `rough_terrain_backlash` | `[0.5, 1.25]` | `[0.9, 1.1]` | `[-0.04, 0.04]` | `{'enabled': True, 'interval_s': [4.0, 8.0], 'magnitude': [0.1, 0.6]}` | `[2.0, 3.25]` | final robustness stage with stronger perturbations, still in corrected envelope |

## Commands

### stage_a_narrow_flat_no_push

```bash
/home/lsd/robots/envs/open-duck-playground/bin/python /home/lsd/robots/open-duck-mini-rdkx5/tools/run_actuator_bridge_training_smoke.py --playground-path /home/lsd/robots/Open_Duck_Playground --env-python /home/lsd/robots/envs/open-duck-playground/bin/python --output-root outputs/phase2_domain_randomization/stage_a_narrow_flat_no_push --platform gpu --task flat_terrain_backlash --num-timesteps 1000000 --export-min-step 100000 --ppo-num-envs 512 --ppo-num-evals 8 --ppo-episode-length 750 --ppo-unroll-length 20 --ppo-batch-size 4096 --ppo-num-minibatches 8 --ppo-num-updates-per-batch 4 --enable-behavior-prior --behavior-prior-mlp-npz /home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_candidate/candidate_mlp.npz --behavior-prior-scale -0.08 --actuator-bridge-delay-min-ticks 3 --actuator-bridge-delay-max-ticks 4 --actuator-bridge-tau-min-s 0.06 --actuator-bridge-tau-max-s 0.1 --actuator-bridge-velocity-limit-min-rad-s 2 --actuator-bridge-velocity-limit-max-rad-s 3.25 --actuator-bridge-per-joint-variation 0.05 --lin-vel-x-min 0.06 --lin-vel-x-max 0.10 --lin-vel-y-min 0.0 --lin-vel-y-max 0.0 --ang-vel-yaw-min 0.0 --ang-vel-yaw-max 0.0 --zero-command-probability 0.15 --command-resample-steps 600 --dr-friction-min 0.7 --dr-friction-max 1 --dr-frictionloss-scale-min 0.97 --dr-frictionloss-scale-max 1.03 --dr-armature-scale-min 1 --dr-armature-scale-max 1.03 --dr-com-jitter-m 0.015 --dr-mass-scale-min 0.97 --dr-mass-scale-max 1.03 --dr-torso-mass-delta-min -0.03 --dr-torso-mass-delta-max 0.03 --dr-qpos-jitter-rad 0.01 --dr-actuator-gain-scale-min 0.97 --dr-actuator-gain-scale-max 1.03 --dr-leg-geometry-jitter-scale 0.005 --push-interval-min-s 8 --push-interval-max-s 12 --push-magnitude-min 0 --push-magnitude-max 0 --noise-level 0.5 --noise-hip-pos 0.01 --noise-knee-pos 0.01 --noise-ankle-pos 0.01 --noise-joint-vel 1 --noise-gravity 0.05 --noise-gyro 0.05 --noise-accelerometer 0.025 --target-rate-scale -0.04 --target-rate-huber-delta 0.08 --actuator-tracking-scale -0.03 --actuator-tracking-huber-delta 0.04 --action-rate-scale -0.12 --action-rate-huber-delta 0.05 --action-magnitude-scale -0.01 --forward-progress-scale 2.0 --command-progress-scale 1.0 --command-progress-shortfall-scale -2.0 --command-progress-required-ratio 0.35 --command-progress-warmup-steps 30 --forward-pitch-scale -0.4 --forward-pitch-rate-scale -0.08 --base-height-scale -0.3 --imitation-scale 0.0 --alive-scale 2.0 --restore-checkpoint-path /home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/ppo_bc_command_conditioned_rate175_step0_checkpoint --restore-policy-kl-scale 0.05 --no-push-enable --jax-platforms cuda
```

### stage_b_full_flat_gentle_push

```bash
/home/lsd/robots/envs/open-duck-playground/bin/python /home/lsd/robots/open-duck-mini-rdkx5/tools/run_actuator_bridge_training_smoke.py --playground-path /home/lsd/robots/Open_Duck_Playground --env-python /home/lsd/robots/envs/open-duck-playground/bin/python --output-root outputs/phase2_domain_randomization/stage_b_full_flat_gentle_push --platform gpu --task flat_terrain_backlash --num-timesteps 1000000 --export-min-step 100000 --ppo-num-envs 512 --ppo-num-evals 8 --ppo-episode-length 750 --ppo-unroll-length 20 --ppo-batch-size 4096 --ppo-num-minibatches 8 --ppo-num-updates-per-batch 4 --enable-behavior-prior --behavior-prior-mlp-npz /home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_candidate/candidate_mlp.npz --behavior-prior-scale -0.06 --actuator-bridge-delay-min-ticks 3 --actuator-bridge-delay-max-ticks 5 --actuator-bridge-tau-min-s 0.06 --actuator-bridge-tau-max-s 0.14 --actuator-bridge-velocity-limit-min-rad-s 2 --actuator-bridge-velocity-limit-max-rad-s 3.25 --actuator-bridge-per-joint-variation 0.1 --lin-vel-x-min 0.06 --lin-vel-x-max 0.10 --lin-vel-y-min 0.0 --lin-vel-y-max 0.0 --ang-vel-yaw-min 0.0 --ang-vel-yaw-max 0.0 --zero-command-probability 0.15 --command-resample-steps 600 --dr-friction-min 0.5 --dr-friction-max 1.25 --dr-frictionloss-scale-min 0.9 --dr-frictionloss-scale-max 1.1 --dr-armature-scale-min 0.98 --dr-armature-scale-max 1.08 --dr-com-jitter-m 0.03 --dr-mass-scale-min 0.9 --dr-mass-scale-max 1.1 --dr-torso-mass-delta-min -0.08 --dr-torso-mass-delta-max 0.08 --dr-qpos-jitter-rad 0.02 --dr-actuator-gain-scale-min 0.9 --dr-actuator-gain-scale-max 1.1 --dr-leg-geometry-jitter-scale 0.015 --push-interval-min-s 6 --push-interval-max-s 10 --push-magnitude-min 0.05 --push-magnitude-max 0.25 --noise-level 1 --noise-hip-pos 0.01 --noise-knee-pos 0.01 --noise-ankle-pos 0.01 --noise-joint-vel 1.5 --noise-gravity 0.08 --noise-gyro 0.08 --noise-accelerometer 0.04 --target-rate-scale -0.04 --target-rate-huber-delta 0.08 --actuator-tracking-scale -0.03 --actuator-tracking-huber-delta 0.04 --action-rate-scale -0.12 --action-rate-huber-delta 0.05 --action-magnitude-scale -0.01 --forward-progress-scale 2.0 --command-progress-scale 1.0 --command-progress-shortfall-scale -2.0 --command-progress-required-ratio 0.35 --command-progress-warmup-steps 30 --forward-pitch-scale -0.4 --forward-pitch-rate-scale -0.08 --base-height-scale -0.3 --imitation-scale 0.0 --alive-scale 2.0 --restore-checkpoint-path /home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/ppo_bc_command_conditioned_rate175_step0_checkpoint --restore-policy-kl-scale 0.03 --push-enable --jax-platforms cuda
```

### stage_c_rough_gentle_push

```bash
/home/lsd/robots/envs/open-duck-playground/bin/python /home/lsd/robots/open-duck-mini-rdkx5/tools/run_actuator_bridge_training_smoke.py --playground-path /home/lsd/robots/Open_Duck_Playground --env-python /home/lsd/robots/envs/open-duck-playground/bin/python --output-root outputs/phase2_domain_randomization/stage_c_rough_gentle_push --platform gpu --task rough_terrain_backlash --num-timesteps 1000000 --export-min-step 100000 --ppo-num-envs 512 --ppo-num-evals 8 --ppo-episode-length 750 --ppo-unroll-length 20 --ppo-batch-size 4096 --ppo-num-minibatches 8 --ppo-num-updates-per-batch 4 --enable-behavior-prior --behavior-prior-mlp-npz /home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_candidate/candidate_mlp.npz --behavior-prior-scale -0.05 --actuator-bridge-delay-min-ticks 3 --actuator-bridge-delay-max-ticks 5 --actuator-bridge-tau-min-s 0.06 --actuator-bridge-tau-max-s 0.14 --actuator-bridge-velocity-limit-min-rad-s 2 --actuator-bridge-velocity-limit-max-rad-s 3.25 --actuator-bridge-per-joint-variation 0.1 --lin-vel-x-min 0.06 --lin-vel-x-max 0.10 --lin-vel-y-min 0.0 --lin-vel-y-max 0.0 --ang-vel-yaw-min 0.0 --ang-vel-yaw-max 0.0 --zero-command-probability 0.15 --command-resample-steps 600 --dr-friction-min 0.5 --dr-friction-max 1.25 --dr-frictionloss-scale-min 0.9 --dr-frictionloss-scale-max 1.1 --dr-armature-scale-min 0.98 --dr-armature-scale-max 1.08 --dr-com-jitter-m 0.03 --dr-mass-scale-min 0.9 --dr-mass-scale-max 1.1 --dr-torso-mass-delta-min -0.08 --dr-torso-mass-delta-max 0.08 --dr-qpos-jitter-rad 0.02 --dr-actuator-gain-scale-min 0.9 --dr-actuator-gain-scale-max 1.1 --dr-leg-geometry-jitter-scale 0.02 --push-interval-min-s 5 --push-interval-max-s 9 --push-magnitude-min 0.05 --push-magnitude-max 0.35 --noise-level 1 --noise-hip-pos 0.01 --noise-knee-pos 0.01 --noise-ankle-pos 0.01 --noise-joint-vel 1.5 --noise-gravity 0.08 --noise-gyro 0.08 --noise-accelerometer 0.04 --target-rate-scale -0.04 --target-rate-huber-delta 0.08 --actuator-tracking-scale -0.03 --actuator-tracking-huber-delta 0.04 --action-rate-scale -0.12 --action-rate-huber-delta 0.05 --action-magnitude-scale -0.01 --forward-progress-scale 2.0 --command-progress-scale 1.0 --command-progress-shortfall-scale -2.0 --command-progress-required-ratio 0.35 --command-progress-warmup-steps 30 --forward-pitch-scale -0.4 --forward-pitch-rate-scale -0.08 --base-height-scale -0.3 --imitation-scale 0.0 --alive-scale 2.0 --restore-checkpoint-path /home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/ppo_bc_command_conditioned_rate175_step0_checkpoint --restore-policy-kl-scale 0.02 --push-enable --jax-platforms cuda
```

### stage_d_rough_stronger_push

```bash
/home/lsd/robots/envs/open-duck-playground/bin/python /home/lsd/robots/open-duck-mini-rdkx5/tools/run_actuator_bridge_training_smoke.py --playground-path /home/lsd/robots/Open_Duck_Playground --env-python /home/lsd/robots/envs/open-duck-playground/bin/python --output-root outputs/phase2_domain_randomization/stage_d_rough_stronger_push --platform gpu --task rough_terrain_backlash --num-timesteps 1000000 --export-min-step 100000 --ppo-num-envs 512 --ppo-num-evals 8 --ppo-episode-length 750 --ppo-unroll-length 20 --ppo-batch-size 4096 --ppo-num-minibatches 8 --ppo-num-updates-per-batch 4 --enable-behavior-prior --behavior-prior-mlp-npz /home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_candidate/candidate_mlp.npz --behavior-prior-scale -0.04 --actuator-bridge-delay-min-ticks 3 --actuator-bridge-delay-max-ticks 6 --actuator-bridge-tau-min-s 0.06 --actuator-bridge-tau-max-s 0.14 --actuator-bridge-velocity-limit-min-rad-s 2 --actuator-bridge-velocity-limit-max-rad-s 3.25 --actuator-bridge-per-joint-variation 0.12 --lin-vel-x-min 0.06 --lin-vel-x-max 0.10 --lin-vel-y-min 0.0 --lin-vel-y-max 0.0 --ang-vel-yaw-min 0.0 --ang-vel-yaw-max 0.0 --zero-command-probability 0.15 --command-resample-steps 600 --dr-friction-min 0.5 --dr-friction-max 1.25 --dr-frictionloss-scale-min 0.9 --dr-frictionloss-scale-max 1.1 --dr-armature-scale-min 0.98 --dr-armature-scale-max 1.1 --dr-com-jitter-m 0.04 --dr-mass-scale-min 0.9 --dr-mass-scale-max 1.1 --dr-torso-mass-delta-min -0.1 --dr-torso-mass-delta-max 0.1 --dr-qpos-jitter-rad 0.025 --dr-actuator-gain-scale-min 0.9 --dr-actuator-gain-scale-max 1.1 --dr-leg-geometry-jitter-scale 0.025 --push-interval-min-s 4 --push-interval-max-s 8 --push-magnitude-min 0.1 --push-magnitude-max 0.6 --noise-level 1 --noise-hip-pos 0.01 --noise-knee-pos 0.01 --noise-ankle-pos 0.01 --noise-joint-vel 1.5 --noise-gravity 0.1 --noise-gyro 0.1 --noise-accelerometer 0.05 --target-rate-scale -0.04 --target-rate-huber-delta 0.08 --actuator-tracking-scale -0.03 --actuator-tracking-huber-delta 0.04 --action-rate-scale -0.12 --action-rate-huber-delta 0.05 --action-magnitude-scale -0.01 --forward-progress-scale 2.0 --command-progress-scale 1.0 --command-progress-shortfall-scale -2.0 --command-progress-required-ratio 0.35 --command-progress-warmup-steps 30 --forward-pitch-scale -0.4 --forward-pitch-rate-scale -0.08 --base-height-scale -0.3 --imitation-scale 0.0 --alive-scale 2.0 --restore-checkpoint-path /home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/ppo_bc_command_conditioned_rate175_step0_checkpoint --restore-policy-kl-scale 0.015 --push-enable --jax-platforms cuda
```

## Missing Implementation

- stage-gated automation that advances only after corrected-bridge gates pass

## Gate

Each stage must pass corrected-bridge seed gates before the next stage:

- `x=0.08`: 8/8 seeds, no falls, zero corrected velocity excess,
  max pitch-chain tracking p95 <= 0.20 rad, track ratio >= 0.40
- `x=0.0`: 8/8 seeds, no falls, mean |vx| <= 0.005 m/s
- report mean speed, track ratio, push recovery, terrain success, and
  foot clearance / swing peak
