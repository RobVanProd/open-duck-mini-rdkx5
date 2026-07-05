# Seed-5 Rate160 Anti-Lunge Student Decision

status: `HOLD_SEED5_ANTILUNGE_TRANSFER_REGRESSED`

This is an offline trainable-compression branch decision. It did not train PPO, deploy, SSH, run robot tests, grounded replay, or change runtime behavior.

## Inputs

- merged_manifest: `outputs/analysis/phase2_command_gated_zero0020_with_seed5_rate160_antilunge_manifest.json`
- dataset_id: `b9d5821e5727ac77`
- student_report: `outputs/analysis/phase2_command_gated_zero0020_seed5_rate160_antilunge_ppo_loc_bc_student.json`
- candidate_onnx: `outputs/analysis/phase2_command_gated_zero0020_seed5_rate160_antilunge_ppo_loc_bc_student/candidate.onnx`
- candidate_onnx_sha256: `02ae0552547786aa975abaaed6a32e089751d72a958580eb26d031f107e65746`
- gate: `outputs/analysis/PHASE2_COMMAND_GATED_ZERO0020_SEED5_RATE160_ANTILUNGE_STUDENT_X008_SEED0_5_7_GATE.md`

## Fit

- fit_status: `PASS_PPO_LOC_BC_FIT_SMOKE`
- samples: `7524`
- weighted_samples: `7644.0`
- MAE: `0.002257`
- p95_abs_error: `0.007259`
- target_rate_p95_rad_s: `1.2638`
- target_rate_max_rad_s: `2.8610`

## Gate Result

- seeds: `[0, 5, 7]`
- pass_count: `0/3`
- falls: `3`
- samples_mean/min: `442.3` / `153`
- mean_track_ratio: `0.8066`
- mean_vx_m_s: `0.0645`
- max_p95_velocity_excess_rad_s: `0.0000`
- max_instant_velocity_excess_rad_s: `1.4007`

| seed | status | samples | termination | vx | track_ratio | pitch_p95 | height_min | p95_excess | max_excess |
|---:|---|---:|---|---:|---:|---:|---:|---:|---:|
| 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 686 | `fall_or_nan` | -0.0008 | -0.0097 | 0.1809 | 0.0814 | 0.0000 | 0.0000 |
| 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 153 | `fall_or_nan` | 0.1327 | 1.6588 | 0.8227 | 0.0091 | 0.0000 | 0.5781 |
| 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 488 | `fall_or_nan` | 0.0617 | 0.7707 | 0.3638 | -0.0014 | 0.0000 | 1.4007 |

## Decision

Do not promote the low-weight seed-5 rate160 anti-lunge PPO-loc student. It failed the target seed and regression-control seeds under the hard z=0.0075 rough+push x=0.08 screen.

Seed 5 still failed by lunge/fall, and regression-control seeds 0 and 7 also failed. This closes the low-weight seed-5 anti-lunge PPO-loc compression attempt.

## Next Recommendation

Close this low-weight transfer path. The rate160 seed-5 stabilizing behavior did not survive compression into the faster command-gated PPO-loc student. Next work should change the preservation structure rather than add another tiny seed-specific relabel: either a branch/router wrapper objective that keeps the passing behaviors separate, or a stronger online behavior-preservation method before Phase 2 DR.
