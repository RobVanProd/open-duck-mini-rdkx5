# Early Tracking-Error Joint Localization

Status: **LOCALIZED_TRACKING_ERROR_CANDIDATES_IDENTIFIED**

| joint | A AUC | B AUC | C AUC | minimum | passes |
|---|---:|---:|---:|---:|---:|
| `left_hip_yaw` | 0.145 | 0.500 | 0.567 | 0.145 | `False` |
| `left_hip_roll` | 0.291 | 0.857 | 0.437 | 0.291 | `False` |
| `left_hip_pitch` | 0.709 | 0.500 | 0.645 | 0.500 | `False` |
| `left_knee` | 0.982 | 0.464 | 0.745 | 0.464 | `False` |
| `left_ankle` | 0.691 | 0.607 | 0.524 | 0.524 | `False` |
| `neck_pitch` | 0.655 | 0.250 | 0.381 | 0.250 | `False` |
| `head_pitch` | 0.236 | 0.321 | 0.411 | 0.236 | `False` |
| `head_yaw` | 0.545 | 0.500 | 0.433 | 0.433 | `False` |
| `head_roll` | 0.636 | 0.643 | 0.433 | 0.433 | `False` |
| `right_hip_yaw` | 0.182 | 0.321 | 0.476 | 0.182 | `False` |
| `right_hip_roll` | 0.582 | 0.607 | 0.424 | 0.424 | `False` |
| `right_hip_pitch` | 0.309 | 0.857 | 0.593 | 0.309 | `False` |
| `right_knee` | 0.727 | 0.929 | 0.753 | 0.727 | `True` |
| `right_ankle` | 0.764 | 0.393 | 0.472 | 0.393 | `False` |

## Decision

Causal screen required before any joint change.

Association only; no intervention is authorized.
