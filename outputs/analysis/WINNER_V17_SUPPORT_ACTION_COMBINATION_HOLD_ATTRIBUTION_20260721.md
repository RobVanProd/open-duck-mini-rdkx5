# Winner-v17 support action-combination hold attribution

- Status: `PASS_WINNER_V17_SUPPORT_ACTION_COMBINATION_HOLD_ATTRIBUTION`
- Decision: `CLOSE_FIXED_003_RAD_OFFSET_SUBSET_PREREGISTER_ONE_SIDED_IMU_ANKLE_FEEDBACK_DIAGNOSTIC`
- Fixed-offset full passes: `0 / 7`
- Optimizer / robot access: `0 / 0`

All fixed `0.03 rad` subsets are closed. Positive ankle alone reduces
failures to `8/6`; adding knee yields `8/7`, and every hip-containing
combination returns to `12/12`.

The next diagnostic keeps the evidence-selected ankle direction but makes
its magnitude one-sided and state-dependent using only deployable gyro-y
and accelerometer-x observations. It performs no training and grants no
robot authority.
