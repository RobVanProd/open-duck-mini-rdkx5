# Winner-v7 Full Measured-Vector Attribution

Status: `HOLD_WINNER_V7_FULL_MEASURED_VECTOR_ATTRIBUTION`

Decision: `CLOSE_FULL_MEASURED_VECTOR_CAUSAL_ROUTE`

- graph vector: `[5.24, 5.24, 1.5, 1.5, 1.5, 5.24, 5.24, 5.24, 5.24, 5.24, 5.24, 1.25, 1.0, 1.25]` rad/s
- full measured conservative vector: `[1.0, 0.75, 1.5, 1.5, 1.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.75, 1.25, 1.0, 1.25]` rad/s
- relaxed graph joints: `['left_hip_yaw', 'left_hip_roll', 'neck_pitch', 'head_pitch', 'head_yaw', 'head_roll', 'right_hip_yaw', 'right_hip_roll']`
- moving traces with full-vector excess: `96/96`
- protection failure events: `888`
- failure events within `6` ticks of a same-joint measured-vector violation: `681/888`

This is a read-only causal audit. Winner-v7 remains closed; no graph transform, behavior run, training, runtime, deployment, robot access, torque, motion, or Gate 5 is authorized by the result itself.
