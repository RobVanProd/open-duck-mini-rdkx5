# Local Velocity Gate Recheck

generated_at: `2026-06-22T22:20Z`

## Reason

The closed-loop candidate gate previously measured nonzero-command forward
progress from world-frame `base_x` displacement. The Open Duck Playground reset
randomizes yaw, while the reward function tracks local base-frame forward
velocity. This made the gate vulnerable to reporting the wrong progress sign.

The evaluator now records `env.get_local_linvel(...)` every tick and uses local
base-x velocity for:

- `mean_velocity_x_m_s`
- `command_tracking_ratio`
- `velocity_error_m_s`

World-frame `base_x` progress remains in JSON as a diagnostic.

## Recheck Results

| policy | command | status | mean local vx, fitted | track ratio, fitted | note |
|---|---:|---|---:|---:|---|
| `BEST_WALK_ONNX_2` | `0.08` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | `0.0174` | `0.2175` | baseline moves forward in local frame but fails actuator-bridge/stress gates |
| balanced probe `153600` | `0.00` | `PASS_CANDIDATE_SIM_GATE` | `0.0007` | `NA` | zero-command gate passes |
| balanced probe `153600` | `0.08` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | `0.0006` | `0.0080` | too stationary |
| movement probe `153600` | `0.00` | `PASS_CANDIDATE_SIM_GATE` | `0.0003` | `NA` | zero-command gate passes |
| movement probe `153600` | `0.08` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | `0.0005` | `0.0059` | still too stationary |

## Interpretation

The previous forward-progress sign issue was real, but it does not rescue the
new training probes. The baseline policy produces meaningful local forward
velocity in vanilla sim, then degrades under the fitted/stress actuator bridge.
The new short actuator-bridge probes are stable at zero command but do not yet
learn forward motion.

Do not deploy any candidate from this recheck. Robot motion remains blocked.
