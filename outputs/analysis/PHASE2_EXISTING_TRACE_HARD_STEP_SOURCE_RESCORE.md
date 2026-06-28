# Phase 2 Existing Trace Hard-Step Source Rescore

status: `PASS_HARD_STEP_SOURCE_FOUND`

## Criteria

- window_sizes: `[100, 150]`
- seeds: `[2, 4]`
- command_x: `0.08`
- min_mean_vx: `0.04`
- max_double_support_pct: `75.0`
- min_single_support_pct: `20.0`
- min_each_single_support_pct: `5.0`
- min_contact_transitions: `2`
- min_swing_segments_per_foot: `1`
- min_swing_rel_x_range_p95_m: `0.003`
- min_swing_peak_lift_m: `0.005`
- max_sent_velocity_p95: `2.5`
- max_tracking_p95: `0.2`
- dt_s: `0.02`

## Root Summary

| root | files | windows | pass_each_seed | seed2_best_vx | seed2_failures | seed4_best_vx | seed4_failures |
|---|---:|---:|---|---:|---|---:|---|
| `outputs/analysis/corrected_bridge_best_walk_reroll_x008/best_walk` | 8 | 4 | `False` | 0.0464 | `high_sent_target_velocity` | 0.0459 | `PASS` |
| `outputs/analysis/dagger5_recovery_teacher_relabel_x008_traces` | 8 | 4 | `False` | 0.0316 | `low_forward_velocity,low_swing_rel_x_range` | 0.0247 | `low_forward_velocity` |
| `outputs/analysis/dagger5_recovery_trace_x008_fitted_10s/dagger5` | 8 | 4 | `False` | 0.0316 | `low_forward_velocity,low_swing_rel_x_range` | 0.0247 | `low_forward_velocity` |
| `outputs/analysis/deployable_source_vx_policy_validation_rate_reg_trace_fitted_backlash/dagger2_rate_reg` | 8 | 4 | `True` | 0.0467 | `PASS` | 0.0415 | `PASS` |
| `outputs/analysis/live_oracle_dagger_phase_student/iter_000/rollouts_x008/student` | 8 | 4 | `True` | 0.0467 | `PASS` | 0.0436 | `PASS` |
| `outputs/analysis/live_oracle_dagger_phase_student/iter_000/relabel_x008/rollouts_x008/student` | 8 | 4 | `True` | 0.0467 | `PASS` | 0.0436 | `PASS` |
| `outputs/analysis/live_oracle_dagger_phase_student/iter_001/rollouts_x008/student` | 8 | 4 | `True` | 0.0571 | `PASS` | 0.0544 | `PASS` |
| `outputs/analysis/live_oracle_dagger_phase_student/iter_001/relabel_x008/rollouts_x008/student` | 8 | 4 | `True` | 0.0571 | `PASS` | 0.0544 | `PASS` |
| `outputs/analysis/live_oracle_dagger_phase_student/iter_002/relabel_x008/rollouts_x008/student` | 8 | 4 | `True` | 0.0571 | `PASS` | 0.0544 | `PASS` |
| `outputs/analysis/live_oracle_dagger_phase_student/iter_003/relabel_x008/rollouts_x008/student` | 8 | 4 | `True` | 0.0571 | `PASS` | 0.0544 | `PASS` |
| `outputs/analysis/phase2_stage_c7_35120_trace_pass_fail_cpu/c7_35120` | 2 | 4 | `False` | 0.0260 | `low_forward_velocity,low_swing_rel_x_range` | 0.0147 | `double_support_dominates,low_forward_velocity,low_swing_peak_lift,low_swing_rel_x_range,single_support_not_balanced,too_few_swing_segments,too_little_single_support` |
| `outputs/analysis/phase2_stage_c7_35120_trace_pass_fail_v2_cpu/c7_35120` | 2 | 4 | `False` | 0.0260 | `low_forward_velocity,low_swing_rel_x_range` | 0.0147 | `double_support_dominates,low_forward_velocity,low_swing_peak_lift,low_swing_rel_x_range,single_support_not_balanced,too_few_swing_segments,too_little_single_support` |
| `outputs/analysis/phase2_stage_c7_35120_trace_pass_fail_v3_cpu/c7_35120` | 2 | 4 | `False` | 0.0260 | `low_forward_velocity,low_swing_rel_x_range` | 0.0147 | `double_support_dominates,low_forward_velocity,low_swing_peak_lift,low_swing_rel_x_range,single_support_not_balanced,too_few_swing_segments,too_little_single_support` |
| `outputs/analysis/pitch_chain_student_trace_validation_fitted/seed_sweep` | 0 | 0 | `False` | NA | `NA` | NA | `NA` |
| `outputs/analysis/phase2_foot_placement_mpc_rough_preflight_traces/fpm_is1_period0p56_ls0p025_fx0p03_fg1p2_sk0p14_sr0p04_sp0p02_tc2p5_psg0p1_pysg0p1` | 0 | 0 | `False` | NA | `NA` | NA | `NA` |
| `outputs/analysis/phase2_foot_placement_mpc_rough_preflight_traces/fpm_ism1_period0p56_ls0p025_fx0p03_fg1p2_sk0p14_sr0p04_sp0p02_tc2p5_psg0p1_pysg0p1` | 0 | 0 | `False` | NA | `NA` | NA | `NA` |

## Best Global By Seed

| seed | root | trace | window | mean_vx | sent_vel_p95 | tracking_p95 | single_support | double_support | min_swing_segments | min_swing_rel_x_range | min_swing_peak_lift | failures |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 2 | `outputs/analysis/live_oracle_dagger_phase_student/iter_001/rollouts_x008/student` | `outputs/analysis/live_oracle_dagger_phase_student/iter_001/rollouts_x008/student/seed_002/trace.jsonl` | 100 | 0.0571 | 2.2257 | 0.1818 | 39.0 | 61.0 | 3 | 0.0091 | 0.0115 | `PASS` |
| 4 | `outputs/analysis/live_oracle_dagger_phase_student/iter_001/rollouts_x008/student` | `outputs/analysis/live_oracle_dagger_phase_student/iter_001/rollouts_x008/student/seed_004/trace.jsonl` | 100 | 0.0544 | 2.2291 | 0.1809 | 45.0 | 55.0 | 4 | 0.0100 | 0.0109 | `PASS` |

## Interpretation

- At least one existing trace source contains hard-step windows for both seed 2 and seed 4 under the corrected bridge criteria.
- Next action: promote that source into the pre-registered terrain-step branch and test whether it transfers to z=0.001/z=0.002 terrain gates before any new PPO run.
- No robot, SSH, deployment, grounded replay, or runtime behavior change was performed.
