# Phase 2 z0.0075 Iter22 Startup Left-Hip-Pitch Limit Relabel

status: `PASS_STARTUP_LHP_LIMIT_RELABEL_READY`

Offline-only one-row relabel from the Iter21 full-observation startup spike trace. No robot tests, SSH, deploy, grounded replay, runtime behavior change, or PPO training were performed.

## Input

- input_trace: `outputs/analysis/phase2_z0075_iter21_startup_spike_fullobs_trace/iter21_rate150/seed_000/trace.jsonl`
- output_trace: `outputs/analysis/phase2_z0075_iter22_startup_lhp_limit_relabel/seed_000/trace.jsonl`
- dataset_id: `1ab0e007e1ca97da`

## Relabel

| field | value |
|---|---:|
| tick | 11 |
| time_s | 0.2200 |
| joint | left_hip_pitch |
| previous_sent_target_rad | -0.797172 |
| old_target_rad | -0.743143 |
| new_target_rad | -0.747172 |
| corrected_limit_rad_s | 2.5000 |
| old_velocity_rad_s | 2.701429 |
| new_velocity_rad_s | 2.500000 |
| old_action | -0.452573 |
| new_action | -0.468687 |
| sample_weight | 120.0 |

## Interpretation

- The Iter21 rate150 candidate has one repeated max target-velocity violation at startup tick 11.
- This relabel changes only the left-hip-pitch action for that traced state, capping the startup target step to the corrected 2.5 rad/s limit.
- This is intended as a local startup continuity correction, not a global gain or broad rate-smoothing change.
