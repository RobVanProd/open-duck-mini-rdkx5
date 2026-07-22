# Winner-v50c gradient backward-error attribution result

- Status: `PASS_WINNER_V50C_GRADIENT_BACKWARD_ERROR_ATTRIBUTION`
- Decision: `AUTHORIZE_FULL_ACTION_TEACHER_ONE_UPDATE_CPU_PREREGISTRATION_ONLY`
- Relative bound: `0.00034526698300124393`
- Old/new maximum relative error: `7.29267879396252e-7 / 7.51381898651892e-7`
- Old/new maximum RMS-relative error: `2.6416685503084517e-7 / 2.6547401864741865e-7`
- Optimizer updates / support cells / exports / robot access: `0 / 0 / 0 / 0`
- Result SHA-256: `ce3bbe554b9497b744f792e1e4b53986cc3c48efe582bff5ac23e6e51d2883d3`

Every old and new gradient leaf is within the preregistered
`sqrt(float32 epsilon)` maximum-relative and RMS-relative bounds, with no
material sign changes and bit-exact zero-reference leaves. The exact V50
absolute errors and all non-composition evidence reproduced.

V50 and V50b remain unchanged holds under their own metrics. This pass does not
authorize training; it authorizes only preregistration of one exact CPU
optimizer-update proof from the frozen Winner-v46 terminal state.
