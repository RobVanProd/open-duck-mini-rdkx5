# Winner-v24 support-regression attribution

- Status: `PASS_WINNER_V24_SUPPORT_REGRESSION_ATTRIBUTION`
- Decision: `AUTHORIZE_DIRECTIONAL_SUPPORT_CONTROL_DIAGNOSTIC_PREREGISTRATION_ONLY`
- Winner-v22 half/final failures: `15 / 14`
- Winner-v24 half/final failures: `20 / 20`
- Recovered failures: `0 / 0`
- Added failures: `5 / 6`
- Shared-failure onset delta median: `-3 / -3 ticks`
- New simulation / optimizer / locomotion / robot: `0 / 0 / 0 / 0`

Winner-v24 preserved response encoding/use and every nonphysical gate, but the symmetric terminal penalty recovered zero Winner-v22 failures, added failures at both checkpoints, and moved every shared failure earlier. Observability is not the remaining blocker; the scalar terminal objective changed support control in the wrong direction. The next evidence question must test the direction of the actor's same-state action change against short-horizon physical pitch response before any new loss or architecture is selected.
