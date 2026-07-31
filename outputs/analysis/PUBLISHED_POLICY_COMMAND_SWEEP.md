# Published Policy Command Sweep

overall_status: `WARN_COMMAND_SPECIFIC_PROPULSION_OVER_ENVELOPE`

## Executive Summary

- Same published `BEST_WALK_ONNX_2` policy, upstream-main `flat_terrain_backlash`, vanilla dynamics.
- Three command cells were evaluated with full observation and foot-site traces.
- The upstream turning command and straight `x=0.08` produce forward tracking.
- Straight `x=0.04` completes without falling but does not meaningfully move forward.
- This means the old straight `x=0.04` gate is not cleared by the published policy either.

## Command Curve

| command_cell | traces | complete | moving>=0.5 | mean_vx | track_ratio | single_% | single_dvx_0p1s | target_vel_p95_mean | target_vel_p95_max_joint | pitch_p95 | height_min |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| straight_x004 | 8 | 8 | 0 | 0.0019 | 0.0468 | 3.6500 | -0.0155 | 0.8225 | 1.2742 | 0.0394 | 0.1520 |
| straight_x008 | 8 | 8 | 7 | 0.0640 | 0.7998 | 49.4000 | 0.0030 | 3.2246 | 5.1546 | 0.0646 | 0.1523 |
| turning_x0074_yneg0037_yawneg0074 | 8 | 8 | 7 | 0.0540 | 0.7294 | 44.8000 | 0.0042 | 3.0488 | 4.6157 | 0.0650 | 0.1523 |

## Stance Geometry

| command_cell | base_minus_stance_x | base_minus_stance_abs_y | positive_push_x | positive_push_abs_y |
|---|---:|---:|---:|---:|
| straight_x004 | -0.0013 | 0.0526 | -0.0160 | 0.0545 |
| straight_x008 | -0.0161 | 0.0478 | -0.0210 | 0.0491 |
| turning_x0074_yneg0037_yawneg0074 | -0.0144 | 0.0484 | -0.0173 | 0.0487 |

## Interpretation

The existence proof is command-specific and actuator-envelope-limited. The published policy walks in vanilla sim at the upstream turning command and at straight `x=0.08`, but not at straight `x=0.04`. The moving command cells still have at least one pitch-chain joint with p95 target velocity above the measured 3.75 rad/s envelope, so this is not a real-robot-ready gait. The straight low-speed gate should not be treated as an easy baseline or as an existence-proven target.

Robot validation remains blocked.
