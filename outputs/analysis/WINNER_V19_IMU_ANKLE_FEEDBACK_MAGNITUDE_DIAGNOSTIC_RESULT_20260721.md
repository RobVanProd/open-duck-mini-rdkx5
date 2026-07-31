# Winner-v19 IMU ankle-feedback magnitude result

- Status: `PASS_WINNER_V19_IMU_ANKLE_FEEDBACK_MAGNITUDE_DIAGNOSTIC`
- Decision: `INSUFFICIENT_FEEDBACK_AUTHORITY_FALSIFIED_STOP_WITH_ATTRIBUTION`
- GitHub run / artifact: `29850348125` / `8503113171`
- Artifact ZIP SHA-256: `8634e251e4b73d13ff4fc8e01e87eac7cf905fafc1b918fa0f668b5492b76cd2`
- Raw result SHA-256: `d247e4b2ab788b17a9288bb6926115dd9f9854c322edaf8b096747b489bd7d71`
- Full pass candidates: `0`
- Constant failures 0.03 / 0.06 / 0.09: `8/6`, `12/12`, `12/12`
- Feedback failures 0.03 / 0.06 / 0.09: `10/10`, `10/8`, `10/8`
- Optimizer / robot access: `0 / 0`

More correction does not solve the support failure: larger constant offsets
regress to `12/12`, and larger feedback remains `10/8`. Insufficient
wrapper authority is falsified; the wrapper mechanism line is closed.
