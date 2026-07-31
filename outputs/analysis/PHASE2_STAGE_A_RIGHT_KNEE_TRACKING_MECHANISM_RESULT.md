# Right-Knee Tracking Mechanism Result

Status: **RIGHT_KNEE_TARGET_DEMAND_MECHANISM_NOT_SUPPORTED**

| feature | A AUC/corr | B AUC/corr | C AUC/corr | passes |
|---|---:|---:|---:|---:|
| `applied_target_rate_p95_rad_s` | 0.309/-0.167 | 0.857/-0.143 | 0.623/0.061 | `False` |
| `rate_saturation_fraction` | 0.500/NA | 0.500/NA | 0.500/NA | `False` |
| `limiter_clip_gap_p95_rad` | 0.200/-0.098 | 0.893/0.067 | 0.645/-0.004 | `False` |
| `prelimit_target_rate_p95_rad_s` | 0.036/-0.237 | 0.857/0.139 | 0.628/-0.051 | `False` |

## Decision

Do not alter the right-knee rate limiter from this evidence.

No limiter or policy change is authorized.
