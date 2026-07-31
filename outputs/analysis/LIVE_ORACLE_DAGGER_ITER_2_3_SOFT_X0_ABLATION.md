# Live-Oracle DAgger Soft x0 Label Ablation

status: `HOLD_SOFT_X0_LABELS_STILL_COLLAPSE_SEED5`

Offline ablation only. No robot, SSH, deployment, or runtime changes were performed.

## Tested Variants

| iteration | x0_zero_action_alpha | seed5_x0_status | samples | termination | mean_local_vx | base_height_min | body_pitch_p95 | max_pitch_vel_p95 | max_tracking_p95 |
|---:|---:|---|---:|---|---:|---:|---:|---:|---:|
| 2 | 0.50 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 49 | `fall_or_nan` | -0.3044 | 0.0598 | 0.0514 | 1.3322 | 0.2389 |
| 3 | 0.20 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 72 | `fall_or_nan` | -0.2078 | 0.0621 | 0.0973 | 1.4477 | 0.1592 |

## Interpretation

- Full zero-action x=0.0 relabeling fixed most zero-command seeds but created seed-5 reverse/fall.
- Softening the x=0.0 label to alpha 0.5 still falls at seed 5.
- Softening further to alpha 0.2 still falls at seed 5.
- The failure persists at low target rates, so it is not an actuator overdrive problem.
- The simple zero-action x=0.0 label stream conflicts with the movement manifold for this seed.

## Decision

Do not spend more branch budget on scalar zero-action alpha sweeps. The next branch step should change structure: separate command-conditioned heads, add a command-aware gate in the student, or move to the next representation rung instead of globally blending zero labels into the same feed-forward map.
