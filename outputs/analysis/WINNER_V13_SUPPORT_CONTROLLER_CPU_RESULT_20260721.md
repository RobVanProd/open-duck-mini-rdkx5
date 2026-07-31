# Winner-v13 support-controller CPU result

- Status: `PASS_WINNER_V13_SUPPORT_CONTROLLER_CPU_CONTRACT`
- Decision: `AUTHORIZE_SUPPORT_CONTROLLER_TRAINING_PREREGISTRATION_ONLY`
- GitHub run / artifact: `29824703022` / `8492842757`
- Artifact ZIP SHA-256: `27968d3dba7f316cf6eaf03c625dc808d030d080e2ac7a555bf549cc8bbaaa59`
- Stage-1 snapshot SHA-256: `8c1392c738eddfb098e61c1a6ae2f863eda883e1eba6ac546aef695da6f163af`
- Sampled / valid transitions: `18251 / 18243`
- JAX/ONNX maximum absolute error: `1.4551915228366852e-11`
- One-update graph / snapshot SHA-256: `2d4103cd3672dfbf065ecb5c0cc25052c369d83ef36ddb139bff76f509ae9420 / 567b1f3e6499d5e29dad50d5ccc47e7e91e906c93465d31cf080ae464347190a`
- Stage-1 tree frozen: `bit exact`
- Stage-2 leaves: `all nonzero-gradient and all changed`
- Formal support / locomotion / robot access: `0 / 0 / 0`

This pass authorizes only a separate support-controller training preregistration.
It does not authorize training execution, formal support evaluation, locomotion, or robot access.
