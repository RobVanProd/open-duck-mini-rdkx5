# Relabelled Selector Continuity Score

status: `PASS_SELECTOR_CONTINUITY_50_TICKS`

This is an offline continuity score over the relabelled balanced selector manifest. It does not train, step simulation, deploy, SSH, run robot tests, or change runtime behavior.

## Summary

- runs: `101`
- pass_runs: `98`
- max_run_span_ticks: `150`
- max_pass_run_span_ticks: `96`
- pass_run_25_count: `20`
- pass_run_50_count: `11`
- pass_run_with_relabel_count: `92`

## Longest Passing Runs

| source | ticks | span | entries | relabel | vx | single_% | move_env_% | move_single_env_% | pitch_p95 | reasons |
|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---|
| published_policy_command_straight_x008_seed1 | 154-249 | 96 | 29 | `True` | 0.0719 | 52.0833 | 92.7083 | 48.9583 | 3.6100 | `` |
| published_policy_command_straight_x008_seed5 | 38-121 | 84 | 27 | `True` | 0.0715 | 54.7619 | 94.0476 | 50.0000 | 3.6100 | `` |
| published_policy_command_straight_x008_seed0 | 72-149 | 78 | 25 | `True` | 0.0717 | 56.4103 | 92.3077 | 52.5641 | 3.6100 | `` |
| published_policy_command_straight_x008_seed7 | 100-175 | 76 | 24 | `True` | 0.0741 | 52.6316 | 94.7368 | 48.6842 | 3.6100 | `` |
| published_policy_command_straight_x008_seed3 | 180-249 | 70 | 23 | `True` | 0.0685 | 51.4286 | 95.7143 | 48.5714 | 3.6100 | `` |
| published_policy_command_straight_x008_seed0 | 180-249 | 70 | 20 | `True` | 0.0679 | 50.0000 | 95.7143 | 47.1429 | 3.6100 | `` |
| published_policy_command_straight_x008_seed2 | 38-95 | 58 | 19 | `True` | 0.0716 | 56.8966 | 93.1034 | 51.7241 | 3.6100 | `` |
| published_policy_command_straight_x008_seed7 | 18-67 | 50 | 14 | `True` | 0.0741 | 52.0000 | 92.0000 | 48.0000 | 3.6100 | `` |
| published_policy_command_straight_x008_seed3 | 100-149 | 50 | 15 | `True` | 0.0714 | 54.0000 | 90.0000 | 50.0000 | 3.6100 | `` |
| published_policy_command_straight_x008_seed5 | 154-203 | 50 | 15 | `True` | 0.0688 | 56.0000 | 96.0000 | 54.0000 | 3.6100 | `` |
| published_policy_command_straight_x008_seed2 | 100-149 | 50 | 15 | `True` | 0.0687 | 52.0000 | 94.0000 | 48.0000 | 3.6100 | `` |
| published_policy_command_straight_x008_seed2 | 154-201 | 48 | 14 | `True` | 0.0712 | 52.0833 | 91.6667 | 47.9167 | 3.6100 | `` |
| published_policy_command_turning_x0074_yneg0037_yawneg0074_seed2 | 172-217 | 46 | 8 | `True` | 0.0661 | 60.8696 | 95.6522 | 56.5217 | 3.6100 | `` |
| published_policy_command_turning_x0074_yneg0037_yawneg0074_seed6 | 118-163 | 46 | 10 | `True` | 0.0654 | 60.8696 | 95.6522 | 56.5217 | 3.6100 | `` |
| published_policy_command_straight_x008_seed5 | 208-249 | 42 | 12 | `True` | 0.0668 | 50.0000 | 95.2381 | 47.6190 | 3.6100 | `` |
| published_policy_command_straight_x008_seed2 | 208-249 | 42 | 12 | `True` | 0.0648 | 52.3810 | 95.2381 | 50.0000 | 3.6100 | `` |
| published_policy_command_straight_x008_seed0 | 10-41 | 32 | 9 | `True` | 0.0717 | 53.1250 | 93.7500 | 46.8750 | 3.6100 | `` |
| published_policy_command_straight_x008_seed6 | 38-67 | 30 | 8 | `True` | 0.0681 | 56.6667 | 93.3333 | 50.0000 | 3.6100 | `` |
| published_policy_command_straight_x008_seed1 | 64-93 | 30 | 8 | `True` | 0.0617 | 53.3333 | 86.6667 | 43.3333 | 3.6100 | `` |
| published_policy_command_turning_x0074_yneg0037_yawneg0074_seed2 | 4-29 | 26 | 7 | `True` | 0.0871 | 42.3077 | 84.6154 | 38.4615 | 3.6100 | `` |
| published_policy_command_straight_x008_seed7 | 72-95 | 24 | 7 | `True` | 0.0772 | 50.0000 | 91.6667 | 45.8333 | 3.6100 | `` |
| published_policy_command_straight_x008_seed1 | 126-149 | 24 | 7 | `True` | 0.0725 | 50.0000 | 87.5000 | 45.8333 | 3.6100 | `` |
| published_policy_command_straight_x008_seed5 | 126-149 | 24 | 7 | `True` | 0.0704 | 50.0000 | 91.6667 | 45.8333 | 3.6100 | `` |
| published_policy_command_straight_x008_seed3 | 72-95 | 24 | 7 | `True` | 0.0699 | 50.0000 | 91.6667 | 45.8333 | 3.6100 | `` |
| published_policy_command_straight_x008_seed4 | 180-203 | 24 | 7 | `True` | 0.0661 | 50.0000 | 91.6667 | 45.8333 | 3.6100 | `` |
| published_policy_command_straight_x008_seed1 | 100-121 | 22 | 7 | `True` | 0.0766 | 50.0000 | 90.9091 | 45.4545 | 3.6100 | `` |
| published_policy_command_straight_x008_seed6 | 72-93 | 22 | 6 | `True` | 0.0758 | 45.4545 | 90.9091 | 40.9091 | 3.6100 | `` |
| published_policy_command_straight_x008_seed4 | 208-229 | 22 | 7 | `True` | 0.0745 | 50.0000 | 90.9091 | 45.4545 | 3.6100 | `` |
| published_policy_command_straight_x008_seed3 | 154-175 | 22 | 6 | `True` | 0.0732 | 50.0000 | 90.9091 | 45.4545 | 3.6100 | `` |
| published_policy_command_straight_x008_seed0 | 154-175 | 22 | 7 | `True` | 0.0714 | 50.0000 | 90.9091 | 45.4545 | 3.6100 | `` |
| published_policy_command_straight_x008_seed0 | 46-67 | 22 | 7 | `True` | 0.0703 | 50.0000 | 90.9091 | 45.4545 | 3.6100 | `` |
| published_policy_command_turning_x0074_yneg0037_yawneg0074_seed3 | 38-59 | 22 | 4 | `True` | 0.0571 | 45.4545 | 86.3636 | 36.3636 | 3.6100 | `` |
| published_policy_command_turning_x0074_yneg0037_yawneg0074_seed0 | 64-83 | 20 | 4 | `True` | 0.0699 | 70.0000 | 95.0000 | 65.0000 | 3.6100 | `` |
| published_policy_command_turning_x0074_yneg0037_yawneg0074_seed6 | 64-83 | 20 | 4 | `True` | 0.0696 | 70.0000 | 95.0000 | 65.0000 | 3.6100 | `` |
| published_policy_command_turning_x0074_yneg0037_yawneg0074_seed6 | 172-191 | 20 | 4 | `True` | 0.0695 | 70.0000 | 95.0000 | 65.0000 | 3.6100 | `` |
| published_policy_command_turning_x0074_yneg0037_yawneg0074_seed3 | 118-137 | 20 | 4 | `True` | 0.0693 | 70.0000 | 95.0000 | 65.0000 | 3.6100 | `` |
| published_policy_command_turning_x0074_yneg0037_yawneg0074_seed0 | 226-245 | 20 | 4 | `True` | 0.0689 | 70.0000 | 95.0000 | 65.0000 | 3.6100 | `` |
| published_policy_command_turning_x0074_yneg0037_yawneg0074_seed7 | 172-191 | 20 | 4 | `True` | 0.0687 | 70.0000 | 95.0000 | 65.0000 | 3.6100 | `` |
| published_policy_command_turning_x0074_yneg0037_yawneg0074_seed5 | 118-137 | 20 | 4 | `True` | 0.0685 | 70.0000 | 95.0000 | 65.0000 | 3.6100 | `` |
| published_policy_command_turning_x0074_yneg0037_yawneg0074_seed1 | 226-245 | 20 | 4 | `True` | 0.0680 | 70.0000 | 95.0000 | 65.0000 | 3.6100 | `` |
| published_policy_command_turning_x0074_yneg0037_yawneg0074_seed7 | 226-245 | 20 | 4 | `True` | 0.0673 | 70.0000 | 95.0000 | 65.0000 | 3.6100 | `` |
| published_policy_command_turning_x0074_yneg0037_yawneg0074_seed3 | 172-191 | 20 | 4 | `True` | 0.0669 | 70.0000 | 95.0000 | 65.0000 | 3.6100 | `` |
| published_policy_command_turning_x0074_yneg0037_yawneg0074_seed2 | 118-137 | 20 | 4 | `True` | 0.0664 | 70.0000 | 95.0000 | 65.0000 | 3.6100 | `` |
| published_policy_command_turning_x0074_yneg0037_yawneg0074_seed3 | 226-245 | 20 | 4 | `True` | 0.0658 | 70.0000 | 95.0000 | 65.0000 | 3.6100 | `` |
| published_policy_command_turning_x0074_yneg0037_yawneg0074_seed5 | 64-83 | 20 | 4 | `True` | 0.0655 | 70.0000 | 95.0000 | 65.0000 | 3.6100 | `` |
| published_policy_command_turning_x0074_yneg0037_yawneg0074_seed5 | 226-245 | 20 | 4 | `True` | 0.0651 | 70.0000 | 95.0000 | 65.0000 | 3.6100 | `` |
| published_policy_command_turning_x0074_yneg0037_yawneg0074_seed7 | 118-137 | 20 | 4 | `True` | 0.0649 | 70.0000 | 95.0000 | 65.0000 | 3.6100 | `` |
| published_policy_command_turning_x0074_yneg0037_yawneg0074_seed5 | 172-191 | 20 | 4 | `True` | 0.0647 | 70.0000 | 95.0000 | 65.0000 | 3.6100 | `` |
| published_policy_command_turning_x0074_yneg0037_yawneg0074_seed6 | 226-245 | 20 | 4 | `True` | 0.0646 | 70.0000 | 95.0000 | 65.0000 | 3.6100 | `` |
| published_policy_command_turning_x0074_yneg0037_yawneg0074_seed2 | 226-245 | 20 | 4 | `True` | 0.0644 | 70.0000 | 95.0000 | 65.0000 | 3.6100 | `` |

## Interpretation

- Passing 25-50 ticks here means the balanced manifest has temporally local source runs worth replaying in sim.
- A hold means the source has coverage but still lacks sustained continuity and needs a selector/generator before training.
