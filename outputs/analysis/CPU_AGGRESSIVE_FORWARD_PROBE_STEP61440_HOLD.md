# CPU Aggressive Forward Probe Step61440 Hold

Last updated: 2026-06-22

## Summary

A local CPU-only ablation was run after browser/Colab automation remained
blocked. This was intended to test whether a much stronger forward-command
reward recipe could overcome the near-standing behavior seen in prior CPU
pilots.

Result:

```text
x=0.0 candidate gate:  PASS_CANDIDATE_SIM_GATE
x=0.08 candidate gate: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
```

This is not a robot candidate.

## Training Run

```text
run_dir: /tmp/open_duck_cpu_aggressive_forward_probe/smoke_20260622T122815Z_cpu
platform: cpu
status: PASS_SMOKE_RUN
latest ONNX: 2026_06_22_083056_61440.onnx
latest ONNX sha256: c6c97d1a94e0f1420a2932bdff5c9e415b6fa62f8f3cc2defa2ca4acc2feb4e2
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
target_rate_scale: -0.0005
actuator_tracking_scale: 0.0
tracking_lin_vel_scale: 30.0
tracking_ang_vel_scale: 0.0
alive_scale: 0.5
imitation_scale: 0.0
stand_still_scale: 0.0
lin_vel_x_min/max: 0.08 / 0.16
lin_vel_y_min/max: 0.0 / 0.0
ang_vel_yaw_min/max: 0.0 / 0.0
head_range_factor: 0.0
actuator_bridge: enabled
```

Reward checkpoints:

| step | reward | reward_std |
|---:|---:|---:|
| 0 | 9.214252 | 17.946888 |
| 20480 | 13.461620 | 22.219254 |
| 40960 | 9.788382 | 16.513422 |
| 61440 | 10.042238 | 14.928759 |

## Candidate Gates

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
| max_pitch_tracking_p95_rad | 0.0482 | 0.0800 |
| max_sent_target_velocity_p95_rad_s | 0.1291 | 2.5000 |
| max_abs_body_pitch_p95_rad | 0.0135 | 0.2500 |
| min_base_height_m | 0.1536 | 0.1200 |
| min_reward_mean | 0.5656 | 0.3000 |

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
| max_pitch_tracking_p95_rad | 0.0489 | 0.0800 |
| max_sent_target_velocity_p95_rad_s | 0.1160 | 2.5000 |
| max_abs_body_pitch_p95_rad | 0.0221 | 0.2500 |
| min_base_height_m | 0.1536 | 0.1200 |
| min_reward_mean | 0.5473 | 0.3000 |
| min_forward_command_tracking_ratio | -0.0014 | 0.2500 |
| max_abs_forward_velocity_error_m_s | 0.0801 | NA |

Mode summary:

| mode | mean_vx | track_ratio | reward_mean |
|---|---:|---:|---:|
| vanilla | 0.0000 | 0.0005 | 0.5473 |
| fitted | -0.0001 | -0.0014 | 0.5480 |
| stress | -0.0000 | -0.0002 | 0.5481 |

## Conclusion

Even with stronger forward-command pressure and reduced standing/imitation
pressure, this CPU-scale run learned a stable near-standing policy. It proves
the local training/gate pipeline still works, but it does not produce a
robot-ready candidate.

The next useful candidate attempt remains a CUDA-backed training run from:

```bash
python3 tools/print_cuda_colab_cell.py --run-candidate
```

Robot motion remains blocked.
