# Closed-Loop Teacher Window Mine

status: `PASS_CURATED_CLOSED_LOOP_WINDOWS_FOUND`

This is an offline trace-mining artifact. It does not train, deploy, SSH, run robot tests, or change runtime behavior.

## Criteria

- window_samples: `10`
- stride_samples: `2`
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

- windows: `2904`
- pass_windows: `142`
- review_windows: `91`
- rejected_windows: `2671`
- pass_command_cells: `['straight_x004', 'straight_x008', 'upstream_nearest_turn']`
- pass_source_names: `['published_policy_upstream_main_backlash_seed0', 'published_policy_upstream_main_backlash_seed1', 'published_policy_upstream_main_backlash_seed2', 'published_policy_upstream_main_backlash_seed3', 'published_policy_upstream_main_backlash_seed4', 'published_policy_upstream_main_backlash_seed5', 'published_policy_upstream_main_backlash_seed6', 'published_policy_upstream_main_backlash_seed7', 'published_policy_upstream_main_backlash_x004_seed0', 'published_policy_upstream_main_backlash_x004_seed4', 'published_policy_upstream_main_backlash_x008_seed0', 'published_policy_upstream_main_backlash_x008_seed1', 'published_policy_upstream_main_backlash_x008_seed2', 'published_policy_upstream_main_backlash_x008_seed3', 'published_policy_upstream_main_backlash_x008_seed4', 'published_policy_upstream_main_backlash_x008_seed5', 'published_policy_upstream_main_backlash_x008_seed6', 'published_policy_upstream_main_backlash_x008_seed7']`

## By Command Cell

| command_cell | windows | pass | review | reject | mean_vx |
|---|---:|---:|---:|---:|---:|
| upstream_nearest_turn | 968 | 76 | 8 | 884 | 0.0541 |
| straight_x004 | 968 | 3 | 3 | 962 | 0.0012 |
| straight_x008 | 968 | 63 | 80 | 825 | 0.0642 |

## Top Passing Windows

| command | source | ticks | vx | single_% | move_env_% | move_single_env_% | pitch_p95 | vy95 | height | fastest_pitch |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| straight_x008 | `published_policy_upstream_main_backlash_x008_seed6` | 200-209 | 0.0875 | 60.0000 | 100.0000 | 60.0000 | 3.3272 | 0.1966 | 0.1622 | `left_knee:3.0216` |
| straight_x008 | `published_policy_upstream_main_backlash_x008_seed7` | 120-129 | 0.0829 | 60.0000 | 100.0000 | 60.0000 | 3.5446 | 0.1964 | 0.1629 | `left_knee:3.1701` |
| straight_x008 | `published_policy_upstream_main_backlash_x008_seed5` | 38-47 | 0.0814 | 60.0000 | 100.0000 | 60.0000 | 3.2076 | 0.1909 | 0.1607 | `left_knee:3.1200` |
| straight_x008 | `published_policy_upstream_main_backlash_x008_seed7` | 222-231 | 0.0806 | 60.0000 | 100.0000 | 60.0000 | 3.4472 | 0.1232 | 0.1633 | `left_knee:3.4026` |
| straight_x008 | `published_policy_upstream_main_backlash_x008_seed1` | 228-237 | 0.0805 | 50.0000 | 90.0000 | 50.0000 | 3.6779 | 0.1979 | 0.1625 | `right_ankle:3.4461` |
| straight_x008 | `published_policy_upstream_main_backlash_x008_seed0` | 92-101 | 0.0787 | 70.0000 | 100.0000 | 70.0000 | 3.3365 | 0.1953 | 0.1634 | `left_knee:2.8984` |
| upstream_nearest_turn | `published_policy_upstream_main_backlash_seed1` | 200-209 | 0.0785 | 60.0000 | 100.0000 | 60.0000 | 3.0287 | 0.1692 | 0.1628 | `left_knee:2.8227` |
| upstream_nearest_turn | `published_policy_upstream_main_backlash_seed5` | 120-129 | 0.0777 | 50.0000 | 100.0000 | 50.0000 | 2.6003 | 0.1765 | 0.1627 | `right_ankle:2.4852` |
| straight_x008 | `published_policy_upstream_main_backlash_x008_seed3` | 112-121 | 0.0775 | 40.0000 | 90.0000 | 30.0000 | 3.7068 | 0.1270 | 0.1644 | `left_knee:3.3871` |
| straight_x008 | `published_policy_upstream_main_backlash_x008_seed0` | 222-231 | 0.0772 | 60.0000 | 90.0000 | 50.0000 | 3.7273 | 0.1260 | 0.1628 | `left_knee:3.6352` |
| straight_x008 | `published_policy_upstream_main_backlash_x008_seed3` | 114-123 | 0.0772 | 60.0000 | 90.0000 | 50.0000 | 3.7068 | 0.1194 | 0.1632 | `left_knee:3.6962` |
| straight_x008 | `published_policy_upstream_main_backlash_x008_seed7` | 220-229 | 0.0771 | 40.0000 | 100.0000 | 40.0000 | 3.4472 | 0.1393 | 0.1647 | `left_knee:3.2507` |
| straight_x008 | `published_policy_upstream_main_backlash_x008_seed5` | 92-101 | 0.0770 | 60.0000 | 100.0000 | 60.0000 | 3.1799 | 0.1928 | 0.1616 | `left_knee:2.8344` |
| straight_x008 | `published_policy_upstream_main_backlash_x008_seed7` | 32-41 | 0.0769 | 50.0000 | 90.0000 | 40.0000 | 3.6754 | 0.1199 | 0.1635 | `left_knee:3.3167` |
| upstream_nearest_turn | `published_policy_upstream_main_backlash_seed3` | 120-129 | 0.0768 | 50.0000 | 100.0000 | 50.0000 | 3.0298 | 0.1728 | 0.1630 | `right_ankle:2.8910` |
| straight_x008 | `published_policy_upstream_main_backlash_x008_seed0` | 90-99 | 0.0764 | 80.0000 | 90.0000 | 70.0000 | 3.6308 | 0.1953 | 0.1634 | `left_knee:3.6618` |
| upstream_nearest_turn | `published_policy_upstream_main_backlash_seed1` | 202-211 | 0.0761 | 40.0000 | 90.0000 | 40.0000 | 3.6829 | 0.1692 | 0.1628 | `right_knee:3.4203` |
| straight_x008 | `published_policy_upstream_main_backlash_x008_seed0` | 220-229 | 0.0760 | 40.0000 | 90.0000 | 30.0000 | 3.7273 | 0.1188 | 0.1641 | `left_knee:3.4044` |
| straight_x008 | `published_policy_upstream_main_backlash_x008_seed7` | 34-43 | 0.0759 | 70.0000 | 90.0000 | 60.0000 | 3.6754 | 0.1524 | 0.1626 | `left_knee:3.6897` |
| upstream_nearest_turn | `published_policy_upstream_main_backlash_seed6` | 174-183 | 0.0759 | 50.0000 | 100.0000 | 50.0000 | 2.9700 | 0.1700 | 0.1625 | `right_ankle:2.9769` |
| straight_x008 | `published_policy_upstream_main_backlash_x008_seed5` | 84-93 | 0.0758 | 30.0000 | 90.0000 | 20.0000 | 3.6111 | 0.1621 | 0.1630 | `left_knee:3.2249` |
| upstream_nearest_turn | `published_policy_upstream_main_backlash_seed6` | 120-129 | 0.0758 | 50.0000 | 100.0000 | 50.0000 | 3.1810 | 0.1768 | 0.1627 | `right_ankle:3.1865` |
| straight_x008 | `published_policy_upstream_main_backlash_x008_seed2` | 38-47 | 0.0757 | 60.0000 | 90.0000 | 60.0000 | 3.6483 | 0.1996 | 0.1620 | `left_knee:3.1936` |
| straight_x008 | `published_policy_upstream_main_backlash_x008_seed7` | 140-149 | 0.0757 | 50.0000 | 90.0000 | 40.0000 | 3.5216 | 0.1174 | 0.1632 | `left_knee:3.1850` |
| upstream_nearest_turn | `published_policy_upstream_main_backlash_seed0` | 66-75 | 0.0757 | 50.0000 | 100.0000 | 50.0000 | 2.8396 | 0.1715 | 0.1630 | `right_ankle:2.8397` |

## Rejection Reasons

| reason | count |
|---|---:|
| `high_pitch_velocity_p95` | 1619 |
| `low_moving_single_in_envelope` | 1223 |
| `low_mean_vx` | 1214 |
| `low_moving_in_envelope` | 1208 |
| `low_single_support` | 1074 |
| `high_lateral_velocity` | 488 |
| `low_base_height` | 2 |

## Interpretation

- Passing windows are candidate teacher snippets only; they are not a complete walking policy.
- If passing windows exist only inside the moving command cells, straight x=0.04 should remain a posture/no-motion gate, not the first walking gate.
- Before BC/export, inspect whether passing snippets have enough phase/contact diversity and whether high right-knee windows can be rejected without destroying continuity.
