# Closed-Loop Snippet Stitch Plan

status: `HOLD_STITCH_RUNS_TOO_SHORT`

This is an offline analysis artifact. It does not train, deploy, SSH, run robot tests, or change runtime behavior.

## Criteria

- window_samples: `10`
- stride_samples: `2`
- allowed_gap_ticks: `2`
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

- traces: `24`
- short_pass_windows: `142`
- runs: `86`
- pass_runs: `84`
- trace_count_with_pass_run_25_ticks: `0`
- trace_count_with_pass_run_50_ticks: `0`
- max_run_span_ticks: `18`
- max_pass_run_span_ticks: `18`

## By Command Cell

| command_cell | traces | short_pass | runs | pass_runs | max_run | max_pass_run |
|---|---:|---:|---:|---:|---:|---:|
| upstream_nearest_turn | 8 | 76 | 56 | 55 | 14 | 12 |
| straight_x004 | 8 | 3 | 2 | 2 | 12 | 12 |
| straight_x008 | 8 | 63 | 28 | 27 | 18 | 18 |

## Longest Passing Runs

| command | source | ticks | span | snippets | vx | single_% | move_env_% | move_single_env_% | pitch_p95 | reasons |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| straight_x008 | `published_policy_upstream_main_backlash_x008_seed5` | 84-101 | 18 | 5 | 0.0755 | 38.8889 | 94.4444 | 33.3333 | 3.3038 | `` |
| straight_x008 | `published_policy_upstream_main_backlash_x008_seed7` | 218-231 | 14 | 3 | 0.0757 | 50.0000 | 100.0000 | 50.0000 | 3.3577 | `` |
| straight_x008 | `published_policy_upstream_main_backlash_x008_seed3` | 110-123 | 14 | 3 | 0.0748 | 50.0000 | 92.8571 | 42.8571 | 3.5003 | `` |
| straight_x008 | `published_policy_upstream_main_backlash_x008_seed0` | 218-231 | 14 | 3 | 0.0736 | 50.0000 | 92.8571 | 42.8571 | 3.5767 | `` |
| straight_x008 | `published_policy_upstream_main_backlash_x008_seed2` | 110-123 | 14 | 3 | 0.0726 | 50.0000 | 92.8571 | 42.8571 | 3.5930 | `` |
| straight_x008 | `published_policy_upstream_main_backlash_x008_seed7` | 30-43 | 14 | 3 | 0.0723 | 50.0000 | 92.8571 | 42.8571 | 3.5287 | `` |
| straight_x008 | `published_policy_upstream_main_backlash_x008_seed7` | 138-151 | 14 | 3 | 0.0719 | 50.0000 | 92.8571 | 42.8571 | 3.3851 | `` |
| straight_x008 | `published_policy_upstream_main_backlash_x008_seed0` | 110-123 | 14 | 3 | 0.0715 | 57.1429 | 92.8571 | 50.0000 | 3.4413 | `` |
| straight_x008 | `published_policy_upstream_main_backlash_x008_seed5` | 192-205 | 14 | 3 | 0.0714 | 50.0000 | 92.8571 | 42.8571 | 3.5605 | `` |
| straight_x008 | `published_policy_upstream_main_backlash_x008_seed6` | 138-151 | 14 | 3 | 0.0713 | 57.1429 | 92.8571 | 50.0000 | 3.4147 | `` |
| straight_x008 | `published_policy_upstream_main_backlash_x008_seed1` | 192-205 | 14 | 3 | 0.0708 | 50.0000 | 92.8571 | 42.8571 | 3.6022 | `` |
| straight_x008 | `published_policy_upstream_main_backlash_x008_seed1` | 164-177 | 14 | 3 | 0.0691 | 50.0000 | 85.7143 | 42.8571 | 3.3991 | `` |
| straight_x008 | `published_policy_upstream_main_backlash_x008_seed5` | 164-177 | 14 | 3 | 0.0675 | 57.1429 | 100.0000 | 57.1429 | 3.1279 | `` |
| straight_x008 | `published_policy_upstream_main_backlash_x008_seed2` | 218-231 | 14 | 3 | 0.0675 | 50.0000 | 92.8571 | 42.8571 | 3.5026 | `` |
| upstream_nearest_turn | `published_policy_upstream_main_backlash_seed6` | 144-157 | 14 | 3 | 0.0628 | 50.0000 | 85.7143 | 42.8571 | 4.2788 | `high_pitch_velocity_p95` |
| straight_x008 | `published_policy_upstream_main_backlash_x008_seed0` | 90-101 | 12 | 2 | 0.0794 | 66.6667 | 91.6667 | 58.3333 | 3.6157 | `` |
| upstream_nearest_turn | `published_policy_upstream_main_backlash_seed1` | 200-211 | 12 | 2 | 0.0780 | 50.0000 | 91.6667 | 50.0000 | 3.5646 | `` |
| straight_x008 | `published_policy_upstream_main_backlash_x008_seed6` | 226-237 | 12 | 2 | 0.0764 | 66.6667 | 91.6667 | 58.3333 | 3.5944 | `` |
| upstream_nearest_turn | `published_policy_upstream_main_backlash_seed5` | 118-129 | 12 | 2 | 0.0763 | 58.3333 | 91.6667 | 50.0000 | 3.6448 | `` |
| straight_x008 | `published_policy_upstream_main_backlash_x008_seed2` | 64-75 | 12 | 2 | 0.0763 | 66.6667 | 91.6667 | 58.3333 | 3.5703 | `` |
| upstream_nearest_turn | `published_policy_upstream_main_backlash_seed3` | 92-103 | 12 | 2 | 0.0755 | 50.0000 | 91.6667 | 50.0000 | 3.6936 | `` |
| upstream_nearest_turn | `published_policy_upstream_main_backlash_seed2` | 10-21 | 12 | 2 | 0.0753 | 33.3333 | 83.3333 | 33.3333 | 3.6245 | `` |
| straight_x008 | `published_policy_upstream_main_backlash_x008_seed6` | 172-183 | 12 | 2 | 0.0748 | 66.6667 | 83.3333 | 58.3333 | 3.9563 | `high_pitch_velocity_p95` |
| upstream_nearest_turn | `published_policy_upstream_main_backlash_seed5` | 146-157 | 12 | 2 | 0.0742 | 50.0000 | 91.6667 | 50.0000 | 3.3255 | `` |
| upstream_nearest_turn | `published_policy_upstream_main_backlash_seed5` | 92-103 | 12 | 2 | 0.0742 | 50.0000 | 91.6667 | 50.0000 | 3.4833 | `` |
| upstream_nearest_turn | `published_policy_upstream_main_backlash_seed3` | 200-211 | 12 | 2 | 0.0736 | 50.0000 | 91.6667 | 50.0000 | 3.6469 | `` |
| upstream_nearest_turn | `published_policy_upstream_main_backlash_seed3` | 146-157 | 12 | 2 | 0.0720 | 50.0000 | 91.6667 | 50.0000 | 3.5528 | `` |
| upstream_nearest_turn | `published_policy_upstream_main_backlash_seed7` | 146-157 | 12 | 2 | 0.0716 | 50.0000 | 91.6667 | 50.0000 | 3.5388 | `` |
| straight_x008 | `published_policy_upstream_main_backlash_x008_seed3` | 198-209 | 12 | 2 | 0.0714 | 58.3333 | 91.6667 | 50.0000 | 3.5667 | `` |
| upstream_nearest_turn | `published_policy_upstream_main_backlash_seed6` | 200-211 | 12 | 2 | 0.0705 | 50.0000 | 91.6667 | 50.0000 | 3.5764 | `` |
| upstream_nearest_turn | `published_policy_upstream_main_backlash_seed2` | 200-211 | 12 | 2 | 0.0672 | 50.0000 | 91.6667 | 50.0000 | 3.4942 | `` |
| upstream_nearest_turn | `published_policy_upstream_main_backlash_seed2` | 146-157 | 12 | 2 | 0.0670 | 50.0000 | 91.6667 | 50.0000 | 3.4910 | `` |
| upstream_nearest_turn | `published_policy_upstream_main_backlash_seed7` | 200-211 | 12 | 2 | 0.0669 | 50.0000 | 91.6667 | 50.0000 | 3.5419 | `` |
| upstream_nearest_turn | `published_policy_upstream_main_backlash_seed0` | 92-103 | 12 | 2 | 0.0651 | 50.0000 | 91.6667 | 50.0000 | 3.4202 | `` |
| upstream_nearest_turn | `published_policy_upstream_main_backlash_seed6` | 92-103 | 12 | 2 | 0.0645 | 50.0000 | 91.6667 | 50.0000 | 3.5719 | `` |
| upstream_nearest_turn | `published_policy_upstream_main_backlash_seed2` | 38-49 | 12 | 2 | 0.0471 | 41.6667 | 91.6667 | 33.3333 | 3.2357 | `` |
| straight_x004 | `published_policy_upstream_main_backlash_x004_seed0` | 8-19 | 12 | 2 | 0.0461 | 25.0000 | 58.3333 | 25.0000 | 3.0366 | `` |
| upstream_nearest_turn | `published_policy_upstream_main_backlash_seed2` | 64-75 | 12 | 2 | 0.0460 | 50.0000 | 75.0000 | 33.3333 | 3.4640 | `` |
| upstream_nearest_turn | `published_policy_upstream_main_backlash_seed1` | 92-103 | 12 | 2 | 0.0452 | 41.6667 | 66.6667 | 25.0000 | 3.2434 | `` |
| straight_x008 | `published_policy_upstream_main_backlash_x008_seed6` | 200-209 | 10 | 1 | 0.0875 | 60.0000 | 100.0000 | 60.0000 | 3.3272 | `` |
| straight_x008 | `published_policy_upstream_main_backlash_x008_seed7` | 120-129 | 10 | 1 | 0.0829 | 60.0000 | 100.0000 | 60.0000 | 3.5446 | `` |
| straight_x008 | `published_policy_upstream_main_backlash_x008_seed5` | 38-47 | 10 | 1 | 0.0814 | 60.0000 | 100.0000 | 60.0000 | 3.2076 | `` |
| straight_x008 | `published_policy_upstream_main_backlash_x008_seed1` | 228-237 | 10 | 1 | 0.0805 | 50.0000 | 90.0000 | 50.0000 | 3.6779 | `` |
| upstream_nearest_turn | `published_policy_upstream_main_backlash_seed3` | 120-129 | 10 | 1 | 0.0768 | 50.0000 | 100.0000 | 50.0000 | 3.0298 | `` |
| upstream_nearest_turn | `published_policy_upstream_main_backlash_seed6` | 174-183 | 10 | 1 | 0.0759 | 50.0000 | 100.0000 | 50.0000 | 2.9700 | `` |
| upstream_nearest_turn | `published_policy_upstream_main_backlash_seed6` | 120-129 | 10 | 1 | 0.0758 | 50.0000 | 100.0000 | 50.0000 | 3.1810 | `` |
| straight_x008 | `published_policy_upstream_main_backlash_x008_seed2` | 38-47 | 10 | 1 | 0.0757 | 60.0000 | 90.0000 | 60.0000 | 3.6483 | `` |
| upstream_nearest_turn | `published_policy_upstream_main_backlash_seed0` | 66-75 | 10 | 1 | 0.0757 | 50.0000 | 100.0000 | 50.0000 | 2.8396 | `` |
| straight_x008 | `published_policy_upstream_main_backlash_x008_seed3` | 228-237 | 10 | 1 | 0.0752 | 60.0000 | 100.0000 | 60.0000 | 3.2131 | `` |
| upstream_nearest_turn | `published_policy_upstream_main_backlash_seed7` | 228-237 | 10 | 1 | 0.0751 | 50.0000 | 100.0000 | 50.0000 | 3.2071 | `` |

## Interpretation

- A passing stitch run means the merged span still satisfies the same window criteria.
- If pass runs do not reach 25 ticks, the short snippets should be treated as local hints, not a BC source.
- If pass runs reach 25-50 ticks, the next step is to export a compact manifest and replay the stitched targets before BC.
