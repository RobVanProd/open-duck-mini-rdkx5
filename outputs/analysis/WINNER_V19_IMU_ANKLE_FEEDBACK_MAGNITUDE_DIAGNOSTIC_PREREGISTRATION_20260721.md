# Winner-v19 IMU ankle-feedback magnitude preregistration

- Status: `PREREGISTERED_WINNER_V19_IMU_ANKLE_FEEDBACK_MAGNITUDE_DIAGNOSTIC`
- Decision: `AUTHORIZE_ONE_CPU_ONLY_FEEDBACK_MAGNITUDE_FEASIBILITY_SCREEN`
- Only variable: maximum target offset `0.03 / 0.06 / 0.09 rad`
- Population: `168` CPU-only cells
- Optimizer / locomotion / robot: `0 / 0 / 0`

The 3x ceiling is derived from Winner-v18's `0.313` combined mean
activation; 2x is the frozen bridge. The feedback law, policy, checkpoints,
population, bounds, and full-pass-only rule remain unchanged.
