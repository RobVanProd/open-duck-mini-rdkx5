# Winner-v24 baseline-anchored training preregistration

- Status: `PREREGISTERED_WINNER_V24_BASELINE_ANCHORED_TRAINING`
- Decision: `AUTHORIZE_ONE_100_UPDATE_BASELINE_ANCHORED_ARM_ONLY`
- Source / final optimizer count: `100 / 200`
- Continuation updates / checkpoints: `100 / 150,200`
- New terminal failure reward: `-250`
- Coefficient / length / predictor-scale searches: `0 / 0 / 0`
- Formal support / locomotion / robot: `0 / 0 / 0`
- Flat-transport equation: `not used`
- Manual mass/COM measurements: `not required`

This workflow trains one fixed offline arm and exports half/final evidence.
It does not evaluate support, select a checkpoint, or access the robot.
