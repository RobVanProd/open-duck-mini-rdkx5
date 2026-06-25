# Contact Weight-Transfer Sequence Optimizer

status: `HOLD_HORIZON_SEQUENCE_NO_ROBUST_TARGET`
command_x: `0.0400`
duration_s: `3.0000`
seeds: `0,2`
horizon_ticks: `150`
iterations: `1`
candidates_per_iteration: `4`

## Iterations

| iter | rollout_status | score_status | robust | best_mode | min_score | mean_score | seed0_vx | seed2_vx | seed2_failures |
|---:|---|---|---:|---|---:|---:|---:|---:|---|
| 0 | `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION` | `HOLD_NO_SEED_ROBUST_TARGETS` | 0 | horizon_i00_c002 | -1.1349 | -1.0366 | -0.0035 | 0.0038 | `double_support_dominates, high_lateral_velocity, low_forward_velocity, single_support_not_balanced, too_little_single_support` |

## Interpretation

- This is a bounded offline target-source optimizer, not PPO/BC training.
- It generates finite-horizon target tables and scores realized closed-loop contacts.
- Passing would only authorize a reviewed target-dataset smoke branch.
- No robot tests, SSH, deploy, training, or runtime behavior changes were performed.
