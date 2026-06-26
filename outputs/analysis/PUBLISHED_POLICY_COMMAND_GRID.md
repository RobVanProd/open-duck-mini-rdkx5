# Published Policy Command Grid

overall_status: `HOLD_MOVEMENT_REQUIRES_OVER_ENVELOPE`

## Scope

- Offline closed-loop sim eval only.
- Same published `BEST_WALK_ONNX_2` policy.
- Vanilla sim path; no fitted actuator bridge, no training, no robot access.
- Gate searches for forward tracking while each seed stays under the measured per-joint pitch-chain velocity envelope.

## Command Cells

| command_cell | x | y | yaw | seeds | complete | moving | mean_vx | track_ratio | max_pitch_vel_p95_mean | max_pitch_vel_p95_max_seed | gate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| straight_x005 | 0.0500 | 0.0000 | 0.0000 | 2 | 2 | 0 | 0.0033 | 0.0664 | 1.6989 | 2.7422 | `HOLD_INSIDE_ENVELOPE_NO_FORWARD_MOTION` |
| straight_x006 | 0.0600 | 0.0000 | 0.0000 | 2 | 2 | 0 | 0.0056 | 0.0935 | 2.2653 | 3.8816 | `HOLD_NO_FORWARD_MOTION_OR_OVER_ENVELOPE` |
| straight_x007 | 0.0700 | 0.0000 | 0.0000 | 2 | 2 | 0 | 0.0152 | 0.2171 | 3.5276 | 3.6654 | `HOLD_INSIDE_ENVELOPE_NO_FORWARD_MOTION` |
| turn_scale050 | 0.0370 | -0.0185 | -0.0370 | 2 | 2 | 0 | 0.0029 | 0.0789 | 0.9819 | 1.1501 | `HOLD_INSIDE_ENVELOPE_NO_FORWARD_MOTION` |
| turn_scale065 | 0.0481 | -0.0241 | -0.0481 | 2 | 2 | 0 | 0.0031 | 0.0643 | 1.5067 | 2.3012 | `HOLD_INSIDE_ENVELOPE_NO_FORWARD_MOTION` |
| turn_scale080 | 0.0592 | -0.0296 | -0.0592 | 2 | 2 | 0 | 0.0038 | 0.0641 | 1.8453 | 2.7692 | `HOLD_INSIDE_ENVELOPE_NO_FORWARD_MOTION` |
| turn_scale090 | 0.0666 | -0.0333 | -0.0666 | 2 | 2 | 0 | 0.0066 | 0.0995 | 2.4527 | 3.1335 | `HOLD_INSIDE_ENVELOPE_NO_FORWARD_MOTION` |
| turn_scale100 | 0.0740 | -0.0370 | -0.0740 | 2 | 2 | 2 | 0.0583 | 0.7874 | 4.9339 | 5.0147 | `WARN_MOVES_OVER_ENVELOPE` |

## Interpretation

In this grid, forward movement only appeared in cells whose per-seed pitch-chain target velocity exceeded the measured envelope. This supports treating published-policy movement as over-envelope for these commands.

Robot validation remains blocked.
