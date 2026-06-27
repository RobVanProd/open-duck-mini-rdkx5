# Published Policy Command Grid

overall_status: `HOLD_NO_MOVING_COMMAND_FOUND`

## Scope

- Offline closed-loop sim eval only.
- Same published `BEST_WALK_ONNX_2` policy.
- Vanilla sim path; no fitted actuator bridge, no training, no robot access.
- Gate searches for forward tracking while each seed stays under the measured per-joint pitch-chain velocity envelope.

## Command Cells

| command_cell | x | y | yaw | seeds | complete | moving | mean_vx | track_ratio | max_pitch_vel_p95_mean | max_pitch_vel_p95_max_seed | gate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| straight_x008 | 0.0800 | 0.0000 | 0.0000 | 1 | 1 | 0 | 0.0303 | 0.3794 | 5.2400 | 5.2400 | `HOLD_NO_FORWARD_MOTION_OR_OVER_ENVELOPE` |

## Interpretation

No command cell in this grid produced reliable forward movement. Expand or revise the grid only after reviewing whether the command region is meaningful.

Robot validation remains blocked.

