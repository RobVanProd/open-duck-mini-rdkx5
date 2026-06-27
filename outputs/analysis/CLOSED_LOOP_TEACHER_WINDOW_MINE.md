# Closed-Loop Teacher Window Mine

status: `HOLD_INSUFFICIENT_CLOSED_LOOP_WINDOWS`

This is an offline trace-mining artifact. It does not train, deploy, SSH, run robot tests, or change runtime behavior.

## Criteria

- window_samples: `25`
- stride_samples: `5`
- dt_s: `0.02`
- envelope_high: `3.75`
- min_mean_vx: `0.04`
- min_tick_vx: `0.04`
- min_single_support_pct: `20.0`
- min_moving_in_envelope_pct: `40.0`
- min_moving_single_in_envelope_pct: `10.0`
- max_vy_abs_p95: `0.2`
- max_body_pitch_abs_p95: `0.2`
- min_base_height: `0.145`

## Aggregate

- windows: `1104`
- pass_windows: `0`
- review_windows: `0`
- rejected_windows: `1104`
- pass_command_cells: `[]`
- pass_source_names: `[]`

## By Command Cell

| command_cell | windows | pass | review | reject | mean_vx |
|---|---:|---:|---:|---:|---:|
| upstream_nearest_turn | 368 | 0 | 0 | 368 | 0.0542 |
| straight_x004 | 368 | 0 | 0 | 368 | 0.0003 |
| straight_x008 | 368 | 0 | 0 | 368 | 0.0644 |

## Top Passing Windows

| command | source | ticks | vx | single_% | move_env_% | move_single_env_% | pitch_p95 | vy95 | height | fastest_pitch |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| NA | NA | NA | NA | NA | NA | NA | NA | NA | NA | NA |

## Rejection Reasons

| reason | count |
|---|---:|
| `high_pitch_velocity_p95` | 705 |
| `low_mean_vx` | 472 |
| `low_moving_in_envelope` | 461 |
| `low_moving_single_in_envelope` | 455 |
| `low_single_support` | 410 |
| `high_lateral_velocity` | 136 |
| `low_base_height` | 1 |

## Interpretation

- Passing windows are candidate teacher snippets only; they are not a complete walking policy.
- If passing windows exist only inside the moving command cells, straight x=0.04 should remain a posture/no-motion gate, not the first walking gate.
- Before BC/export, inspect whether passing snippets have enough phase/contact diversity and whether high right-knee windows can be rejected without destroying continuity.
