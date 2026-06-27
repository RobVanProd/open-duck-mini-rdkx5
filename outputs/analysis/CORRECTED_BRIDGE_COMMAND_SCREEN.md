# Published Policy Command Grid

overall_status: `HOLD_MOVEMENT_REQUIRES_OVER_ENVELOPE`

## Scope

- Offline closed-loop sim eval only.
- Same published `BEST_WALK_ONNX_2` policy.
- Bridge mode: `fitted`; no training, no robot access.
- Gate searches for forward tracking while each seed stays under the measured per-joint pitch-chain velocity envelope.

## Command Cells

| command_cell | x | y | yaw | seeds | complete | moving | mean_vx | track_ratio | max_pitch_vel_p95_mean | max_pitch_vel_excess_max | gate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| straight_x002 | 0.0200 | 0.0000 | 0.0000 | 2 | 2 | 0 | 0.0006 | 0.0283 | 1.8078 | 0.0000 | `HOLD_INSIDE_ENVELOPE_NO_FORWARD_MOTION` |
| straight_x004 | 0.0400 | 0.0000 | 0.0000 | 2 | 2 | 0 | 0.0020 | 0.0499 | 2.0264 | 0.0651 | `HOLD_NO_FORWARD_MOTION_OR_OVER_ENVELOPE` |
| straight_x006 | 0.0600 | 0.0000 | 0.0000 | 2 | 2 | 0 | 0.0031 | 0.0515 | 2.6940 | 1.2289 | `HOLD_NO_FORWARD_MOTION_OR_OVER_ENVELOPE` |
| straight_x008 | 0.0800 | 0.0000 | 0.0000 | 2 | 2 | 2 | 0.0340 | 0.4250 | 4.9825 | 2.4362 | `WARN_MOVES_OVER_ENVELOPE` |
| turn_scale050 | 0.0370 | -0.0185 | -0.0370 | 2 | 2 | 0 | 0.0012 | 0.0337 | 1.8575 | 0.1204 | `HOLD_NO_FORWARD_MOTION_OR_OVER_ENVELOPE` |
| turn_scale075 | 0.0555 | -0.0278 | -0.0555 | 2 | 2 | 0 | 0.0046 | 0.0829 | 2.5577 | 1.0259 | `HOLD_NO_FORWARD_MOTION_OR_OVER_ENVELOPE` |
| turn_scale100 | 0.0740 | -0.0370 | -0.0740 | 2 | 2 | 2 | 0.0366 | 0.4941 | 5.1119 | 2.4900 | `WARN_MOVES_OVER_ENVELOPE` |

## Interpretation

In this grid, forward movement only appeared in cells whose per-seed pitch-chain target velocity exceeded the measured envelope. This supports treating published-policy movement as over-envelope for these commands.

Robot validation remains blocked.

