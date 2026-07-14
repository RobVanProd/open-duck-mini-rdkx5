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
| 0.074 | 100 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | `False` | `duration_complete` | -0.06800767406821251 | 5 | no_positive_forward_displacement, no_positive_mean_forward_velocity |
| 0.074 | 101 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `False` | `fall_or_nan` | -0.148618271574378 | 8 | standing_collapse_or_nonfinite, no_positive_forward_displacement, no_positive_mean_forward_velocity |
| 0.08 | 100 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | `False` | `duration_complete` | -0.06800767406821251 | 5 | no_positive_forward_displacement, no_positive_mean_forward_velocity |
| 0.08 | 101 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `False` | `fall_or_nan` | -0.148618271574378 | 8 | standing_collapse_or_nonfinite, no_positive_forward_displacement, no_positive_mean_forward_velocity |
