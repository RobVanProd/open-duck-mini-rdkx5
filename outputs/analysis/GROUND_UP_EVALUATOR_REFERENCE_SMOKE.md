# Ground-Up Policy Evaluation

status: `HOLD_GAIT_NOT_EMERGED`
execution: `CPU_ONLY`

## Aggregate

- runs: `2`
- moving_runs: `1`
- zero_command_runs: `1`
- moving_emergence_pass: `False`
- zero_command_finite_recorded: `True`
- checkpoint_emergence_pass: `False`

## Runs

| command x | seed | evaluator | emergence | termination | dx m | transitions | reasons |
|---:|---:|---|---|---|---:|---:|---|
| 0.0 | 100 | `HOLD_CANDIDATE_TRACKING` | `False` | `duration_complete` | 0.0012172088027000427 | 1 | contract_window_too_short_for_gait_classification |
| 0.08 | 100 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | `False` | `duration_complete` | 0.0012155044823884964 | 1 | contract_window_too_short_for_gait_classification, no_positive_mean_forward_velocity |
