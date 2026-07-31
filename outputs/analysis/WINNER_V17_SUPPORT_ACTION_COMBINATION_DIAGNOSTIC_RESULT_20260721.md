# Winner-v17 support action-combination diagnostic result

- Status: `PASS_WINNER_V17_SUPPORT_ACTION_COMBINATION_DIAGNOSTIC`
- Decision: `NO_SIGN_CONSISTENT_COMBINATION_PASSES_CLOSE_CONSTANT_OFFSET_CLASS`
- GitHub run / artifact: `29848345372` / `8502313017`
- Artifact ZIP SHA-256: `1aea84365f2198ca00b19e8a7ed2c08088f317f5407cb366da6042d6bd1ca57f`
- Raw result SHA-256: `3207c32c67ddc5e592e23c2b12c5e7823dda40f5105798b4b5f1e9ad52fc8e11`
- Full pass candidates: `0`
- Positive ankle failures half / final: `8 / 6`
- Knee+ankle failures half / final: `8 / 7`
- Optimizer / robot access: `0 / 0`

No constant subset passes both checkpoints. Adding knee does not improve
the positive-ankle persistence result, and any hip-containing combination
fails every cell. The constant-offset mechanism class is closed.
