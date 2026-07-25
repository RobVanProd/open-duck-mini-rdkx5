# T3 observation z-score v2 result

- Status: `HOLD_T3_V2_VIOLATIONS_AND_INCOMPLETE_REAL_OBS_COVERAGE`
- Policy SHA-256: `3c606f9381a1710cc8fecdb7442787dcbfce3ee9bc02a6f1224774ab2b3a1067`
- Sustained threshold: `|z| > 0.5` for `50` consecutive samples.
- Complete-observation coverage: `False`.
- Sustained source-level flags: `21`.
- Calibrated Gate 3 upright `obs[3]`: median `0.3900 m/s^2`, median `z=0.2128`, longest violation run `3` ticks—there is no sustained upright `obs[3]` violation in this capture.
- Sparse suspended snapshots: legacy current `obs[3]=1.97` (`z=0.999`), corrected `obs[3]=1.35` (`z=0.690`); one sample each cannot establish persistence.
- The historical telemetry's swallowed ONNX import error is confirmed; the runtime/diagnostic path now fails before capture.

## Sustained flags

- `obs[3] accel_x_m_s2` in `gate3_nose_back`: longest run 248 samples, median `|z|=3.4508`.
- `obs[4] accel_y_m_s2` in `gate3_left_tilt`: longest run 249 samples, median `|z|=2.7283`.
- `obs[4] accel_y_m_s2` in `gate3_right_tilt`: longest run 249 samples, median `|z|=2.5471`.
- `obs[3] accel_x_m_s2` in `gate3_nose_forward`: longest run 249 samples, median `|z|=2.4780`.
- `obs[98] contact_right` in `gate3_left_contact`: longest run 250 samples, median `|z|=2.0714`.
- `obs[98] contact_right` in `gate3_left_tilt`: longest run 250 samples, median `|z|=2.0714`.
- `obs[98] contact_right` in `gate3_no_contacts`: longest run 250 samples, median `|z|=2.0714`.
- `obs[98] contact_right` in `gate3_nose_back`: longest run 250 samples, median `|z|=2.0714`.
- `obs[98] contact_right` in `gate3_nose_forward`: longest run 250 samples, median `|z|=2.0714`.
- `obs[98] contact_right` in `gate3_right_tilt`: longest run 250 samples, median `|z|=2.0714`.
- `obs[98] contact_right` in `gate3_upright`: longest run 233 samples, median `|z|=2.0714`.
- `obs[97] contact_left` in `gate3_left_tilt`: longest run 250 samples, median `|z|=2.0621`.
- `obs[97] contact_left` in `gate3_no_contacts`: longest run 250 samples, median `|z|=2.0621`.
- `obs[97] contact_left` in `gate3_nose_back`: longest run 250 samples, median `|z|=2.0621`.
- `obs[97] contact_left` in `gate3_nose_forward`: longest run 250 samples, median `|z|=2.0621`.
- `obs[97] contact_left` in `gate3_right_contact`: longest run 250 samples, median `|z|=2.0621`.
- `obs[97] contact_left` in `gate3_right_tilt`: longest run 250 samples, median `|z|=2.0621`.
- `obs[97] contact_left` in `gate3_upright`: longest run 183 samples, median `|z|=2.0621`.
- `obs[5] accel_z_m_s2` in `gate3_left_tilt`: longest run 250 samples, median `|z|=1.0940`.
- `obs[5] accel_z_m_s2` in `gate3_right_tilt`: longest run 250 samples, median `|z|=0.9309`.
- `obs[5] accel_z_m_s2` in `gate3_nose_back`: longest run 250 samples, median `|z|=0.8251`.

## 101-channel table

| rank | obs | channel | samples | complete | |z| p50 | |z| p95 | |z| max | sustained sources |
|---:|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | 3 | `accel_x_m_s2` | 2253 | 3 | 0.207856 | 3.455814 | 3.729378 | 2 |
| 2 | 4 | `accel_y_m_s2` | 2253 | 3 | 0.333964 | 2.729669 | 2.891828 | 2 |
| 3 | 5 | `accel_z_m_s2` | 2253 | 3 | 0.111775 | 1.098280 | 2.868032 | 3 |
| 4 | 98 | `contact_right` | 2253 | 3 | 2.071358 | 2.071358 | 2.071358 | 7 |
| 5 | 97 | `contact_left` | 2253 | 3 | 2.062110 | 2.062110 | 2.062110 | 7 |
| 6 | 96 | `previous_target_right_ankle_rad` | 3 | 3 | 1.737069 | 1.844365 | 1.856287 | 0 |
| 7 | 26 | `position_error_right_ankle_rad` | 3 | 3 | 1.797223 | 1.797223 | 1.797223 | 0 |
| 8 | 54 | `action_t_minus_1_right_ankle` | 3 | 3 | 1.606190 | 1.705944 | 1.717027 | 0 |
| 9 | 18 | `position_error_neck_pitch_rad` | 3 | 3 | 1.614320 | 1.672317 | 1.678761 | 0 |
| 10 | 87 | `previous_target_left_ankle_rad` | 3 | 3 | 0.147704 | 1.504323 | 1.655059 | 0 |
| 11 | 88 | `previous_target_neck_pitch_rad` | 3 | 3 | 0.299204 | 1.493553 | 1.626258 | 0 |
| 12 | 68 | `action_t_minus_2_right_ankle` | 3 | 3 | 1.605170 | 1.605170 | 1.605170 | 0 |
| 13 | 82 | `action_t_minus_3_right_ankle` | 3 | 3 | 1.604360 | 1.604360 | 1.604360 | 0 |
| 14 | 94 | `previous_target_right_hip_pitch_rad` | 3 | 3 | 0.199765 | 1.443327 | 1.581501 | 0 |
| 15 | 46 | `action_t_minus_1_neck_pitch` | 3 | 3 | 0.748241 | 1.453192 | 1.531520 | 0 |
| 16 | 60 | `action_t_minus_2_neck_pitch` | 3 | 3 | 1.529939 | 1.529939 | 1.529939 | 0 |
| 17 | 74 | `action_t_minus_3_neck_pitch` | 3 | 3 | 1.528429 | 1.528429 | 1.528429 | 0 |
| 18 | 45 | `action_t_minus_1_left_ankle` | 3 | 3 | 0.412743 | 1.411617 | 1.522603 | 0 |
| 19 | 59 | `action_t_minus_2_left_ankle` | 3 | 3 | 1.521250 | 1.521250 | 1.521250 | 0 |
| 20 | 73 | `action_t_minus_3_left_ankle` | 3 | 3 | 1.519948 | 1.519948 | 1.519948 | 0 |
| 21 | 17 | `position_error_left_ankle_rad` | 3 | 3 | 1.500546 | 1.500546 | 1.500546 | 0 |
| 22 | 52 | `action_t_minus_1_right_hip_pitch` | 3 | 3 | 0.561195 | 1.396074 | 1.488838 | 0 |
| 23 | 66 | `action_t_minus_2_right_hip_pitch` | 3 | 3 | 1.486676 | 1.486676 | 1.486676 | 0 |
| 24 | 80 | `action_t_minus_3_right_hip_pitch` | 3 | 3 | 1.484592 | 1.484592 | 1.484592 | 0 |
| 25 | 85 | `previous_target_left_hip_pitch_rad` | 3 | 3 | 0.427502 | 1.375091 | 1.480378 | 0 |
| 26 | 24 | `position_error_right_hip_pitch_rad` | 3 | 3 | 1.474660 | 1.474660 | 1.474660 | 0 |
| 27 | 43 | `action_t_minus_1_left_hip_pitch` | 3 | 3 | 0.399508 | 1.293466 | 1.392795 | 0 |
| 28 | 57 | `action_t_minus_2_left_hip_pitch` | 3 | 3 | 1.390900 | 1.390900 | 1.390900 | 0 |
| 29 | 71 | `action_t_minus_3_left_hip_pitch` | 3 | 3 | 1.389088 | 1.389088 | 1.389088 | 0 |
| 30 | 99 | `phase_cos` | 3 | 3 | 1.378432 | 1.378432 | 1.378432 | 0 |
| 31 | 15 | `position_error_left_hip_pitch_rad` | 3 | 3 | 1.293262 | 1.325398 | 1.328968 | 0 |
| 32 | 84 | `previous_target_left_hip_roll_rad` | 3 | 3 | 0.779994 | 0.981141 | 1.003491 | 0 |
| 33 | 95 | `previous_target_right_knee_rad` | 3 | 3 | 0.742196 | 0.976195 | 1.002195 | 0 |
| 34 | 6 | `command_x_m_s` | 3 | 3 | 0.969951 | 0.969951 | 0.969951 | 0 |
| 35 | 42 | `action_t_minus_1_left_hip_roll` | 3 | 3 | 0.720676 | 0.906502 | 0.927149 | 0 |
| 36 | 53 | `action_t_minus_1_right_knee` | 3 | 3 | 0.677322 | 0.893452 | 0.917467 | 0 |
| 37 | 9 | `command_neck_pitch` | 3 | 3 | 0.834958 | 0.834958 | 0.834958 | 0 |
| 38 | 21 | `position_error_head_roll_rad` | 3 | 3 | 0.756146 | 0.794925 | 0.799234 | 0 |
| 39 | 91 | `previous_target_head_roll_rad` | 3 | 3 | 0.454919 | 0.752287 | 0.785328 | 0 |
| 40 | 49 | `action_t_minus_1_head_roll` | 3 | 3 | 0.398901 | 0.664825 | 0.694373 | 0 |
| 41 | 63 | `action_t_minus_2_head_roll` | 3 | 3 | 0.694032 | 0.694032 | 0.694032 | 0 |
| 42 | 77 | `action_t_minus_3_head_roll` | 3 | 3 | 0.693763 | 0.693763 | 0.693763 | 0 |
| 43 | 93 | `previous_target_right_hip_roll_rad` | 3 | 3 | 0.386343 | 0.634708 | 0.662304 | 0 |
| 44 | 51 | `action_t_minus_1_right_hip_roll` | 3 | 3 | 0.354815 | 0.591943 | 0.618290 | 0 |
| 45 | 19 | `position_error_head_pitch_rad` | 3 | 3 | 0.517971 | 0.552256 | 0.556065 | 0 |
| 46 | 20 | `position_error_head_yaw_rad` | 3 | 3 | 0.266549 | 0.499308 | 0.525170 | 0 |
| 47 | 89 | `previous_target_head_pitch_rad` | 3 | 3 | 0.296055 | 0.493655 | 0.515611 | 0 |
| 48 | 90 | `previous_target_head_yaw_rad` | 3 | 3 | 0.175118 | 0.452896 | 0.483760 | 0 |
| 49 | 47 | `action_t_minus_1_head_pitch` | 3 | 3 | 0.267842 | 0.449749 | 0.469961 | 0 |
| 50 | 61 | `action_t_minus_2_head_pitch` | 3 | 3 | 0.469635 | 0.469635 | 0.469635 | 0 |
| 51 | 75 | `action_t_minus_3_head_pitch` | 3 | 3 | 0.469321 | 0.469321 | 0.469321 | 0 |
| 52 | 48 | `action_t_minus_1_head_yaw` | 3 | 3 | 0.165532 | 0.422870 | 0.451464 | 0 |
| 53 | 62 | `action_t_minus_2_head_yaw` | 3 | 3 | 0.451407 | 0.451407 | 0.451407 | 0 |
| 54 | 76 | `action_t_minus_3_head_yaw` | 3 | 3 | 0.451366 | 0.451366 | 0.451366 | 0 |
| 55 | 86 | `previous_target_left_knee_rad` | 3 | 3 | 0.220596 | 0.350248 | 0.364654 | 0 |
| 56 | 79 | `action_t_minus_3_right_hip_roll` | 3 | 3 | 0.355090 | 0.355090 | 0.355090 | 0 |
| 57 | 65 | `action_t_minus_2_right_hip_roll` | 3 | 3 | 0.354944 | 0.354944 | 0.354944 | 0 |
| 58 | 44 | `action_t_minus_1_left_knee` | 3 | 3 | 0.194688 | 0.315049 | 0.328422 | 0 |
| 59 | 100 | `phase_sin` | 3 | 3 | 0.326676 | 0.326676 | 0.326676 | 0 |
| 60 | 25 | `position_error_right_knee_rad` | 3 | 3 | 0.304155 | 0.304155 | 0.304155 | 0 |
| 61 | 2 | `gyro_z_rad_s` | 2253 | 3 | 0.004377 | 0.060029 | 0.272904 | 0 |
| 62 | 0 | `gyro_x_rad_s` | 2253 | 3 | 0.006151 | 0.057224 | 0.252281 | 0 |
| 63 | 16 | `position_error_left_knee_rad` | 3 | 3 | 0.241134 | 0.250034 | 0.251023 | 0 |
| 64 | 23 | `position_error_right_hip_roll_rad` | 3 | 3 | 0.226594 | 0.226594 | 0.226594 | 0 |
| 65 | 14 | `position_error_left_hip_roll_rad` | 3 | 3 | 0.194170 | 0.194170 | 0.194170 | 0 |
| 66 | 72 | `action_t_minus_3_left_knee` | 3 | 3 | 0.180307 | 0.180307 | 0.180307 | 0 |
| 67 | 58 | `action_t_minus_2_left_knee` | 3 | 3 | 0.180288 | 0.180288 | 0.180288 | 0 |
| 68 | 1 | `gyro_y_rad_s` | 2253 | 3 | 0.010778 | 0.052116 | 0.169868 | 0 |
| 69 | 83 | `previous_target_left_hip_yaw_rad` | 3 | 3 | 0.118563 | 0.137645 | 0.139766 | 0 |
| 70 | 41 | `action_t_minus_1_left_hip_yaw` | 3 | 3 | 0.107389 | 0.127969 | 0.130256 | 0 |
| 71 | 81 | `action_t_minus_3_right_knee` | 3 | 3 | 0.127081 | 0.127081 | 0.127081 | 0 |
| 72 | 67 | `action_t_minus_2_right_knee` | 3 | 3 | 0.126631 | 0.126631 | 0.126631 | 0 |
| 73 | 92 | `previous_target_right_hip_yaw_rad` | 3 | 3 | 0.053557 | 0.111242 | 0.117651 | 0 |
| 74 | 78 | `action_t_minus_3_right_hip_yaw` | 3 | 3 | 0.108763 | 0.108763 | 0.108763 | 0 |
| 75 | 64 | `action_t_minus_2_right_hip_yaw` | 3 | 3 | 0.108754 | 0.108754 | 0.108754 | 0 |
| 76 | 50 | `action_t_minus_1_right_hip_yaw` | 3 | 3 | 0.049681 | 0.102840 | 0.108746 | 0 |
| 77 | 22 | `position_error_right_hip_yaw_rad` | 3 | 3 | 0.093381 | 0.093381 | 0.093381 | 0 |
| 78 | 69 | `action_t_minus_3_left_hip_yaw` | 3 | 3 | 0.056467 | 0.056467 | 0.056467 | 0 |
| 79 | 55 | `action_t_minus_2_left_hip_yaw` | 3 | 3 | 0.056374 | 0.056374 | 0.056374 | 0 |
| 80 | 32 | `velocity_scaled_neck_pitch` | 3 | 3 | 0.004435 | 0.037208 | 0.040850 | 0 |
| 81 | 13 | `position_error_left_hip_yaw_rad` | 3 | 3 | 0.035969 | 0.035969 | 0.035969 | 0 |
| 82 | 70 | `action_t_minus_3_left_hip_roll` | 3 | 3 | 0.035636 | 0.035636 | 0.035636 | 0 |
| 83 | 56 | `action_t_minus_2_left_hip_roll` | 3 | 3 | 0.035476 | 0.035476 | 0.035476 | 0 |
| 84 | 40 | `velocity_scaled_right_ankle` | 3 | 3 | 0.010050 | 0.010050 | 0.010050 | 0 |
| 85 | 31 | `velocity_scaled_left_ankle` | 3 | 3 | 0.009991 | 0.009991 | 0.009991 | 0 |
| 86 | 38 | `velocity_scaled_right_hip_pitch` | 3 | 3 | 0.007464 | 0.007464 | 0.007464 | 0 |
| 87 | 29 | `velocity_scaled_left_hip_pitch` | 3 | 3 | 0.006903 | 0.006903 | 0.006903 | 0 |
| 88 | 12 | `command_head_roll` | 3 | 3 | 0.004681 | 0.004681 | 0.004681 | 0 |
| 89 | 39 | `velocity_scaled_right_knee` | 3 | 3 | 0.003871 | 0.003871 | 0.003871 | 0 |
| 90 | 7 | `command_y_m_s` | 3 | 3 | 0.003060 | 0.003060 | 0.003060 | 0 |
| 91 | 30 | `velocity_scaled_left_knee` | 3 | 3 | 0.002756 | 0.002756 | 0.002756 | 0 |
| 92 | 34 | `velocity_scaled_head_yaw` | 3 | 3 | 0.002171 | 0.002171 | 0.002171 | 0 |
| 93 | 35 | `velocity_scaled_head_roll` | 3 | 3 | 0.002079 | 0.002079 | 0.002079 | 0 |
| 94 | 8 | `command_yaw_rad_s` | 3 | 3 | 0.001876 | 0.001876 | 0.001876 | 0 |
| 95 | 36 | `velocity_scaled_right_hip_yaw` | 3 | 3 | 0.001107 | 0.001107 | 0.001107 | 0 |
| 96 | 37 | `velocity_scaled_right_hip_roll` | 3 | 3 | 0.001017 | 0.001017 | 0.001017 | 0 |
| 97 | 10 | `command_head_pitch` | 3 | 3 | 0.000846 | 0.000846 | 0.000846 | 0 |
| 98 | 11 | `command_head_yaw` | 3 | 3 | 0.000718 | 0.000718 | 0.000718 | 0 |
| 99 | 28 | `velocity_scaled_left_hip_roll` | 3 | 3 | 0.000240 | 0.000240 | 0.000240 | 0 |
| 100 | 27 | `velocity_scaled_left_hip_yaw` | 3 | 3 | 0.000206 | 0.000206 | 0.000206 | 0 |
| 101 | 33 | `velocity_scaled_head_pitch` | 3 | 3 | 0.000111 | 0.000111 | 0.000111 | 0 |

## Interpretation

The available archive does not contain the full 747-tick corrected policy replay. Component captures are reported without filling unrecorded fields. Therefore this result cannot authorize the claim that `obs[3]` is the only real-observation violation; it identifies measured candidates and preserves the missing-data hold.
