# Winner-v22 support HOLD attribution

- Status: `PASS_WINNER_V22_SUPPORT_HOLD_ATTRIBUTION`
- Decision: `AUTHORIZE_NEGATIVE_X_RESPONSE_USE_DIAGNOSTIC_PREREGISTRATION_ONLY`
- Learned predictor versus constant: `4/4 pass`
- Physical support failures, half/final: `15/124`, `14/124`
- Failure mechanism: `roll_pitch` only
- Failed-domain sign: `negative torso COM X` in every failure
- v15 physical-support failures, half/final: `12/124`, `12/124`
- New simulation / optimization / robot: `0 / 0 / 0`
- Manual mass/COM measurements: `not required`

The normalization bug is fixed, but response prediction did not create
robust negative-X support control. A pass here authorizes only a separately
frozen read-only response-use diagnostic; it does not authorize training.
