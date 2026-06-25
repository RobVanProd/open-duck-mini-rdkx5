# Reference Motion Seed Audit

status: `PASS_REFERENCE_MOTION_AVAILABLE`
reference_path: `/home/lsd/robots/Open_Duck_Playground/playground/open_duck_mini_v2/data/polynomial_coefficients.pkl`
command: `{'x': 0.04, 'y': 0.0, 'yaw': 0.0}`
nearest_reference_key: `0.074_-0.037_-0.074`

## Command Grid

- dx_values: `[-0.148, -0.074, 0.0, 0.074, 0.148, 0.222]`
- dy_values: `[-0.111, -0.037, 0.037, 0.111]`
- dtheta_values: `[-1.111, -0.852, -0.593, -0.333, -0.074, 0.185, 0.444, 0.704, 0.963, 1.222]`
- dx_range: `[-0.148, 0.222]`
- dy_range: `[-0.111, 0.111]`
- dtheta_range: `[-1.111, 1.222]`

## Reference Timing

- period_s: `0.54`
- fps: `50.0`
- steps_per_period: `27`

## 14-Action Joint Reference Ranges

| joint | ref_dim | min | max | mean | p95_abs |
|---|---:|---:|---:|---:|---:|
| `left_hip_yaw` | 0 | -0.0091 | 0.0090 | 0.0011 | 0.0090 |
| `left_hip_roll` | 1 | -0.1027 | 0.1604 | 0.0405 | 0.1557 |
| `left_hip_pitch` | 2 | -1.0294 | -0.5931 | -0.7951 | 1.0150 |
| `left_knee` | 3 | 1.0789 | 1.7838 | 1.3747 | 1.7576 |
| `left_ankle` | 4 | -0.8814 | -0.4227 | -0.6498 | 0.8664 |
| `neck_pitch` | 5 | 0.3491 | 0.3491 | 0.3491 | 0.3491 |
| `head_pitch` | 6 | -0.4538 | -0.4538 | -0.4538 | 0.4538 |
| `head_yaw` | 7 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| `head_roll` | 8 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| `right_hip_yaw` | 11 | -0.0173 | 0.0015 | -0.0076 | 0.0169 |
| `right_hip_roll` | 12 | -0.1974 | 0.0520 | -0.0831 | 0.1956 |
| `right_hip_pitch` | 13 | 0.5882 | 1.1479 | 0.8168 | 1.0724 |
| `right_knee` | 14 | 1.1990 | 1.9659 | 1.4230 | 1.8874 |
| `right_ankle` | 15 | -0.9327 | -0.4862 | -0.6765 | 0.8988 |

## Interpretation

- The reference-motion data is present and contains the 14 runtime action joints plus two antenna dimensions.
- The active Playground imitation reward compares leg joint pose/velocity, base velocity, base angular velocity, and foot contacts; head/neck and antenna dimensions are present in the reference but are not the leg-imitation error term.
- The lowest positive reference `dx` is above the `x=0.04` low-command gate, so V19 uses a slightly faster gait shape as a reference-motion reward while grading command tracking at `x=0.04`.
- If the reference-imitation policy still degrades into standstill/reverse, the reward/task landscape should be debugged against this reference path rather than continuing cold-start reward tuning.
