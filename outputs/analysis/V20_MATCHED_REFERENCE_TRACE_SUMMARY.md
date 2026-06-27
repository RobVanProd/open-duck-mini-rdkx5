# V20 Matched Reference Trace Summary

status: `HOLD_V20_MATCHED_REFERENCE_NO_LOCK`

## Aggregate

- runs: `8`
- falls: `8`
- duration_complete: `0`
- vx_mean: `-0.0539`
- track_ratio_mean: `-1.3468`
- samples_mean: `68.6250`
- samples_min: `33`
- samples_max: `152`
- vy_p95_abs_mean: `0.3793`
- body_pitch_p95_mean: `0.0462`
- base_height_min_mean: `0.1266`

## Per Seed

| seed | samples | vx_mean | track_ratio | vy_p95_abs | base_height_min | body_pitch_p95 | contact_transitions | imitation_mean60 | shortfall_mean60 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 70 | 0.0014 | 0.0341 | 0.1081 | 0.1536 | 0.0759 | 3 | -0.4935 | 30.3624 |
| 1 | 34 | -0.0913 | -2.2813 | 1.0815 | 0.0916 | 0.0070 | 3 | -7.0457 | 502.8247 |
| 2 | 70 | 0.0077 | 0.1926 | 0.1296 | 0.1526 | 0.0319 | 3 | 0.2170 | 14.0770 |
| 3 | 70 | -0.0157 | -0.3930 | 0.1326 | 0.1579 | 0.0822 | 3 | -1.2927 | 76.8199 |
| 4 | 152 | 0.0080 | 0.1992 | 0.0381 | 0.1513 | 0.0421 | 1 | 0.6786 | 12.1243 |
| 5 | 50 | -0.3133 | -7.8315 | 0.2133 | 0.0506 | 0.0614 | 9 | -3.2490 | 8377.4548 |
| 6 | 70 | -0.0143 | -0.3563 | 0.2642 | 0.1588 | 0.0296 | 5 | -1.2556 | 86.4929 |
| 7 | 33 | -0.0135 | -0.3385 | 1.0669 | 0.0961 | 0.0393 | 3 | -8.3432 | 80.6862 |

## Interpretation

- V20 used the command-matched x=0.04 reference override and vanilla dynamics.
- It still failed every seed before the 5 s duration.
- The dominant gate failure is low/reverse forward progress, not actuator-envelope violation.
- Lateral motion is present and should stay tracked, but the seed distribution is not explained by a pure lateral-sway fall.
- This supports debugging the imitation/reference-locking mechanism rather than launching another reward-weight variant.
