# Candidate Policy Package

status: `READY_FOR_SIM_GATE_REVIEW`
generated_at: `2026-06-22T08:02:44Z`

## Candidate

- name: `open_duck_mini_actuator_bridge_cpu_pilot_20260622_step8240`
- path: `/home/lsd/robots/open-duck-mini-rdkx5/policy/candidates/open_duck_mini_actuator_bridge_cpu_pilot_20260622_step8240/candidate.onnx`
- sha256: `ae48fe2678ef3ab1ef2d791b7eefb92218f790774ddaa6525ce6d2838bef2590`
- size_bytes: `884094`

## Contract

- status: `PASS_POLICY_CONTRACT`
- expected input dim: `101`
- actual input dim: `101`
- expected output dim: `14`
- actual output dim: `14`

| kind | name | shape | dtype |
|---|---|---|---|
| input | `obs` | `[1, 101]` | `tensor(float)` |
| output | `continuous_actions` | `[1, 14]` | `tensor(float)` |

## Source Revisions

| repo | branch | commit | dirty status |
|---|---|---|---|
| `rdk_repo` | `codex/preserve-review-candidate-step8240` | `c40cbabdd7cc6b9c0e81146eebfd14391369d8c2` | `dirty` |
| `playground_repo` | `main` | `bdf37aa850dae0cc383d3817d97c4f3f35edd487` | `clean` |

## Evidence

| evidence | status | path |
|---|---|---|
| `contract_audit` | `PRESENT` | `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/POLICY_SIM_CONTRACT_AUDIT.md` |
| `target_velocity_summary` | `PRESENT` | `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/ACTUATOR_RESPONSE_FIT.md` |
| `actuator_bridge_eval` | `PRESENT` | `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/CPU_CANDIDATE_GATE_STEP8240_ZERO_15S.md` |
| `training_manifest` | `PRESENT` | `/home/lsd/robots/open-duck-mini-rdkx5/policy/candidates/open_duck_mini_actuator_bridge_cpu_pilot_20260622_step8240/training_manifest.json` |

## Sim Gate Status

- eval_role: `candidate`
- overall_status: `PASS_CANDIDATE_SIM_GATE`
- candidate_gate_status: `PASS_CANDIDATE_SIM_GATE`

## Training Manifest

- status: `PASS_SMOKE_RUN`
- platform: `cpu`
- actuator_bridge_enabled: `True`
- target_rate_scale: `0.0`
- actuator_tracking_scale: `0.0`

```bash
JAX_PLATFORM_NAME=cpu /home/lsd/robots/envs/open-duck-playground/bin/python /home/lsd/robots/Open_Duck_Playground/playground/open_duck_mini_v2/runner.py --task flat_terrain --env joystick --output_dir /tmp/open_duck_actuator_bridge_pilots/smoke_20260622T073127Z_cpu --num_timesteps 8192 --ppo_num_envs 16 --ppo_num_evals 1 --ppo_episode_length 100 --ppo_unroll_length 5 --ppo_batch_size 16 --ppo_num_minibatches 1 --ppo_num_updates_per_batch 1 --target_rate_scale 0.0 --actuator_tracking_scale 0.0 --enable_actuator_bridge --actuator_bridge_delay_min_ticks 3 --actuator_bridge_delay_max_ticks 8 --actuator_bridge_tau_min_s 0.06 --actuator_bridge_tau_max_s 0.14 --actuator_bridge_velocity_limit_min_rad_s 2.5 --actuator_bridge_velocity_limit_max_rad_s 4.7 --actuator_bridge_per_joint_variation 0.15
```

## Robot Gate

This package does not approve robot testing. Robot-side suspended
validation still requires reviewed sim gates, Rob physically present,
and explicit approval for the specific test.
