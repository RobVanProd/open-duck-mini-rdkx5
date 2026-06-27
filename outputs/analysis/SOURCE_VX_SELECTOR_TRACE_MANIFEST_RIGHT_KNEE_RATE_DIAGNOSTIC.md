# Source-Vx Selector Trace Manifest Right-Knee Rate Diagnostic

status: `HOLD_TEACHER_TRACE_RIGHT_KNEE_RATE_DISCONTINUITIES`

This is an offline dataset diagnostic. It does not run robot tests, SSH, deploy, train, or change runtime behavior.

## Setup

- manifest: `outputs/analysis/source_vx_selector_fitted_bridge_trace_manifest.json`
- dataset_id: `de4935ec7672ceea`
- joint: `right_knee`
- joint_index: `12`
- implied target equation: `target = home + action * 0.25`
- dt: `0.02 s`

## Result

- total_deltas: `3992`
- events_over_3p75_rad_s: `506` (`12.68%`)
- max_target_velocity_rad_s: `8.3015`
- high_event_contacts: `{'11': 297, '10': 208, '00': 1}`

## Per-Source Rows

| source | deltas | events>3.75 | pct | max_vel | contacts |
|---|---:|---:|---:|---:|---|
| `source_vx_selector_fitted_bridge_x008_10s_traces/seed_000.jsonl` | 499 | 65 | 13.03% | 7.4214 | `{'11': 35, '10': 30}` |
| `source_vx_selector_fitted_bridge_x008_10s_traces/seed_001.jsonl` | 499 | 62 | 12.42% | 7.4632 | `{'11': 41, '10': 21}` |
| `source_vx_selector_fitted_bridge_x008_10s_traces/seed_002.jsonl` | 499 | 63 | 12.63% | 6.8682 | `{'10': 30, '11': 33}` |
| `source_vx_selector_fitted_bridge_x008_10s_traces/seed_003.jsonl` | 499 | 63 | 12.63% | 5.9447 | `{'00': 1, '11': 35, '10': 27}` |
| `source_vx_selector_fitted_bridge_x008_10s_traces/seed_004.jsonl` | 499 | 62 | 12.42% | 8.3015 | `{'11': 36, '10': 26}` |
| `source_vx_selector_fitted_bridge_x008_10s_traces/seed_005.jsonl` | 499 | 65 | 13.03% | 6.3583 | `{'11': 39, '10': 26}` |
| `source_vx_selector_fitted_bridge_x008_10s_traces/seed_006.jsonl` | 499 | 64 | 12.83% | 7.7089 | `{'11': 39, '10': 25}` |
| `source_vx_selector_fitted_bridge_x008_10s_traces/seed_007.jsonl` | 499 | 62 | 12.42% | 7.7909 | `{'11': 39, '10': 23}` |

## Top Events

| source | tick | time_s | target_vel | action_delta | contacts |
|---|---:|---:|---:|---:|---|
| `source_vx_selector_fitted_bridge_x008_10s_traces/seed_004.jsonl` | 329 | 6.58 | 8.3015 | 0.6641 | `11` |
| `source_vx_selector_fitted_bridge_x008_10s_traces/seed_007.jsonl` | 22 | 0.44 | 7.7909 | 0.6233 | `11` |
| `source_vx_selector_fitted_bridge_x008_10s_traces/seed_006.jsonl` | 446 | 8.92 | 7.7089 | 0.6167 | `11` |
| `source_vx_selector_fitted_bridge_x008_10s_traces/seed_006.jsonl` | 476 | 9.52 | 7.7089 | 0.6167 | `10` |
| `source_vx_selector_fitted_bridge_x008_10s_traces/seed_007.jsonl` | 233 | 4.66 | 7.7089 | 0.6167 | `11` |
| `source_vx_selector_fitted_bridge_x008_10s_traces/seed_001.jsonl` | 116 | 2.32 | 7.4632 | 0.5971 | `11` |
| `source_vx_selector_fitted_bridge_x008_10s_traces/seed_001.jsonl` | 147 | 2.94 | 7.4632 | 0.5971 | `11` |
| `source_vx_selector_fitted_bridge_x008_10s_traces/seed_004.jsonl` | 422 | 8.44 | 7.4537 | 0.5963 | `11` |
| `source_vx_selector_fitted_bridge_x008_10s_traces/seed_000.jsonl` | 354 | 7.08 | 7.4214 | 0.5937 | `11` |
| `source_vx_selector_fitted_bridge_x008_10s_traces/seed_000.jsonl` | 116 | 2.32 | 7.4055 | 0.5924 | `11` |
| `source_vx_selector_fitted_bridge_x008_10s_traces/seed_004.jsonl` | 147 | 2.94 | 7.4055 | 0.5924 | `11` |
| `source_vx_selector_fitted_bridge_x008_10s_traces/seed_002.jsonl` | 176 | 3.52 | 6.8682 | 0.5495 | `11` |
| `source_vx_selector_fitted_bridge_x008_10s_traces/seed_002.jsonl` | 86 | 1.72 | 6.4301 | 0.5144 | `11` |
| `source_vx_selector_fitted_bridge_x008_10s_traces/seed_006.jsonl` | 30 | 0.60 | 6.3641 | 0.5091 | `10` |
| `source_vx_selector_fitted_bridge_x008_10s_traces/seed_005.jsonl` | 33 | 0.66 | 6.3583 | 0.5087 | `11` |
| `source_vx_selector_fitted_bridge_x008_10s_traces/seed_007.jsonl` | 111 | 2.22 | 6.2926 | 0.5034 | `11` |
| `source_vx_selector_fitted_bridge_x008_10s_traces/seed_006.jsonl` | 25 | 0.50 | 5.9664 | 0.4773 | `11` |
| `source_vx_selector_fitted_bridge_x008_10s_traces/seed_000.jsonl` | 476 | 9.52 | 5.9447 | 0.4756 | `11` |
| `source_vx_selector_fitted_bridge_x008_10s_traces/seed_005.jsonl` | 213 | 4.26 | 5.9447 | 0.4756 | `11` |
| `source_vx_selector_fitted_bridge_x008_10s_traces/seed_006.jsonl` | 236 | 4.72 | 5.9447 | 0.4756 | `11` |

## Interpretation

- The exact blend ONNX right-knee spikes are not an ONNX export artifact and not introduced only by closed-loop rollout.
- The teacher trace manifest already includes frequent right-knee target-rate discontinuities, especially during double support.
- The earlier blend smoke metric was flattened across joints, so it hid this max-joint right-knee problem.
- Next offline branch should re-curate or relabel the selector trace dataset with a max-joint/per-joint right-knee target-rate constraint before another portable student export.
