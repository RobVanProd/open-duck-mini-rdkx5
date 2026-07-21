# Winner-v15 pitch-margin support HOLD attribution

- Status: `PASS_WINNER_V15_PITCH_MARGIN_SUPPORT_HOLD_ATTRIBUTION`
- Decision: `CLOSE_PITCH_MARGIN_OBJECTIVE_PREREGISTER_ACTION_DIRECTION_DIAGNOSTIC`
- Half/final physical failures: `12 / 12`
- Sensor/transport failures: `0`
- New training / behavior / robot access: `0 / 0 / 0`

Both checkpoints remain held by 12 early backward-pitch exits in six negative-X configurations.
All six configurations persist from the Winner-v13 failure set at both checkpoints.
The exact dense pitch-margin signal therefore did not solve the mechanism, and the objective is closed without a scale or duration search.

The legacy predictor score repeats the already-attributed normalized-vs-raw reporting defect.
That score is not gate-setting here because the physical support failures independently hold both checkpoints.

The next authorized step is a preregistered CPU-only action-direction diagnostic on the fixed persistent core.
The flat-transport kernel remains unselected because contexts separate and failures occur by ticks 28-62.
