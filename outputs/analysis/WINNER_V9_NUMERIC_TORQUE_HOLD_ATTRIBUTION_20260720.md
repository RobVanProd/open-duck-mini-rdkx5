# Winner-v9 Numeric Torque Hold Attribution

Status: `PASS_WINNER_V9_HOLD_ATTRIBUTED_TO_FLOAT32_TORQUE_BOUNDARY`

Decision: `PREREGISTER_DISTINCT_WINNER_V10_INWARD_TORQUE_REPRESENTATION_CONTRACT_ONLY`

- frozen decimal torque gate: `1.91229675` Nm
- nearest float32 torque: `1.9122967720031738` Nm
- representational overage: `2.2003173727469516e-08` Nm
- one-step inward float32 torque: `1.9122966527938843` Nm
- inward XML decimal: `1.91229665` Nm
- moving cells at the represented boundary: `12/12`

All behavior, current, overcurrent-duration, measured-rate-vector, x=0, identity, and completeness checks passed. Winner-v9 remains closed. The distinct Winner-v10 hypothesis changes only the XML torque representation by one float32 step inward and first requires a zero-behavior contract. No training, runtime, robot access, torque, motion, Gate 5, deployment, or robot clearance is authorized.
