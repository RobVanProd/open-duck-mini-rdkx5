# Soft-Prior Fragment Config

status: `PASS_SOFT_PRIOR_CONFIG_READY`

This is a compact pitch-chain/contact prior distilled from curated
low-command target fragments. It is not a policy, not a target-label
dataset, and not training permission.

## Inputs

- manifest: `outputs/analysis/target_dataset_manifest_dynamic_roll_lateral_fix_robust_modes.json`
- dataset_id: `c4833a96744101d9`
- entries: `9`
- source_files: `2`
- source_mode_pairs: `6`
- window_len: `50`
- joints: `left_hip_pitch, left_knee, left_ankle, right_hip_pitch, right_knee, right_ankle`

## Source Metrics

| metric | min | mean | p50 | p95 | max |
|---|---:|---:|---:|---:|---:|
| mean_vx_m_s | 0.0401 | 0.0417 | 0.0416 | 0.0436 | 0.0437 |
| vy_abs_p95_m_s | 0.0431 | 0.0702 | 0.0716 | 0.0902 | 0.0910 |
| body_pitch_abs_p95_rad | 0.2417 | 0.2785 | 0.2782 | 0.3243 | 0.3294 |
| base_height_min_m | 0.1455 | 0.1468 | 0.1467 | 0.1484 | 0.1488 |
| contact_dominance_pct | 88.0000 | 92.6667 | 94.0000 | 94.0000 | 94.0000 |

## Prior Metrics

- max target velocity p95: `2.4428` rad/s

| joint | action std p95 | target velocity p95 |
|---|---:|---:|
| left_hip_pitch | 0.0961 | 1.4698 |
| left_knee | 0.1513 | 2.4428 |
| left_ankle | 0.0080 | 0.0884 |
| right_hip_pitch | 0.0961 | 1.4698 |
| right_knee | 0.1476 | 1.9263 |
| right_ankle | 0.0069 | 0.0619 |

## Gate

- `PASS_SOFT_PRIOR_CONFIG_READY` means the compact prior is usable for a default-off smoke evaluator.
- It does not permit PPO, robot validation, or deployment.
- Next required gate: `PASS_SOFT_PRIOR_SMOKE` from `docs/SOFT_PRIOR_CLOSED_LOOP_LEARNER_PLAN.md`.
