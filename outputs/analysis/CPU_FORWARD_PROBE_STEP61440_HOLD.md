# CPU Forward Probe Step61440 Hold

Last updated: 2026-06-22

## Summary

A CPU-only forward-curriculum probe was run to see whether stronger velocity
tracking pressure and lower alive/imitation pressure could overcome the
stand-still tendency seen in earlier small CPU pilots.

Result:

```text
x=0.0 candidate gate:  PASS_CANDIDATE_SIM_GATE
x=0.08 candidate gate: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
```

This is not a robot candidate.

## Training Run

```text
run_dir: /tmp/open_duck_cpu_forward_probe/smoke_20260622T100321Z_cpu
platform: cpu
status: PASS_SMOKE_RUN
latest ONNX: 2026_06_22_060609_61440.onnx
latest ONNX sha256: 086ec020728bd7bfaf9ce302bcb14575a8704d8905395c9db937476f7f681266
```

Recipe:

```text
num_timesteps: 50000
ppo_num_envs: 256
ppo_num_evals: 4
ppo_episode_length: 500
ppo_unroll_length: 10
ppo_batch_size: 256
ppo_num_minibatches: 8
ppo_num_updates_per_batch: 2
target_rate_scale: -0.001
actuator_tracking_scale: 0.0
tracking_lin_vel_scale: 10.0
alive_scale: 2.0
imitation_scale: 0.0
lin_vel_x_min/max: 0.06 / 0.12
lin_vel_y_min/max: 0.0 / 0.0
ang_vel_yaw_min/max: 0.0 / 0.0
head_range_factor: 0.0
actuator_bridge: enabled
```

Reward checkpoints:

| step | reward | reward_std |
|---:|---:|---:|
| 0 | 3.814843 | 6.575037 |
| 20480 | 5.689296 | 8.353263 |
| 40960 | 3.706674 | 5.376723 |
| 61440 | 4.852508 | 7.032936 |

## Corrected CPU Candidate Gates

The first gate attempt accidentally used the default ROCm backend and hit the
known local `ROCM_ERROR_ILLEGAL_ADDRESS` / timeout path. The corrected gates
were rerun with `JAX_PLATFORM_NAME=cpu`.

### x=0.0

```text
overall_status: PASS_CANDIDATE_SIM_GATE
jax: cpu / TFRT_CPU_0
samples: 750 per mode
duration: 15 s
```

Key metrics:

| metric | value | threshold |
|---|---:|---:|
| max_action_saturation_pct | 0.0000 | 1.0000 |
| max_pitch_tracking_p95_rad | 0.0488 | 0.0800 |
| max_sent_target_velocity_p95_rad_s | 0.1188 | 2.5000 |
| max_abs_body_pitch_p95_rad | 0.0088 | 0.2500 |
| min_base_height_m | 0.1536 | 0.1200 |
| min_reward_mean | 0.5647 | 0.3000 |

Interpretation: the policy remains stable at zero command.

### x=0.08

```text
overall_status: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
jax: cpu / TFRT_CPU_0
samples: 750 per mode
duration: 15 s
```

Key metrics:

| metric | value | threshold |
|---|---:|---:|
| max_action_saturation_pct | 0.0000 | 1.0000 |
| max_pitch_tracking_p95_rad | 0.0461 | 0.0800 |
| max_sent_target_velocity_p95_rad_s | 0.1066 | 2.5000 |
| max_abs_body_pitch_p95_rad | 0.0241 | 0.2500 |
| min_base_height_m | 0.1537 | 0.1200 |
| min_reward_mean | 0.5469 | 0.3000 |
| min_forward_command_tracking_ratio | -0.0005 | 0.2500 |
| max_abs_forward_velocity_error_m_s | 0.0800 | NA |

Mode summary:

| mode | mean_vx | track_ratio | reward_mean |
|---|---:|---:|---:|
| vanilla | 0.0001 | 0.0015 | 0.5469 |
| fitted | 0.0000 | 0.0000 | 0.5473 |
| stress | -0.0000 | -0.0005 | 0.5476 |

Interpretation: the probe still learned a smooth near-standing policy. It does
not track the nonzero forward command.

## Conclusion

The stronger CPU recipe confirms the CPU-scale PPO path is useful for plumbing
and gate validation, but not for generating the walking candidate. The next
useful candidate run remains CUDA-scale training through:

```bash
python3 tools/print_cuda_colab_cell.py --run-candidate
```

Robot testing remains blocked.
