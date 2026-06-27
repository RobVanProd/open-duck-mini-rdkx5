# Reference Lock Signal

status: `PASS_REFERENCE_SIGNAL_COHERENT`
reference: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/reference_motion_x004_override.pkl`
command: `{'x': 0.04, 'y': 0.0, 'yaw': 0.0}`
period_steps: `27`

## Velocity

- linvel_x_mean: `0.0426`
- linvel_x_p95: `0.0641`
- linvel_y_mean: `-0.0021`
- linvel_y_abs_p95: `0.2350`
- angvel_z_abs_p95: `0.0001`

## Progress

- progress_ratio: `1.0512`
- failure_min_ratio: `0.2000`
- forward_required_ratio: `0.5500`

## Imitation Signal

- ideal_imitation_raw: `6.0000`
- ideal_imitation_scaled: `24.0000`
- pre_terminal_unclipped_sum_mean: `50.8050`

## Contacts

- left_true_count: `19`
- right_true_count: `18`
- transitions_per_period: `4`
- patterns: `{'(0, 1)': 8, '(1, 0)': 9, '(1, 1)': 10}`

## Warnings

- reference lateral p95_abs is large relative to command_x

## Interpretation

- `PASS_REFERENCE_SIGNAL_COHERENT` means the reference itself clears the analytic command-progress check.
- This does not mean PPO can discover or preserve the reference; V20 showed it did not.
- Large lateral velocity warnings should be carried into any later reference-lock or behavior-cloning work.
