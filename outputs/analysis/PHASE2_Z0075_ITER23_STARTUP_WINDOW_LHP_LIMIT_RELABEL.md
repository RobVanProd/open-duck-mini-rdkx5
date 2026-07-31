# Phase 2 z0.0075 Iter23 Startup-Window Left-Hip-Pitch Limit Relabel

status: `PASS_STARTUP_WINDOW_LHP_LIMIT_RELABEL_READY`

Offline-only six-row startup-window relabel from the Iter21 full-observation spike trace. No robot tests, SSH, deploy, grounded replay, runtime behavior change, or PPO training were performed.

## Input

- input_trace: `outputs/analysis/phase2_z0075_iter21_startup_spike_fullobs_trace/iter21_rate150/seed_000/trace.jsonl`
- output_trace: `outputs/analysis/phase2_z0075_iter23_startup_window_lhp_limit_relabel/seed_000/trace.jsonl`
- dataset_id: `e4289041746c3afb`
- tick_window: `8-13`
- sample_weight_each: `30.0`

## Changed Tick

| field | value |
|---|---:|
| tick | 11 |
| joint | left_hip_pitch |
| previous_sent_target_rad | -0.797172 |
| old_target_rad | -0.743143 |
| new_target_rad | -0.747172 |
| old_velocity_rad_s | 2.701429 |
| new_velocity_rad_s | 2.500000 |
| old_action | -0.452573 |
| new_action | -0.468687 |

## Interpretation

- This keeps neighboring startup actions as local anchors and only caps the illegal tick-11 left-hip-pitch target step.
- It tests whether Iter22 failed because a single high-weight point distorted the local action map.
