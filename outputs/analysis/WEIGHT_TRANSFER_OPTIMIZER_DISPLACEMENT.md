# Weight-Transfer Optimizer

status: `HOLD_OPTIMIZER_NO_ROBUST_TARGET`
command_x: `0.04`
duration_s: `2.0`
seeds: `0,2`
iterations: `2`
candidates_per_iteration: `4`

## Iterations

| iter | status | robust | best_mode | min_score | mean_score | seed0_vx | seed2_vx | seed2_vy95 | seed2_failures |
|---:|---|---:|---|---:|---:|---:|---:|---:|---|
| 0 | HOLD_NO_SEED_ROBUST_TARGETS | 0 | opt_i00_c001 | -1.3551 | -1.3447 | -0.0035 | 0.0015 | 0.1587 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| 1 | HOLD_NO_SEED_ROBUST_TARGETS | 0 | opt_i01_c002 | -1.4535 | -1.1798 | -0.0036 | 0.0060 | 0.1018 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |

## Interpretation

- This is an offline optimizer probe, not training.
- `PASS_OPTIMIZER_FOUND_ROBUST_TARGET` requires at least one seed-robust scored target.
- Do not build a target dataset from optimizer traces until the 100/150 tick gates pass.
