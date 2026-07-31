# Corrected Bridge Teacher Window Analysis

status: `HOLD_NO_CORRECTED_IN_ENVELOPE_WINDOWS`

This is offline sim analysis only. It does not SSH, deploy, train, or touch robot hardware.

## Corrected Velocity Limits

| joint | limit_rad_s |
|---|---:|
| `left_hip_pitch` | 2.5000 |
| `left_knee` | 3.2500 |
| `left_ankle` | 2.7500 |
| `right_hip_pitch` | 2.2500 |
| `right_knee` | 2.7500 |
| `right_ankle` | 2.0000 |

## Summary

- windows: `1030`
- pass_windows: `1`
- pass_left_stance_windows: `0`
- pass_right_stance_windows: `0`
- reason_counts: `{'over_corrected_envelope': 1029, 'low_mean_vx': 172, 'low_moving_tick': 29, 'high_lateral_velocity': 19, 'high_body_pitch': 8, 'low_single_support': 4}`

## Contact Groups

| group | windows | pass | mean_vx | max_excess | single_support | top_reasons |
|---|---:|---:|---:|---:|---:|---|
| center_double_support__majority_double_support | 586 | 1 | 0.0373 | 1.9166 | 42.2184 | over_corrected_envelope:585, low_mean_vx:121, low_moving_tick:21, high_lateral_velocity:3, low_single_support:2 |
| center_double_support__majority_right_stance | 2 | 0 | 0.0010 | 2.5533 | 60.0000 | low_mean_vx:2, over_corrected_envelope:2, high_lateral_velocity:2, high_body_pitch:1 |
| center_flight__majority_double_support | 13 | 0 | 0.0420 | 1.8563 | 38.1538 | over_corrected_envelope:13, low_mean_vx:1 |
| center_left_stance__majority_double_support | 221 | 0 | 0.0431 | 2.1003 | 39.9095 | over_corrected_envelope:221, low_mean_vx:14, low_single_support:1, high_lateral_velocity:1 |
| center_left_stance__majority_right_stance | 2 | 0 | -0.1165 | 2.7010 | 96.0000 | low_mean_vx:2, low_moving_tick:2, over_corrected_envelope:2, high_lateral_velocity:2, high_body_pitch:2 |
| center_right_stance__majority_double_support | 199 | 0 | 0.0406 | 1.7266 | 40.2814 | over_corrected_envelope:199, low_mean_vx:27, high_lateral_velocity:4, low_moving_tick:3, low_single_support:1 |
| center_right_stance__majority_left_stance | 1 | 0 | 0.0360 | 2.9900 | 64.0000 | over_corrected_envelope:1, high_lateral_velocity:1 |
| center_right_stance__majority_right_stance | 6 | 0 | -0.1976 | 2.5731 | 82.0000 | over_corrected_envelope:6, high_lateral_velocity:6, low_mean_vx:5, high_body_pitch:5, low_moving_tick:3 |

## Top Passing Windows

| seed | ticks | center | majority | vx | single_% | left_% | right_% | max_excess |
|---:|---:|---|---|---:|---:|---:|---:|---:|
| 1 | 245-269 | double_support | double_support | 0.0462 | 48.0000 | 24.0000 | 24.0000 | 0.0000 |

## Interpretation

- `PASS_CORRECTED_WINDOWS_BALANCED` means corrected in-envelope snippets exist on both stance sides.
- `HOLD_CORRECTED_WINDOWS_ONE_SIDED` means the old one-sided selector problem remains under the corrected bridge.
- `HOLD_NO_CORRECTED_IN_ENVELOPE_WINDOWS` means the old teacher source is no longer usable under the corrected per-joint envelope.
