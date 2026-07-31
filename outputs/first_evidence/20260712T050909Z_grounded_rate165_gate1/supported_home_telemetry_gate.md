# Supported Home Telemetry Gate

status: `PASS_TELEMETRY_COMPONENT_WITH_WARNINGS`
physical_pose_status: `REQUIRES_OPERATOR_VISUAL_CONFIRMATION`

Telemetry cannot approve physical geometry.

## Holds

- none

## Tracking

| joint | pitch | p95 abs rad | max consecutive over limit |
|---|---|---:|---:|
| `left_hip_yaw` | `False` | 0.0030 | 0 |
| `left_hip_roll` | `False` | 0.0040 | 0 |
| `left_hip_pitch` | `True` | 0.0010 | 0 |
| `left_knee` | `True` | 0.0000 | 0 |
| `left_ankle` | `True` | 0.0010 | 0 |
| `neck_pitch` | `False` | 0.0010 | 0 |
| `head_pitch` | `False` | 0.0020 | 0 |
| `head_yaw` | `False` | 0.0000 | 0 |
| `head_roll` | `False` | 0.0060 | 0 |
| `right_hip_yaw` | `False` | 0.0000 | 0 |
| `right_hip_roll` | `False` | 0.0060 | 0 |
| `right_hip_pitch` | `True` | 0.0030 | 0 |
| `right_knee` | `True` | 0.0030 | 0 |
| `right_ankle` | `True` | 0.0050 | 0 |

gyro_p95_abs_rad_s: `[0.004363323129985824, 0.00545415391248228, 0.002181661564992912]`
accel_mean_m_s2: `[1.6678333333333333, 0.35816666666666663, 9.682055555555555]`
