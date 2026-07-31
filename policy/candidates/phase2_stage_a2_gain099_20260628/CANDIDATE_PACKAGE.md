# Candidate Policy Package

status: `READY_FOR_SIM_GATE_REVIEW`
generated_at: `2026-06-28T07:30:56Z`

## Candidate

- name: `phase2_stage_a2_gain099_20260628`
- path: `/home/lsd/robots/open-duck-mini-rdkx5/policy/candidates/phase2_stage_a2_gain099_20260628/candidate.onnx`
- sha256: `a082be6cf5c486073523bbd0fba4ea3645dc448270ca0a8e28c4ce5a4e8d31c4`
- size_bytes: `884902`

## Contract

- status: `PASS_POLICY_CONTRACT`
- expected input dim: `101`
- actual input dim: `101`
- expected output dim: `14`
- actual output dim: `14`

| kind | name | shape | dtype |
|---|---|---|---|
| input | `obs` | `[1, 101]` | `tensor(float)` |
| output | `continuous_actions_gain099` | `[1, 14]` | `tensor(float)` |

## Source Revisions

| repo | branch | commit | dirty status |
|---|---|---|---|
| `rdk_repo` | `codex/live-oracle-dagger-phase-student` | `62f82e3902e4fd47a875ed64860e16b38212e293` | `dirty` |
| `playground_repo` | `codex/forward-progress-reward` | `a2bbcff4b6dd50803499adfabf882750e19f6bd9` | `clean` |

## Evidence

| evidence | required | status | path |
|---|---|---|---|
| `contract_audit` | `True` | `PRESENT` | `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/policy_sim_contract_audit.json` |
| `target_velocity_summary` | `False` | `MISSING` | `None` |
| `candidate_gate_x0` | `True` | `PRESENT` | `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/phase2_stage_a2_164k_gain099_x000_gate.json` |
| `candidate_gate_x008` | `True` | `PRESENT` | `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/phase2_stage_a2_164k_gain099_x008_gate.json` |
| `actuator_bridge_eval_legacy` | `False` | `MISSING` | `None` |
| `training_manifest` | `True` | `PRESENT` | `/home/lsd/robots/open-duck-mini-rdkx5/outputs/phase2_domain_randomization/stage_a2_preserve_narrow_flat_no_push_gpu/smoke_20260628T031553Z_gpu/smoke_manifest.final.json` |

## Sim Gate Status

| gate | eval_role | overall_status | candidate_gate_status | pass/total |
|---|---|---|---|---:|
| `candidate_gate_x0` | `candidate_seed_sweep` | `PASS_CANDIDATE_SEED_SWEEP` | `PASS_CANDIDATE_SEED_SWEEP` | `8/8` |
| `candidate_gate_x008` | `candidate_seed_sweep` | `PASS_CANDIDATE_SEED_SWEEP` | `PASS_CANDIDATE_SEED_SWEEP` | `8/8` |

## Training Manifest

- status: `PASS_SMOKE_RUN`
- platform: `gpu`
- actuator_bridge_enabled: `True`
- target_rate_scale: `0.0`
- actuator_tracking_scale: `0.0`

```bash
JAX_PLATFORM_NAME=gpu JAX_PLATFORMS=rocm ../envs/open-duck-playground/bin/python ../Open_Duck_Playground/playground/open_duck_mini_v2/runner.py --task flat_terrain_backlash --env joystick --output_dir /home/lsd/robots/open-duck-mini-rdkx5/outputs/phase2_domain_randomization/stage_a2_preserve_narrow_flat_no_push_gpu/smoke_20260628T031553Z_gpu --export_min_step 1 --num_timesteps 250000 --ppo_num_envs 128 --ppo_num_evals 4 --ppo_episode_length 750 --ppo_unroll_length 20 --ppo_batch_size 1024 --ppo_num_minibatches 4 --ppo_num_updates_per_batch 2 --target_rate_scale 0 --actuator_tracking_scale 0 --restore_checkpoint_path /home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/ppo_bc_command_conditioned_rate175_step0_checkpoint --ppo_learning_rate 0.00003 --ppo_entropy_cost 0.001 --ppo_clipping_epsilon 0.05 --ppo_max_grad_norm 0.25 --restore_policy_kl_scale 1 --forward_progress_scale 2 --command_progress_scale 1 --command_progress_shortfall_scale -2.5 --command_progress_required_ratio 0.4 --command_progress_warmup_steps 30 --action_rate_huber_delta 0.05 --target_rate_huber_delta 0.08 --actuator_tracking_huber_delta 0.04 --action_rate_scale -0.08 --action_magnitude_scale -0.005 --base_height_scale -0.3 --forward_pitch_scale -0.4 --forward_pitch_rate_scale -0.08 --alive_scale 2 --imitation_scale 0 --lin_vel_x_min 0.06 --lin_vel_x_max 0.1 --lin_vel_y_min 0 --lin_vel_y_max 0 --ang_vel_yaw_min 0 --ang_vel_yaw_max 0 --command_resample_steps 600 --zero_command_probability 0.15 --dr_friction_min 0.85 --dr_friction_max 1 --dr_frictionloss_scale_min 0.99 --dr_frictionloss_scale_max 1.01 --dr_armature_scale_min 1 --dr_armature_scale_max 1.01 --dr_com_jitter_m 0.005 --dr_mass_scale_min 0.99 --dr_mass_scale_max 1.01 --dr_torso_mass_delta_min -0.01 --dr_torso_mass_delta_max 0.01 --dr_qpos_jitter_rad 0.003 --dr_actuator_gain_scale_min 0.99 --dr_actuator_gain_scale_max 1.01 --dr_leg_geometry_jitter_scale 0.001 --push_interval_min_s 8 --push_interval_max_s 12 --push_magnitude_min 0 --push_magnitude_max 0 --noise_level 0.25 --noise_hip_pos 0.005 --noise_knee_pos 0.005 --noise_ankle_pos 0.005 --noise_joint_vel 0.5 --noise_gravity 0.025 --noise_gyro 0.025 --noise_accelerometer 0.0125 --no-push_enable --enable_behavior_prior --behavior_prior_mlp_npz /home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_candidate/candidate_mlp.npz --behavior_prior_scale -0.4 --behavior_prior_huber_delta 0.05 --enable_actuator_bridge --actuator_bridge_delay_min_ticks 3 --actuator_bridge_delay_max_ticks 4 --actuator_bridge_tau_min_s 0.06 --actuator_bridge_tau_max_s 0.1 --actuator_bridge_velocity_limit_min_rad_s 2 --actuator_bridge_velocity_limit_max_rad_s 3.25 --actuator_bridge_per_joint_variation 0.05
```

## Robot Gate

This package does not approve robot testing. Robot-side suspended
validation still requires reviewed sim gates, Rob physically present,
and explicit approval for the specific test.
