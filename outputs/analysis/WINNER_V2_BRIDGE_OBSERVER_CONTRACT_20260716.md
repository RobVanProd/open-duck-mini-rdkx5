# Winner v2 Bridge-Observer Contract

Status: `PASS_WINNER_V2_BRIDGE_OBSERVER_CONTRACT`

Decision: `PIN_EXTERNAL_FITTED_BRIDGE_OBSERVER_FOR_OBS83_97`

- Frozen traces: 16/16
- Frozen rows: 9600/9600
- Maximum inverse-home roundoff versus configured home: 3.72529029846e-09 rad
- Maximum applied-target reconstruction error: 0 rad

The winner ONNX interface carries only the 115-D observation and a 14-D bounded-action state. It does not carry the per-joint delay queues and lag state. Therefore obs[83:97] is an external host responsibility. On pass, the v2 contract pins the existing fitted bridge forward observer to that slot, initialized at home and advanced once after each sent target.

This does not integrate the runtime, choose a hardware fit, authorize Gate 5, or clear the robot.
