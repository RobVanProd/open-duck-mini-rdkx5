# Contact Transfer Blocker Audit

status: `HOLD_TARGET_SOURCE_DOUBLE_SUPPORT`

This offline audit separates two different failure explanations:

1. the target/demo source itself mostly stays in double support, or
2. the target/demo source asks for single support but closed-loop execution cannot realize it.

No simulation, training, robot SSH, deployment, or hardware motion was run.

## Target Fragment Sources

| source | status | curated | wt-pass | double support mean/p95 | single support mean/p95 | min side mean | sent vel p95 mean |
|---|---|---:|---:|---:|---:|---:|---:|
| target_generator_dynamic_roll_lateral_fix_robust_modes_curation_50.json | `PASS_CURATED_DATASET_SEED_READY` | 9 | 0 | 92.67/94.00 | 7.33/11.20 | 1.78 | 0.5133 |
| target_generator_dynamic_roll_lateral_fix_window_curation_100.json | `HOLD_INSUFFICIENT_CURATED_WINDOWS` | 0 | 0 | NA/NA | NA/NA | NA | NA |
| target_generator_dynamic_roll_lateral_fix_window_curation_150.json | `HOLD_INSUFFICIENT_CURATED_WINDOWS` | 0 | 0 | NA/NA | NA/NA | NA | NA |

Weight-transfer target criteria used by this audit:

- double_support_pct <= `75.0`
- single_support_pct >= `20.0`
- min_each_single_support_pct >= `5.0`

## Best Available Weight-Transfer Rows

| source | tier | seed | ticks | vx | double | single | min side | reasons |
|---|---|---|---|---:|---:|---:|---:|---|
| target_generator_dynamic_roll_lateral_fix_robust_modes_curation_50.json | `PASS_CURATED_SEED_WINDOW` | `seed_000` | `5-54` | 0.0423 | 88.00 | 12.00 | 6.00 | `` |
| target_generator_dynamic_roll_lateral_fix_robust_modes_curation_50.json | `PASS_CURATED_SEED_WINDOW` | `seed_000` | `5-54` | 0.0416 | 90.00 | 10.00 | 4.00 | `` |
| target_generator_dynamic_roll_lateral_fix_robust_modes_curation_50.json | `PASS_CURATED_SEED_WINDOW` | `seed_000` | `5-54` | 0.0401 | 92.00 | 8.00 | 2.00 | `` |
| target_generator_dynamic_roll_lateral_fix_window_curation_100.json | `REJECT_DATASET_SEED` | `seed_000` | `0-99` | 0.0216 | 91.00 | 9.00 | 2.00 | `low_forward_velocity` |
| target_generator_dynamic_roll_lateral_fix_window_curation_100.json | `REJECT_DATASET_SEED` | `seed_000` | `0-99` | 0.0211 | 91.00 | 9.00 | 3.00 | `low_forward_velocity` |
| target_generator_dynamic_roll_lateral_fix_window_curation_100.json | `REJECT_DATASET_SEED` | `seed_002` | `0-99` | 0.0206 | 92.00 | 8.00 | 2.00 | `low_forward_velocity, high_lateral_velocity` |

## Reference Rollout Contact Mismatch

| run | samples | mismatch | actual double | reference double | actual single | reference single | top mismatch |
|---|---:|---:|---:|---:|---:|---:|---|
| reference_motion_rollout_v20_traces | 635 | 68.03 | 73.86 | 35.43 | 23.94 | 64.57 | `01->11` 25.35 |
| reference_motion_rollout_v20_projected_traces | 664 | 67.77 | 75.90 | 35.54 | 22.44 | 64.46 | `10->11` 25.75 |
| reference_motion_rollout_v20_projected_phase5_traces | 653 | 67.23 | 74.89 | 37.52 | 23.12 | 62.48 | `01->11` 24.66 |
| reference_motion_rollout_v20_projected_phase19_traces | 555 | 67.57 | 74.41 | 38.38 | 23.60 | 61.62 | `10->11` 25.41 |

## Decision

The current curated dynamic-roll/lateral-fix fragments do not clear
the weight-transfer criteria. Their short successful windows mostly
move forward while staying in double support, and longer 100/150 tick
windows have no curated passes.

Next branch: do not train BC/PPO from these fragments as if they are
stepping demonstrations. Build or optimize a target source that
explicitly produces sustained single-support alternation first.
