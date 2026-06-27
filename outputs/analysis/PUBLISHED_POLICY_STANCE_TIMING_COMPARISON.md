# Published Policy Stance Timing Comparison

status: `PASS_STANCE_TIMING_COMPARISON_READY`

This is an offline analysis of existing BEST_WALK traces. It does not train, deploy, SSH, run robot tests, or change runtime behavior.

## Command Summary

| command_cell | traces | complete | mean_vx | track_ratio | single_% | double_% | alt | single_dvx_0p1s | single_push_% | stance_dx | stance_abs_dy | pitch_p95 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| straight_x004 | 8 | 8 | 0.0019 | 0.0468 | 3.6500 | 96.1000 | 1.5000 | -0.0155 | 40.5258 | -0.0013 | 0.0526 | 0.8647 |
| straight_x008 | 8 | 8 | 0.0640 | 0.7998 | 49.4000 | 50.3500 | 17.6250 | 0.0030 | 59.1070 | -0.0161 | 0.0478 | 3.2849 |
| turning_x0074_yneg0037_yawneg0074 | 8 | 8 | 0.0540 | 0.7294 | 44.8000 | 54.9500 | 16.2500 | 0.0042 | 56.2205 | -0.0144 | 0.0484 | 3.2396 |

## Interpretation

- `single_dvx_0p1s` is the average local-forward velocity change 5 ticks after a single-support tick.
- `stance_dx` and `stance_abs_dy` use base x/y minus the active stance foot site x/y during single support.
- Compare straight `x=0.04` with the moving command cells before treating x=0.04 as a walking existence gate.
- Positive single-support propulsion with high pitch p95 means the mechanism exists, but may still exceed the measured actuator envelope.
