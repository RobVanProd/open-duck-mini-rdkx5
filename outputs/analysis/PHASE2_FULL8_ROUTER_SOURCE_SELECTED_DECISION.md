# Full-8 Router Source Selected Decision

status: `PASS_FULL8_ROUTER_SOURCE_SELECTED`

A selected full-8 behavior source now covers seeds 0-7 under the z=0.0075 rough+push corrected-bridge screen: command-gated source for seeds 0,1,2,3,4,6,7 and iter25 for seed 5.

This is offline source-generation evidence. It did not train, deploy, SSH, run robot tests, grounded replay, or change runtime behavior. It is not a deployable runtime router because the selected route is assembled from evaluated seed coverage.

## Artifacts

- command_gated_trace_sweep: `outputs/analysis/phase2_full8_router_source_command_gated_traces.json`
- iter25_seed5_trace_sweep: `outputs/analysis/phase2_full8_router_source_iter25_seed5_trace.json`
- selected_manifest: `outputs/analysis/phase2_full8_router_source_selected_manifest.json`
- manifest_dataset_id: `e395c159e077d118`
- manifest_entries/samples: `8` / `6000`

## Route

| seed | selected policy | status | vx | track ratio | pitch p95 | base min | p95 excess | max excess |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 0 | `command_gated_zero0020` | `PASS_CANDIDATE_SIM_GATE` | 0.0272 | 0.3403 | 0.1737 | 0.1581 | 0.0000 | 0.0000 |
| 1 | `command_gated_zero0020` | `PASS_CANDIDATE_SIM_GATE` | 0.0254 | 0.3170 | 0.1876 | 0.1581 | 0.0000 | 0.0000 |
| 2 | `command_gated_zero0020` | `PASS_CANDIDATE_SIM_GATE` | 0.0269 | 0.3367 | 0.1894 | 0.1581 | 0.0000 | 0.0000 |
| 3 | `command_gated_zero0020` | `PASS_CANDIDATE_SIM_GATE` | 0.0238 | 0.2975 | 0.1776 | 0.1581 | 0.0000 | 0.0000 |
| 4 | `command_gated_zero0020` | `PASS_CANDIDATE_SIM_GATE` | 0.0244 | 0.3052 | 0.1830 | 0.1581 | 0.0000 | 0.0000 |
| 5 | `iter25` | `PASS_CANDIDATE_SIM_GATE` | 0.0314 | 0.3924 | 0.1779 | 0.1589 | 0.0000 | 0.0000 |
| 6 | `command_gated_zero0020` | `PASS_CANDIDATE_SIM_GATE` | 0.0232 | 0.2896 | 0.1917 | 0.1581 | 0.0000 | 0.0000 |
| 7 | `command_gated_zero0020` | `PASS_CANDIDATE_SIM_GATE` | 0.0265 | 0.3311 | 0.1724 | 0.1581 | 0.0000 | 0.0000 |

## Aggregate

- pass_count: `8/8`
- falls: `0`
- mean_vx_m_s: `0.0261`
- mean_track_ratio: `0.3262`
- max_body_pitch_p95_rad: `0.1917`
- min_base_height_m: `0.1581`
- max_p95_velocity_excess_rad_s: `0.0000`
- max_instant_velocity_excess_rad_s: `0.0000`

## Decision

The full-8 source route is valid as an offline behavior-preservation source. It is not a deployable policy and it does not authorize robot validation or long DR training by itself.

## Next Recommendation

Use this selected full-8 source manifest as the next behavior-preservation target. The next branch should first test an eval-only wrapper/router or branch-aware trainable parent against this full-8 source, then only resume domain-randomized robustness training after the resulting trainable parent clears x=0.08 and x=0.0 gates. Do not treat this seed-selected source as deployable runtime routing.
