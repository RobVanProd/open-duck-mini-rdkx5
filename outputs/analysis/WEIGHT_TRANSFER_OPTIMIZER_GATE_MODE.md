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
| 0 | HOLD_NO_SEED_ROBUST_TARGETS | 0 | opt_i00_c000 | -0.3634 | -0.3450 | -0.0008 | 0.0016 | 0.1222 | `double_support_dominates, high_lateral_velocity, low_forward_velocity` |
| 1 | HOLD_NO_SEED_ROBUST_TARGETS | 0 | opt_i01_c000 | -0.3612 | -0.3550 | -0.0036 | 0.0043 | 0.1106 | `double_support_dominates, low_forward_velocity, too_little_single_support` |

## Interpretation

- This is an offline optimizer probe, not training.
- `PASS_OPTIMIZER_FOUND_ROBUST_TARGET` requires at least one seed-robust scored target.
- Do not build a target dataset from optimizer traces until the 100/150 tick gates pass.
