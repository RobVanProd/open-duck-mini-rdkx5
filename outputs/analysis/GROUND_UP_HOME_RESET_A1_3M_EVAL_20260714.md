# Ground-Up Policy Evaluation

status: `HOLD_GAIT_NOT_EMERGED`
execution: `CPU_ONLY`

## Aggregate

- runs: `4`
- moving_runs: `4`
- zero_command_runs: `0`
- moving_emergence_pass: `False`
- zero_command_finite_recorded: `False`
- checkpoint_emergence_pass: `False`

## Runs

| command x | seed | evaluator | emergence | termination | dx m | transitions | reasons |
|---:|---:|---|---|---|---:|---:|---|
| 0.074 | 100 | `HOLD_CANDIDATE_TRACKING` | `True` | `duration_complete` | 0.055993106834357605 | 8 | none |
| 0.074 | 101 | `HOLD_CANDIDATE_TRACKING` | `True` | `duration_complete` | 0.055993106834357605 | 8 | none |
| 0.08 | 100 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | `False` | `duration_complete` | -0.20451154336333274 | 8 | no_positive_forward_displacement, no_positive_mean_forward_velocity, constant_saturated_action_vector |
| 0.08 | 101 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | `False` | `duration_complete` | -0.20451154336333274 | 8 | no_positive_forward_displacement, no_positive_mean_forward_velocity, constant_saturated_action_vector |
