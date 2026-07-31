# Ground-Up Policy Evaluation

status: `HOLD_GAIT_NOT_EMERGED`
execution: `CPU_ONLY`

## Aggregate

- runs: `4`
- moving_runs: `3`
- zero_command_runs: `1`
- moving_emergence_pass: `False`
- zero_command_finite_recorded: `False`
- checkpoint_emergence_pass: `False`

## Runs

| command x | seed | evaluator | emergence | termination | dx m | transitions | reasons |
|---:|---:|---|---|---|---:|---:|---|
| 0.0 | 167931544 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `False` | `fall_or_nan` | -0.34953977160155775 | 5 | standing_collapse_or_nonfinite |
| 0.074 | 167931544 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `False` | `fall_or_nan` | -0.33007572416216135 | 20 | standing_collapse_or_nonfinite, no_positive_forward_displacement, no_positive_mean_forward_velocity |
| 0.077 | 167931544 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `False` | `fall_or_nan` | -0.31867464201524853 | 14 | standing_collapse_or_nonfinite, no_positive_forward_displacement, no_positive_mean_forward_velocity |
| 0.08 | 167931544 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `False` | `fall_or_nan` | -0.30724784079939127 | 18 | standing_collapse_or_nonfinite, no_positive_forward_displacement, no_positive_mean_forward_velocity |
