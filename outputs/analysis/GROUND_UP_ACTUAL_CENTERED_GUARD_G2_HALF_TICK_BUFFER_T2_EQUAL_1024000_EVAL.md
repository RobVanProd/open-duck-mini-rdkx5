# Ground-Up Policy Evaluation

status: `HOLD_GAIT_NOT_EMERGED`
execution: `CPU_ONLY`

## Aggregate

- runs: `6`
- moving_runs: `6`
- zero_command_runs: `0`
- moving_emergence_pass: `False`
- zero_command_finite_recorded: `True`
- checkpoint_emergence_pass: `False`

## Runs

| command x | seed | evaluator | emergence | termination | dx m | transitions | reasons |
|---:|---:|---|---|---|---:|---:|---|
| 0.074 | 100 | `PASS_CANDIDATE_SIM_GATE` | `True` | `duration_complete` | 1.0821442233631389 | 147 | none |
| 0.074 | 101 | `PASS_CANDIDATE_SIM_GATE` | `True` | `duration_complete` | 1.0821442233631389 | 147 | none |
| 0.077 | 100 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `False` | `fall_or_nan` | 1.4089259113464505 | 160 | standing_collapse_or_nonfinite |
| 0.077 | 101 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `False` | `fall_or_nan` | 1.4089259113464505 | 160 | standing_collapse_or_nonfinite |
| 0.08 | 100 | `PASS_CANDIDATE_SIM_GATE` | `True` | `duration_complete` | 1.158334684818983 | 151 | none |
| 0.08 | 101 | `PASS_CANDIDATE_SIM_GATE` | `True` | `duration_complete` | 1.158334684818983 | 151 | none |
