# Winner-v18 IMU ankle-feedback diagnostic preregistration

- Status: `PREREGISTERED_WINNER_V18_IMU_ANKLE_FEEDBACK_DIAGNOSTIC`
- Decision: `AUTHORIZE_ONE_CPU_ONLY_ONE_SIDED_IMU_ANKLE_FEEDBACK_DIAGNOSTIC`
- Inputs: deployable `obs[1]` gyro-y and `obs[3:6]` accelerometer
- Maximum ankle offset: `0.03 rad`
- Population: `168` CPU-only cells
- Optimizer / locomotion / robot: `0 / 0 / 0`

The screen compares baseline, the closed constant ankle offset, one-sided
tilt/rate feedback and their opposite-sign controls, plus combined backward
feedback. Only a full two-checkpoint pass advances.
