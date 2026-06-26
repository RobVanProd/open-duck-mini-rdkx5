# Relabelled Selector Replay Manifest

status: `PASS_SELECTOR_REPLAY_MANIFEST_READY`

This manifest converts the top continuity-score runs into replayable selector spans. It does not train, step simulation, deploy, SSH, run robot tests, or change runtime behavior.

## Source

- continuity_score: `outputs/analysis/relabelled_selector_continuity_score.json`
- continuity_status: `PASS_SELECTOR_CONTINUITY_50_TICKS`
- max_runs: `8`
- min_span_ticks: `50`
- right_knee_cap_rad_s: `3.61`

## Entries

| source | ticks | span | relabel | vx | single_% | move_env_% | pitch_p95 |
|---|---:|---:|---|---:|---:|---:|---:|
| published_policy_command_straight_x008_seed1 | 154-249 | 96 | `right_knee_rate_cap` | 0.0719 | 52.0833 | 92.7083 | 3.6100 |
| published_policy_command_straight_x008_seed5 | 38-121 | 84 | `right_knee_rate_cap` | 0.0715 | 54.7619 | 94.0476 | 3.6100 |
| published_policy_command_straight_x008_seed0 | 72-149 | 78 | `right_knee_rate_cap` | 0.0717 | 56.4103 | 92.3077 | 3.6100 |
| published_policy_command_straight_x008_seed7 | 100-175 | 76 | `right_knee_rate_cap` | 0.0741 | 52.6316 | 94.7368 | 3.6100 |
| published_policy_command_straight_x008_seed3 | 180-249 | 70 | `right_knee_rate_cap` | 0.0685 | 51.4286 | 95.7143 | 3.6100 |
| published_policy_command_straight_x008_seed0 | 180-249 | 70 | `right_knee_rate_cap` | 0.0679 | 50.0000 | 95.7143 | 3.6100 |
| published_policy_command_straight_x008_seed2 | 38-95 | 58 | `right_knee_rate_cap` | 0.0716 | 56.8966 | 93.1034 | 3.6100 |
| published_policy_command_straight_x008_seed7 | 18-67 | 50 | `right_knee_rate_cap` | 0.0741 | 52.0000 | 92.0000 | 3.6100 |

## Interpretation

- A pass here only means the continuity-score runs were converted into a replay manifest.
- The next gate is closed-loop sim replay with `run_target_sequence_replay_smoke.py`.
