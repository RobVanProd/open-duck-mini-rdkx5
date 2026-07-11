# Pre-Fall Trajectory Signature Result

Status: **CANDIDATE_RECOVERY_VARIABLES_IDENTIFIED**

Offline analysis of existing traces only. No intervention, training, robot, GPU, or Colab use.

Window: first `10` ticks (`0.20` seconds)

| feature | A AUC | B AUC | C AUC | minimum | passes |
|---|---:|---:|---:|---:|---:|
| `base_height_drop_m` | 0.409 | 0.500 | 0.519 | 0.409 | `False` |
| `abs_pitch_growth_rad` | 0.855 | 0.750 | 0.753 | 0.750 | `True` |
| `adverse_forward_velocity_m_s` | 0.436 | 0.536 | 0.537 | 0.436 | `False` |
| `actuator_tracking_error_p95_rad` | 0.945 | 0.821 | 0.827 | 0.821 | `True` |
| `joint_speed_p95_rad_s` | 0.636 | 0.821 | 0.714 | 0.636 | `False` |
| `contact_transition_count` | 0.627 | 0.482 | 0.515 | 0.482 | `False` |

## Decision

Treat passing features only as candidate recovery variables requiring causal intervention tests.

Passing is association evidence only; no intervention is authorized.
