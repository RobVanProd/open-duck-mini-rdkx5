# Left-Stance Right-Knee Rate Recovery

status: `PASS_RIGHT_KNEE_RELABEL_RECOVERS_LEFT_STANCE`

This is an offline relabeling analysis of existing BEST_WALK windows. It does not step simulation, train, deploy, SSH, run robot tests, or change runtime behavior.

## Filters

- window_samples: `10`
- stride_samples: `2`
- envelope_high: `3.75`
- right_knee_cap: `3.61`
- min_recovery_pct: `20.0`

## Summary

- total_left_related_windows: `553`
- original_pass_windows: `1`
- relabeled_pass_windows: `343`
- relabeled_pass_pct: `62.0253`

## By Contact Group

| group | windows | original_pass | relabeled_pass | relabeled_pass_% | top remaining reasons |
|---|---:|---:|---:|---:|---|
| center_double__majority_left_stance | 64 | 0 | 31 | 48.4375 | high_lateral_velocity:28, low_mean_vx:5, low_moving_in_envelope:3 |
| center_left_stance__majority_double | 94 | 1 | 70 | 74.4681 | low_mean_vx:17, low_moving_in_envelope:17, low_moving_single_in_envelope:17 |
| center_left_stance__majority_left_stance | 388 | 0 | 242 | 62.3711 | high_lateral_velocity:125, high_pitch_velocity_p95:23, low_moving_in_envelope:14 |
| center_left_stance__majority_right_stance | 2 | 0 | 0 | 0.0000 | low_mean_vx:2, low_moving_in_envelope:2, high_pitch_velocity_p95:2 |
| center_right_stance__majority_left_stance | 5 | 0 | 0 | 0.0000 | low_moving_in_envelope:5, high_pitch_velocity_p95:5, high_lateral_velocity:3 |

## Interpretation

- A pass here means right-knee relabeling can create enough left-stance candidate windows to justify a selector/replay prototype.
- A hold means the left-stance problem is not solved by right-knee rate capping alone and needs a different source or dynamics-aware recovery.
