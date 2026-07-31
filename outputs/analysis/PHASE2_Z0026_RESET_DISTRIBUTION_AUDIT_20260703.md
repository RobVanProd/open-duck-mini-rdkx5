# Playground Reset Distribution Audit

status: `HOLD_RESET_DISTRIBUTION_CONTAINS_NO_CONTACT_STARTS`

This is an offline reset/support diagnostic. It does not SSH, deploy,
train, run robot tests, or change runtime behavior.

## Config

- playground_path: `/home/lsd/robots/Open_Duck_Playground`
- task: `rough_terrain_backlash`
- terrain_hfield_z_scale: `0.0026`
- command_x: `0.08`
- seeds: `[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]`
- jax_backend: `cpu`
- jax_devices: `['TFRT_CPU_0']`

## Reset Implementation

- base_xy_uniform_m: `[-0.05, 0.05]`
- yaw_uniform_rad: `[-3.14, 3.14]`
- actuator_qpos_multiplier: `[0.5, 1.5]`
- base_qvel_uniform: `[-0.05, 0.05]`
- ctrl_initialized_to_actuator_qpos: `True`
- source: `Open_Duck_Playground/playground/open_duck_mini_v2/joystick.py reset()`

## Support Counts

| support | count | percent |
|---|---:|---:|
| `none` | 2 | 6.2500 |
| `left` | 8 | 25.0000 |
| `right` | 6 | 18.7500 |
| `double` | 16 | 50.0000 |

## Distribution Stats

| metric | mean | min | p50 | p95 | max |
|---|---:|---:|---:|---:|---:|
| `base_height_m` | 0.1500 | 0.1500 | 0.1500 | 0.1500 | 0.1500 |
| `base_qvel_norm` | 0.0656 | 0.0434 | 0.0641 | 0.0877 | 0.1061 |
| `foot_z_min_m` | -0.0096 | -0.0348 | -0.0110 | 0.0168 | 0.0312 |
| `foot_z_max_m` | 0.0144 | -0.0239 | 0.0114 | 0.0450 | 0.0682 |
| `foot_z_delta_m` | 0.0240 | 0.0009 | 0.0181 | 0.0598 | 0.0690 |
| `actuator_delta_l2_rad` | 0.6462 | 0.2621 | 0.6163 | 1.0081 | 1.0301 |
| `actuator_delta_max_abs_rad` | 0.4442 | 0.1948 | 0.4295 | 0.6611 | 0.6692 |

## Per-Seed Reset State

| seed | support | contact | base_h | foot_z | foot_z_delta | qpos_l2 | qpos_max_abs |
|---:|---|---|---:|---|---:|---:|---:|
| 0 | `right` | `[False, True]` | 0.1500 | `[0.0319, -0.0053]` | 0.0372 | 0.8136 | 0.6392 |
| 1 | `double` | `[True, True]` | 0.1500 | `[-0.0111, -0.0073]` | 0.0038 | 0.4393 | 0.2894 |
| 2 | `right` | `[False, True]` | 0.1500 | `[0.0289, 0.0128]` | 0.0161 | 0.9070 | 0.6632 |
| 3 | `double` | `[True, True]` | 0.1500 | `[-0.01, -0.0108]` | 0.0009 | 0.4096 | 0.2110 |
| 4 | `left` | `[True, False]` | 0.1500 | `[0.0036, 0.0158]` | 0.0122 | 0.5305 | 0.4288 |
| 5 | `none` | `[False, False]` | 0.1500 | `[0.0312, 0.0682]` | 0.0370 | 1.0251 | 0.6692 |
| 6 | `left` | `[True, False]` | 0.1500 | `[-0.0249, 0.0342]` | 0.0591 | 0.7571 | 0.4628 |
| 7 | `double` | `[True, True]` | 0.1500 | `[-0.0307, -0.0024]` | 0.0283 | 0.6277 | 0.4827 |
| 8 | `none` | `[False, False]` | 0.1500 | `[0.0113, 0.0401]` | 0.0288 | 0.8541 | 0.6594 |
| 9 | `right` | `[False, True]` | 0.1500 | `[0.0338, 0.0203]` | 0.0135 | 0.7234 | 0.3787 |
| 10 | `left` | `[True, False]` | 0.1500 | `[0.0029, 0.0322]` | 0.0293 | 0.5564 | 0.4303 |
| 11 | `left` | `[True, False]` | 0.1500 | `[-0.0002, 0.0088]` | 0.0090 | 0.6060 | 0.3434 |
| 12 | `right` | `[False, True]` | 0.1500 | `[0.0315, 0.014]` | 0.0175 | 0.7062 | 0.4575 |
| 13 | `double` | `[True, True]` | 0.1500 | `[0.0082, -0.0105]` | 0.0187 | 0.6017 | 0.3517 |
| 14 | `right` | `[False, True]` | 0.1500 | `[0.0253, -0.0238]` | 0.0491 | 0.8330 | 0.5785 |
| 15 | `double` | `[True, True]` | 0.1500 | `[-0.0201, -0.0155]` | 0.0046 | 0.4685 | 0.3540 |
| 16 | `double` | `[True, True]` | 0.1500 | `[-0.0152, -0.0075]` | 0.0077 | 0.4408 | 0.3150 |
| 17 | `double` | `[True, True]` | 0.1500 | `[-0.0018, 0.004]` | 0.0057 | 0.4436 | 0.2733 |
| 18 | `left` | `[True, False]` | 0.1500 | `[-0.0121, 0.0391]` | 0.0512 | 0.6828 | 0.5077 |
| 19 | `double` | `[True, True]` | 0.1500 | `[-0.0239, -0.0348]` | 0.0109 | 1.0301 | 0.6557 |
| 20 | `left` | `[True, False]` | 0.1500 | `[-0.0043, 0.0268]` | 0.0311 | 0.8491 | 0.5708 |
| 21 | `double` | `[True, True]` | 0.1500 | `[-0.0089, 0.0019]` | 0.0109 | 0.4763 | 0.2831 |
| 22 | `double` | `[True, True]` | 0.1500 | `[-0.0062, 0.0024]` | 0.0086 | 0.4510 | 0.3445 |
| 23 | `double` | `[True, True]` | 0.1500 | `[-0.0161, -0.0127]` | 0.0034 | 0.3921 | 0.2668 |
| 24 | `double` | `[True, True]` | 0.1500 | `[-0.0049, -0.0037]` | 0.0013 | 0.2621 | 0.1948 |
| 25 | `double` | `[True, True]` | 0.1500 | `[-0.0258, 0.0005]` | 0.0264 | 0.5620 | 0.4106 |
| 26 | `double` | `[True, True]` | 0.1500 | `[-0.0285, -0.0202]` | 0.0084 | 0.5864 | 0.4929 |
| 27 | `left` | `[True, False]` | 0.1500 | `[-0.0333, 0.0274]` | 0.0607 | 0.9942 | 0.6474 |
| 28 | `left` | `[True, False]` | 0.1500 | `[-0.0211, 0.0286]` | 0.0497 | 0.8727 | 0.5978 |
| 29 | `double` | `[True, True]` | 0.1500 | `[-0.0198, 0.014]` | 0.0338 | 0.6266 | 0.3918 |
| 30 | `right` | `[False, True]` | 0.1500 | `[0.051, -0.018]` | 0.0690 | 0.7790 | 0.5736 |
| 31 | `double` | `[True, True]` | 0.1500 | `[-0.0158, 0.0088]` | 0.0246 | 0.3692 | 0.2877 |

## Seed 5 Detail

- support: `none`
- contact: `[False, False]`
- base_height_m: `0.1500`
- foot_z_m: `[0.0312, 0.0682]`
- actuator_delta_l2_rad: `1.0251`
- actuator_delta_max_abs_rad: `0.6692`

Largest actuator deltas from home:

| joint | delta_rad |
|---|---:|
| `right_knee` | 0.6692 |
| `left_knee` | 0.6258 |
| `right_hip_pitch` | -0.2838 |
| `right_ankle` | 0.2553 |
| `left_ankle` | -0.2382 |
| `left_hip_pitch` | -0.0910 |
| `left_hip_roll` | -0.0226 |
| `right_hip_roll` | -0.0023 |

## Interpretation

No-contact reset starts are outside the standing support manifold and should be treated as a reset-distribution issue unless the real robot start protocol can produce the same unsupported state.
