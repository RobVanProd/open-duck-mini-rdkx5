# Low-Command Reward Signal

status: `PASS_FORWARD_REWARDED_ABOVE_STANDSTILL`
command_x: `0.04`
pre_failure_step: `49`
terminal_step: `50`
reward_overrides_json: `outputs/analysis/v18_a100_staged_plan.json`
reward_overrides_phase: `phase1_x004_dense_progress_discovery`

## Verdict

Forward local velocity is rewarded above standing before the command-progress terminal gate. This supports the exploration / optimization-landscape hypothesis rather than a simple reward-sign or reward-weight signal bug.

## Pre-Failure Reward Table

| vx | tracking | progress | shortfall_cost | wrong_dir_cost | window_progress | window_shortfall | failure | reward | delta_vs_stand |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| -0.0800 | 0.0003 | 0.0000 | -842.7000 | -480.0000 | -24.0000 | -540.8000 | -0.0000 | -20.0000 | -18.6314 |
| -0.0400 | 0.2028 | 0.0000 | -326.7000 | -120.0000 | -12.0000 | -204.8000 | -0.0000 | -13.2659 | -11.8974 |
| -0.0200 | 2.0911 | 0.0000 | -158.7000 | -30.0000 | -6.0000 | -96.8000 | -0.0000 | -5.7882 | -4.4196 |
| 0.0000 | 11.0711 | 0.0000 | -50.7000 | -0.0000 | 0.0000 | -28.8000 | -0.0000 | -1.3686 | 0.0000 |
| 0.0100 | 19.8394 | 15.0000 | -19.2000 | -0.0000 | 3.0000 | -9.8000 | -0.0000 | 0.1768 | 1.5454 |
| 0.0200 | 30.0943 | 30.0000 | -2.7000 | -0.0000 | 6.0000 | -0.8000 | -0.0000 | 1.2519 | 2.6205 |
| 0.0260 | 35.6709 | 39.0000 | -0.0000 | -0.0000 | 7.8000 | -0.0000 | -0.0000 | 1.6494 | 3.0180 |
| 0.0400 | 42.0000 | 60.0000 | -0.0000 | -0.0000 | 12.0000 | -0.0000 | -0.0000 | 2.2800 | 3.6486 |
| 0.0600 | 30.0943 | 60.0000 | -0.0000 | -0.0000 | 18.0000 | -0.0000 | -0.0000 | 2.1619 | 3.5305 |
| 0.0680 | 21.8530 | 60.0000 | -0.0000 | -0.0000 | 20.4000 | -0.0000 | -0.0000 | 2.0451 | 3.4136 |
| 0.0800 | 11.0711 | 60.0000 | -0.0000 | -0.0000 | 24.0000 | -0.0000 | -0.0000 | 1.8989 | 3.2675 |

## Terminal-Step Check

At the command-progress terminal step, low-progress velocities are allowed to become strongly negative if the phase enables command-progress failure. This table is included to verify that the backstop is active.

| vx | progress_ratio | failure_term | reward |
|---:|---:|---:|---:|
| -0.0800 | -2.0000 | -160.0000 | -20.0000 |
| -0.0400 | -1.0000 | -160.0000 | -16.4659 |
| -0.0200 | -0.5000 | -160.0000 | -8.9882 |
| 0.0000 | 0.0000 | -160.0000 | -4.5686 |
| 0.0100 | 0.2500 | -0.0000 | 0.1768 |
| 0.0200 | 0.5000 | -0.0000 | 1.2519 |
| 0.0260 | 0.6500 | -0.0000 | 1.6494 |
| 0.0400 | 1.0000 | -0.0000 | 2.2800 |
| 0.0600 | 1.5000 | -0.0000 | 2.1619 |
| 0.0680 | 1.7000 | -0.0000 | 2.0451 |
| 0.0800 | 2.0000 | -0.0000 | 1.8989 |

## Gate Inputs

- standstill_reward: `-1.3685784039827897`
- required_vx: `0.026000000000000002`
- required_vx_reward: `1.6494187523786839`
- command_vx: `0.04`
- command_vx_reward: `2.2800000000000002`
- required_minus_standstill: `3.0179971563614734`
- command_minus_standstill: `3.64857840398279`

## Stop Condition

No further reward-weight tuning is authorized solely to make standing worse. The immediate reward signal already prefers forward motion; the next decisive experiment is an imitation/reference gait seed test.
