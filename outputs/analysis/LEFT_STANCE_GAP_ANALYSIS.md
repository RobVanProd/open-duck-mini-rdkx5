# Left-Stance Gap Analysis

status: `WARN_LEFT_STANCE_EXISTS_BUT_NOT_IN_SELECTOR`

This is an offline analysis of existing BEST_WALK full-observation traces. It does not train, deploy, SSH, run robot tests, or change runtime behavior.

## Summary

- windows: `2904`
- left_related_windows: `553`

## Contact-Side Groups

| group | windows | pass | pass_% | vx | pitch_p95 | right_knee_p95 | left_knee_p95 | top reasons |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| center_double__majority_double | 1809 | 167 | 9.2316 | 0.0264 | 1.9250 | 1.5804 | 1.3039 | low_moving_single_in_envelope:1170, low_mean_vx:1125, low_moving_in_envelope:1110 |
| center_double__majority_left_stance | 64 | 0 | 0.0000 | 0.0586 | 5.0198 | 4.9586 | 2.7300 | high_pitch_velocity_p95:64, high_lateral_velocity:28, low_mean_vx:5 |
| center_double__majority_right_stance | 64 | 33 | 51.5625 | 0.0605 | 3.3411 | 2.6167 | 3.1245 | high_lateral_velocity:20, low_moving_in_envelope:10, high_pitch_velocity_p95:9 |
| center_flight__majority_double | 3 | 0 | 0.0000 | -0.0908 | 5.2400 | 3.5715 | 5.2400 | low_mean_vx:3, low_moving_in_envelope:3, low_moving_single_in_envelope:3 |
| center_left_stance__majority_double | 94 | 1 | 1.0638 | 0.0579 | 5.0024 | 4.9303 | 2.1449 | high_pitch_velocity_p95:89, low_moving_in_envelope:22, low_moving_single_in_envelope:20 |
| center_left_stance__majority_left_stance | 388 | 0 | 0.0000 | 0.0600 | 5.1021 | 5.0757 | 2.6358 | high_pitch_velocity_p95:388, high_lateral_velocity:125, low_moving_in_envelope:26 |
| center_left_stance__majority_right_stance | 2 | 0 | 0.0000 | -0.0108 | 5.2400 | 5.2400 | 4.8974 | low_mean_vx:2, low_moving_in_envelope:2, high_pitch_velocity_p95:2 |
| center_right_stance__majority_double | 113 | 27 | 23.8938 | 0.0582 | 4.0739 | 2.3376 | 3.9295 | high_pitch_velocity_p95:76, low_mean_vx:27, low_moving_in_envelope:27 |
| center_right_stance__majority_left_stance | 5 | 0 | 0.0000 | 0.0320 | 5.0264 | 4.9194 | 3.9499 | low_moving_in_envelope:5, high_pitch_velocity_p95:5, high_lateral_velocity:3 |
| center_right_stance__majority_right_stance | 362 | 102 | 28.1768 | 0.0693 | 3.6390 | 1.9382 | 3.6082 | high_pitch_velocity_p95:188, high_lateral_velocity:100, low_moving_in_envelope:13 |

## Left-Stance Examples

| source | ticks | bucket | reasons | vx | pitch_p95 | right_knee_p95 | left_knee_p95 |
|---|---:|---|---|---:|---:|---:|---:|
| published_policy_command_straight_x004_seed1 | 0-9 | reject_high_rate_moving | low_moving_in_envelope, high_pitch_velocity_p95, high_lateral_velocity | 0.0429 | 5.2400 | 4.4233 | 5.2400 |
| published_policy_command_straight_x004_seed1 | 2-11 | reject_high_rate_moving | low_moving_in_envelope, high_pitch_velocity_p95, high_lateral_velocity | 0.0593 | 4.8083 | 4.5609 | 4.8083 |
| published_policy_command_straight_x004_seed1 | 4-13 | reject_high_rate_moving | low_moving_in_envelope, high_pitch_velocity_p95 | 0.0490 | 4.8083 | 4.5609 | 4.8083 |
| published_policy_command_straight_x004_seed1 | 6-15 | reject_low_progress | low_mean_vx, low_moving_in_envelope, high_pitch_velocity_p95 | 0.0221 | 4.8083 | 4.1205 | 4.8083 |
| published_policy_command_straight_x004_seed2 | 0-9 | reject_high_rate_moving | high_pitch_velocity_p95 | 0.1226 | 5.1612 | 5.1612 | 2.2581 |
| published_policy_command_straight_x004_seed3 | 2-11 | reject_low_progress | low_mean_vx, low_moving_in_envelope, low_moving_single_in_envelope, high_pitch_velocity_p95 | -0.0605 | 5.2400 | 3.0374 | 5.2400 |
| published_policy_command_straight_x004_seed5 | 0-9 | reject_high_rate_moving | low_moving_in_envelope, low_moving_single_in_envelope, high_pitch_velocity_p95, high_lateral_velocity, low_base_height | 0.1092 | 5.2400 | 5.2400 | 4.1081 |
| published_policy_command_straight_x004_seed5 | 4-13 | reject_high_rate_moving | low_moving_in_envelope, low_moving_single_in_envelope, high_pitch_velocity_p95, high_lateral_velocity | 0.0465 | 5.2400 | 5.2400 | 5.2400 |
| published_policy_command_straight_x004_seed5 | 6-15 | reject_low_progress | low_mean_vx, low_moving_in_envelope, low_moving_single_in_envelope, high_pitch_velocity_p95 | -0.0014 | 5.2400 | 4.9744 | 5.2400 |
| published_policy_command_straight_x004_seed5 | 8-17 | reject_low_progress | low_mean_vx, low_moving_in_envelope, low_moving_single_in_envelope, high_pitch_velocity_p95 | -0.0316 | 5.2400 | 4.6121 | 5.2400 |
| published_policy_command_straight_x004_seed5 | 10-19 | reject_low_progress | low_mean_vx, low_moving_in_envelope, low_moving_single_in_envelope, high_pitch_velocity_p95 | -0.0339 | 5.2400 | 3.5907 | 5.0151 |
| published_policy_command_straight_x004_seed5 | 20-29 | reject_high_rate_moving | low_moving_in_envelope, high_pitch_velocity_p95 | 0.0423 | 4.9683 | 4.9683 | 2.2441 |
| published_policy_command_straight_x008_seed0 | 18-27 | reject_high_rate_moving | high_pitch_velocity_p95 | 0.0870 | 5.2400 | 5.2400 | 1.8810 |
| published_policy_command_straight_x008_seed0 | 20-29 | reject_high_rate_moving | high_pitch_velocity_p95 | 0.0757 | 5.2400 | 5.2400 | 2.2883 |
| published_policy_command_straight_x008_seed0 | 22-31 | reject_high_rate_moving | high_pitch_velocity_p95 | 0.0647 | 5.2400 | 5.2400 | 2.2883 |
| published_policy_command_straight_x008_seed0 | 24-33 | reject_high_rate_moving | high_pitch_velocity_p95 | 0.0581 | 4.9943 | 4.9943 | 2.2883 |
| published_policy_command_straight_x008_seed0 | 46-55 | reject_high_rate_moving | high_pitch_velocity_p95 | 0.0655 | 5.2400 | 5.2400 | 2.0660 |
| published_policy_command_straight_x008_seed0 | 48-57 | reject_high_rate_moving | high_pitch_velocity_p95 | 0.0649 | 5.2400 | 5.2400 | 2.2688 |
| published_policy_command_straight_x008_seed0 | 50-59 | reject_high_rate_moving | high_pitch_velocity_p95 | 0.0623 | 4.9848 | 4.9848 | 2.2688 |
| published_policy_command_straight_x008_seed0 | 52-61 | reject_high_rate_moving | high_pitch_velocity_p95 | 0.0635 | 4.9848 | 4.9848 | 2.2688 |

## Interpretation

- If left stance is absent, the selector source must be mirrored/recovered from another source before training.
- If left stance exists but is unsafe, the next branch should target the specific failing reason instead of training from the one-sided source.
